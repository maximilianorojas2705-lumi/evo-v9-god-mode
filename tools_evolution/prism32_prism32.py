#!/usr/bin/env python3
"""
Prism32 v7.1.0 - MegaDyne Systems Terminal Agent
Green phosphor vibes. Pure terminal energy.
"""
import urllib.request
import urllib.error
import urllib.parse
try:
    import ssl
except ImportError:  # Some minimal/embedded builds lack ssl
    ssl = None
import json
import sys
import os
import subprocess
import time
import socket
import shutil
import re
import shlex
import signal
import argparse
import textwrap
import difflib
from datetime import datetime
import platform
import atexit
import math
import base64
import threading
stdout_lock = threading.RLock()
import queue
import hashlib
import importlib.util
import py_compile
try:
    import pty
except ImportError:
    pty = None
try:
    import select
except ImportError:
    select = None
try:
    import readline
except ImportError:
    pass

# ── Low-RAM Detection ───────────────────────────────────────
_LOW_RAM = False
try:
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemTotal:'):
                total_kb = int(line.split()[1])
                _LOW_RAM = total_kb < 65536  # < 64MB
                break
except Exception:
    pass

_CMD_RESULT_CAP = 500 if _LOW_RAM else 1500

# ── Plugin & Extension System ──────────────────────────────

class Command:
    """A registered command with metadata."""
    def __init__(self, name, handler, *, aliases=None, description="", category="", hidden=False):
        self.name = name
        self.handler = handler
        self.aliases = list(aliases) if aliases else []
        self.description = description
        self.category = category
        self.hidden = hidden

    def all_names(self):
        return [self.name] + self.aliases

class CommandRegistry:
    """Registry of commands (built-in + plugins)."""
    def __init__(self):
        self._cmds = {}

    def register(self, name, handler=None, **kwargs):
        if handler is None:
            return lambda h: self.register(name, h, **kwargs)
        cmd = Command(name, handler, **kwargs) if not isinstance(handler, Command) else handler
        self._cmds[cmd.name] = cmd
        for alias in cmd.aliases:
            self._cmds[alias] = cmd
        return cmd

    def get(self, name):
        return self._cmds.get(name)

    def all(self):
        seen = set()
        for cmd in self._cmds.values():
            if id(cmd) not in seen:
                seen.add(id(cmd))
                yield cmd

    def names(self):
        return {cmd.name for cmd in self.all()} | {a for cmd in self.all() for a in cmd.aliases}

    def dispatch(self, name, args_str, history, cmd_log):
        cmd = self.get(name)
        if cmd:
            cmd.handler(args_str, history, cmd_log)
            return True
        return False

    def dispatch_capture(self, name, args_str):
        """Dispatch a command and return its output as a string (for AI use)."""
        import io
        cmd = self.get(name)
        if not cmd:
            return None
        old_stdout = sys.stdout
        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd.handler(args_str, [], [])
            result = captured.getvalue()
        finally:
            sys.stdout = old_stdout
        return result

registry = CommandRegistry()

# ── Provider Registry (extensible) ─────────────────────────
PROVIDER_REGISTRY = {}

def register_provider(provider_id, **config):
    PROVIDER_REGISTRY[provider_id] = dict(config)
    return config

# ── Theme Registry (extensible) ─────────────────────────────
THEME_REGISTRY = {}

def register_theme(name, **colors):
    THEME_REGISTRY[name] = dict(colors)
    return colors

# ── Home Directory Resolution ───────────────────────────────
def _resolve_prism32_home():
    """Resolve the ~/.prism32 base directory, falling back to /tmp/prism32
    if home is missing or unwritable (e.g. Synology DSM missing homes dir)."""
    home = os.path.expanduser("~")
    base = os.path.join(home, ".prism32")
    try:
        os.makedirs(base, exist_ok=True)
        test_file = os.path.join(base, ".write_test")
        with open(test_file, 'w') as f:
            f.write("ok")
        os.remove(test_file)
        return base
    except (OSError, PermissionError, FileNotFoundError):
        fallback = os.path.join("/tmp", "prism32")
        try:
            os.makedirs(fallback, exist_ok=True)
        except OSError:
            pass
        return fallback

_PRISM32_HOME = _resolve_prism32_home()

# ── Plugin Loader ──────────────────────────────────────────
PLUGIN_DIR = os.path.join(_PRISM32_HOME, "plugins")
_PLUGINS = {}


class PluginAPI:
    """API object passed to plugins for accessing agent internals."""
    def __init__(self, plugin_name):
        self.name = plugin_name
        self._timers = []
        self._running = True
        self.registry = registry
        self.register_provider = register_provider
        self.register_theme = register_theme
        self.plugins = _PLUGINS

    @property
    def config(self):
        return Config

    @property
    def memory(self):
        return get_mem_cache()

    @property
    def history(self):
        return _PluginHooks._history if hasattr(_PluginHooks, '_history') else []

    def inject_context(self, text):
        """Add text to the AI system prompt context."""
        _PluginHooks._extra_context.append(text)

    def schedule(self, interval_sec, callback):
        """Schedule a callback to run every interval_sec seconds."""
        self._scheduled_interval = interval_sec
        for old_t in self._timers:
            old_t.cancel()
        t = threading.Timer(interval_sec, self._run_scheduled, [callback])
        t.daemon = True
        self._timers = [t]
        t.start()
        return t

    def _run_scheduled(self, callback):
        if not self._running:
            return
        try:
            callback(self)
        except Exception as e:
            with stdout_lock:
                print(f"  [plugin:{self.name}] timer error: {e}")
        if self._running:
            interval = getattr(self, '_scheduled_interval', 60)
            t = threading.Timer(interval, self._run_scheduled, [callback])
            t.daemon = True
            self._timers = [t]
            t.start()

    def http_get(self, url, headers=None, timeout=10):
        import urllib.request
        h = dict(PRISM32_DEFAULT_HEADERS)
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, headers=h)
        try:
            with urlopen_with_ssl(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception as e:
            return f"Error: {e}"

    def http_post(self, url, data=None, headers=None, timeout=10):
        import urllib.request
        import json as _j
        if isinstance(data, dict):
            data_bytes = _j.dumps(data).encode()
        elif isinstance(data, str):
            data_bytes = data.encode()
        elif isinstance(data, (bytes, bytearray)):
            data_bytes = bytes(data)
        else:
            data_bytes = _j.dumps(data).encode() if data is not None else b""
        h = {"Content-Type": "application/json"}
        h.update(PRISM32_DEFAULT_HEADERS)
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, data=data_bytes, headers=h, method='POST')
        try:
            with urlopen_with_ssl(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception as e:
            return f"Error: {e}"

    def log(self, msg):
        with stdout_lock:
            print(f"  [plugin:{self.name}] {msg}")
            sys.stdout.flush()

    def stop(self):
        self._running = False
        for t in self._timers:
            t.cancel()


class _PluginHooks:
    """Internal hook dispatcher. Plugins define methods, we call them."""
    _extra_context = []
    _history = []
    _boot_callbacks = []
    _message_callbacks = []
    _response_callbacks = []
    _command_callbacks = []
    _shutdown_callbacks = []
    _tick_callbacks = []
    _tick_thread = None

    @classmethod
    def register_plugin(cls, mod, api):
        if hasattr(mod, 'on_boot'):
            cls._boot_callbacks.append((mod.on_boot, api))
        if hasattr(mod, 'on_message'):
            cls._message_callbacks.append((mod.on_message, api))
        if hasattr(mod, 'on_response'):
            cls._response_callbacks.append((mod.on_response, api))
        if hasattr(mod, 'on_command'):
            cls._command_callbacks.append((mod.on_command, api))
        if hasattr(mod, 'on_shutdown'):
            cls._shutdown_callbacks.append((mod.on_shutdown, api))
        if hasattr(mod, 'on_tick'):
            cls._tick_callbacks.append((mod.on_tick, api))

    @classmethod
    def fire_boot(cls):
        for cb, api in cls._boot_callbacks:
            try:
                cb(api)
            except Exception as e:
                with stdout_lock:
                    print(f"  [plugin] on_boot error: {e}")

    @classmethod
    def fire_message(cls, user_input):
        for cb, api in cls._message_callbacks:
            try:
                cb(api, user_input)
            except Exception as e:
                with stdout_lock:
                    print(f"  [plugin] on_message error: {e}")

    @classmethod
    def fire_response(cls, response):
        for cb, api in cls._response_callbacks:
            try:
                cb(api, response)
            except Exception as e:
                with stdout_lock:
                    print(f"  [plugin] on_response error: {e}")

    @classmethod
    def fire_command(cls, cmd_name, args, result):
        for cb, api in cls._command_callbacks:
            try:
                cb(api, cmd_name, args, result)
            except Exception as e:
                with stdout_lock:
                    print(f"  [plugin] on_command error: {e}")

    @classmethod
    def fire_shutdown(cls):
        for cb, api in cls._shutdown_callbacks:
            try:
                cb(api)
            except Exception:
                pass
        for api_name in list(_PLUGINS.keys()):
            api = _plugin_apis.get(api_name)
            if api and hasattr(api, 'stop'):
                try:
                    api.stop()
                except Exception:
                    pass

    @classmethod
    def start_tick(cls, interval=5):
        if not cls._tick_callbacks:
            return
        def _tick_loop():
            while not _shutdown_flag:
                time.sleep(interval)
                for cb, api in cls._tick_callbacks:
                    try:
                        cb(api)
                    except Exception:
                        pass
        cls._tick_thread = threading.Thread(target=_tick_loop, daemon=True)
        cls._tick_thread.start()

_plugin_apis = {}
_PluginAPI_placeholder = object()

def _load_plugin_file(mod_path, mod_name=None, quiet=False):
    """Load one plugin file and register its commands/hooks."""
    mod_name = mod_name or os.path.splitext(os.path.basename(mod_path))[0]
    if mod_name in _PLUGINS:
        return True, f"Already loaded: {mod_name}"
    try:
        py_compile.compile(mod_path, doraise=True)
    except py_compile.PyCompileError as e:
        msg = f"Syntax error in plugin file {mod_path}: {e}"
        if not quiet:
            print(f"  [plugin] {msg}")
        return False, msg
    try:
        spec = importlib.util.spec_from_file_location(mod_name, mod_path)
        if not spec or not spec.loader:
            return False, f"Could not create plugin spec: {mod_path}"
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        api = PluginAPI(mod_name)
        _plugin_apis[mod_name] = api
        if hasattr(mod, "register"):
            mod.register(api)
        _PluginHooks.register_plugin(mod, api)
        _PLUGINS[mod_name] = mod
        if not quiet:
            print(f"  [plugin] Loaded: {mod_name}")
        return True, f"Loaded: {mod_name}"
    except Exception as e:
        if not quiet:
            print(f"  [plugin] Error loading {mod_name}: {e}")
        return False, f"Error loading {mod_name}: {e}"

def load_plugins():
    """Load external command plugins from ~/.prism32/plugins/.
    Uses importlib.util to load from file path (no sys.path manipulation needed)."""
    if _LOW_RAM:
        return
    global PLUGIN_DIR
    if not os.path.isdir(PLUGIN_DIR):
        try:
            os.makedirs(PLUGIN_DIR, exist_ok=True)
            return
        except OSError:
            return
    try:
        for f in sorted(os.listdir(PLUGIN_DIR)):
            if f.endswith(".py") and not f.startswith("_"):
                mod_path = os.path.join(PLUGIN_DIR, f)
                _load_plugin_file(mod_path, mod_name=f[:-3])
    except OSError:
        pass

# ── Self-Evolving Memory System ─────────────────────────────
# Small persistent file (~/.prism32/memory.json) that tracks
# usage patterns, errors, and preferences to improve over time.

MEMORY_FILE = os.path.join(_PRISM32_HOME, "memory.json")
STARTUP_MEMORY_FILE = os.path.join(_PRISM32_HOME, "startup_memory.md")
SOUL_FILE = os.path.join(_PRISM32_HOME, "soul.md")
PROMPTSHARD_FILE = os.path.join(_PRISM32_HOME, "promptshard.md")
HARNESS_FILE = os.path.join(_PRISM32_HOME, "harnesses.json")
EVOLVE_DIR = os.path.join(_PRISM32_HOME, "evolve")
EVOLVE_DOC_FILE = os.path.join(EVOLVE_DIR, "evolve.md")
EVOLVE_TOOL_FILE = os.path.join(EVOLVE_DIR, "tools.json")
EVOLVE_BASELINE_DIR = os.path.join(EVOLVE_DIR, "baseline")
EVOLVE_BASELINE_FILE = os.path.join(EVOLVE_BASELINE_DIR, "prism32.py")
EVOLVE_BASELINE_CONFIG_FILE = os.path.join(EVOLVE_BASELINE_DIR, "config.default.json")
EVOLVE_TEMP_PLUGIN_DIR = os.path.join(EVOLVE_DIR, "tmp_plugins")

# Secrets vault: stored separately from promptshard to prevent injection
SECRETS_FILE = os.path.join(_PRISM32_HOME, ".secrets.json")

_MEMORY_DIRTY = False
_MEMORY_FLUSH_COUNTER = 0
_LAST_INTERJECT = ""
_CURRENT_SESSION_ID = None
_EVOLVE_MODE = False

# ── Interjection state ────────────────────────────────────────
_INTERJECTION_ACTIVE = False
_INTERJECTION_BUF = ""
_INTERJECTION_CURSOR = 0
_INTERJECTION_RESULT = None
_SAVED_TERMIOS = None
_INTERJECTION_HAS_TYPED = False
_INTERJECTION_ESCAPE = False
_INTERJECTION_ESCAPE_BUF = ""
_INTERJECTION_HISTORY = []
_INTERJECTION_HISTORY_IDX = -1
_INTERJECTION_SAVED_BUF = ""
_INTERJECTION_CANCEL = object()
AGENT_CANCELLED_RESPONSE = "[CANCELLED] Agent stopped by Escape"
RESPONSE_BUDGET_EXHAUSTED = "[BUDGET EXHAUSTED] reasoning consumed the entire response budget before any content was produced"
_AGENT_CANCEL_REQUESTED = False
_AGENT_CANCEL_REASON = ""

# ── Footer animator state ─────────────────────────────────────
_AGENT_BUSY = False
_AGENT_STATE = "idle"
_FOOTER_ANIMATOR = None
_FOOTER_FRAME = 0
_FOOTER_HISTORY_REF = None
_FOOTER_TOOL_NAME = ""

# ── Session