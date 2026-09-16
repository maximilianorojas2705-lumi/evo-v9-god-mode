# Plugin compatibility manifest (temporary)

The September 2026 decomposition (PR #102117) split the large modules of Hermes Agent into focused
files. **Internal import paths are not a stable API**, and after that PR the names below are no
longer defined where they used to be. To give external plugin authors time to update, every name
is still importable from its OLD module through a `PLUGIN-COMPAT` block appended to that module.

**This layer is temporary and removed on 2026-09-14.** It was added as a single commit and is removed
by reverting that commit. Update your plugin to import from the `new location` column now.
Nothing inside this repository is allowed to use these pointers (`scripts/check_compat_pointers.py`
fails CI if it does).

**What happens to an affected plugin.**

| when | CLI banner / `hermes doctor` / `hermes update` | Desktop | the plugin |
|---|---|---|---|
| before 2026-09-14 | yellow notice naming the plugin, the date, and `hermes plugins compat` | one-time modal (per set of affected plugins) | loads; each old-path resolution emits `HermesPluginCompatWarning` once |
| from 2026-09-14 | red notice: plugin **DISABLED** | one-time modal | **not loaded**; `hermes plugins list` shows the reason |
| after the revert lands | same | same | not loaded (the old paths no longer exist) |

Escape hatch for users who cannot wait on an author: `plugins.allow_deprecated_imports: true` in
`config.yaml` keeps affected plugins loading after the date, until the revert actually removes the paths.

**For plugin authors:** run `hermes plugins compat <path-to-your-plugin>` — it prints every `file:line`,
old path → new path, and exits 1 while anything remains. Import from the `new location` column.

**You will see a warning.** The first time a process resolves a name through one of these blocks, Hermes emits a
`HermesPluginCompatWarning` (a `FutureWarning`) naming the old path, the new path, and the removal target — once per
name per process. Fix the import and it goes away. To silence during migration:
`python -W ignore::hermes_cli.plugin_compat.HermesPluginCompatWarning` or `warnings.filterwarnings("ignore", category=HermesPluginCompatWarning)`.

**Scope.** Only PUBLIC names (no leading underscore) that were defined or imported at module top level
before the decomposition are covered. Private names (`_foo`, `_TG_NAME_LIMIT`, `_clamp_telegram_names`,
...) were never part of any surface and are NOT restored; a plugin that patched or imported one must move
to the public equivalent or the new module. Test monkeypatch seams are likewise not preserved.

| kind | count | meaning |
|---|---|---|
| moved | 0 | name now defined in `new location`; re-exported from the old module |
| moved-lazy | 1148 | same, resolved lazily via `__getattr__` to avoid an import cycle |
| import | 592 | a third-party/stdlib name the old module used to expose; original import restored |
| restored-def | 290 | public name that was deleted as unused; its pre-decomposition definition is restored verbatim |
| restored-helper | 41 | private helper restored only because a restored-def above depends on it |
| restored-import | 17 | import re-added only because a restored-def above depends on it |
| module-stub | 3 | whole module deleted; stub re-exports from its replacement |
| unrestorable | 34 | not restorable (e.g. leaked loop variables); listed for completeness |

## Names by old module


### `acp_adapter.auth`

| name | kind | new location |
|---|---|---|
| `has_provider` | restored-def | `(deleted; BASE body restored)` |

### `acp_adapter.edit_approval`

| name | kind | new location |
|---|---|---|
| `FutureTimeout` | import | `concurrent.futures` |
| `clear_edit_approval_requester` | restored-def | `(deleted; BASE body restored)` |
| `get_edit_approval_requester` | restored-def | `(deleted; BASE body restored)` |

### `acp_adapter.events`

| name | kind | new location |
|---|---|---|
| `json` | import | `json` |

### `acp_adapter.server`

| name | kind | new location |
|---|---|---|
| `ACP_MAX_MODELS_PER_PROVIDER` | moved-lazy | `acp_adapter.model_catalog` |
| `AgentThoughtChunk` | import | `acp.schema` |
| `AudioContentBlock` | import | `acp.schema` |
| `AvailableCommand` | import | `acp.schema` |
| `AvailableCommandsUpdate` | import | `acp.schema` |
| `BlobResourceContents` | import | `acp.schema` |
| `EmbeddedResourceContentBlock` | import | `acp.schema` |
| `ImageContentBlock` | import | `acp.schema` |
| `Path` | import | `pathlib` |
| `ResourceContentBlock` | import | `acp.schema` |
| `TextResourceContents` | import | `acp.schema` |
| `UnstructuredCommandInput` | import | `acp.schema` |
| `base64` | import | `base64` |
| `json` | import | `json` |
| `unquote` | import | `urllib.parse` |
| `urlparse` | import | `urllib.parse` |

### `acp_adapter.session`

| name | kind | new location |
|---|---|---|
| `Lock` | import | `threading` |

### `agent`

| name | kind | new location |
|---|---|---|
| `message_sanitization` | unrestorable | `no top-level definition on BASE` |

### `agent.agent_init`

| name | kind | new location |
|---|---|---|
| `ToolGuardrailDecision` | moved-lazy | `agent.tool_guardrails` |

### `agent.agent_runtime_helpers`

| name | kind | new location |
|---|---|---|
| `agent_runtime_owns_post_tool_hook` | restored-def | `(deleted; BASE body restored)` |
| `intent_ack_continuation_enabled` | restored-def | `(deleted; BASE body restored)` |

### `agent.anthropic_adapter`

| name | kind | new location |
|---|---|---|
| `CredentialPersistError` | moved-lazy | `agent.anthropic_credentials` |
| `Path` | import | `pathlib` |
| `Tuple` | import | `typing` |
| `base_url_host_matches` | moved-lazy | `utils` |
| `base_url_hostname` | moved-lazy | `utils` |
| `claude_code_credentials_path` | moved-lazy | `agent.anthropic_credentials` |
| `copy` | import | `copy` |
| `get_hermes_home` | moved-lazy | `hermes_constants` |
| `is_claude_code_token_valid` | moved-lazy | `agent.anthropic_credentials` |
| `is_rotation_consumed_uncommitted` | moved-lazy | `agent.anthropic_credentials` |
| `json` | import | `json` |
| `mark_rotation_consumed_uncommitted` | moved-lazy | `agent.anthropic_credentials` |
| `os` | import | `os` |
| `platform` | import | `platform` |
| `read_claude_code_credentials` | moved-lazy | `agent.anthropic_credentials` |
| `read_hermes_oauth_credentials` | moved-lazy | `agent.anthropic_credentials` |
| `refresh_anthropic_oauth_pure` | moved-lazy | `agent.anthropic_credentials` |
| `resolve_anthropic_token` | moved-lazy | `agent.anthropic_credentials` |
| `run_hermes_oauth_login_pure` | moved-lazy | `agent.anthropic_credentials` |
| `run_oauth_setup_token` | moved-lazy | `agent.anthropic_credentials` |
| `secrets` | import | `secrets` |
| `stat` | import | `stat` |
| `urlparse` | import | `urllib.parse` |

### `agent.aux_accounting`

| name | kind | new location |
|---|---|---|
| `get_accounting_context` | restored-def | `(deleted; BASE body restored)` |

### `agent.auxiliary_client`

| name | kind | new location |
|---|---|---|
| `NOUS_EXTRA_BODY` | restored-def | `(deleted; BASE body restored)` |
| `Path` | import | `pathlib` |
| `copy` | import | `copy` |
| `get_async_text_auxiliary_client` | restored-def | `(deleted; BASE body restored)` |

### `agent.backend_identity`

| name | kind | new location |
|---|---|---|
| `_REASON_SCOPES` | restored-helper | `(deleted; restored as a dependency of classify_failure_scope)` |
| `classify_failure_scope` | restored-def | `(deleted; BASE body restored)` |

### `agent.background_review`

| name | kind | new location |
|---|---|---|
| `Path` | import | `pathlib` |
| `is_background_review_enabled` | restored-def | `(deleted; BASE body restored)` |

### `agent.bedrock_adapter`

| name | kind | new location |
|---|---|---|
| `CONTEXT_OVERFLOW_PATTERNS` | restored-def | `(deleted; BASE body restored)` |
| `OVERLOAD_PATTERNS` | restored-def | `(deleted; BASE body restored)` |
| `THROTTLE_PATTERNS` | restored-def | `(deleted; BASE body restored)` |
| `call_converse_stream` | restored-def | `(deleted; BASE body restored)` |
| `classify_bedrock_error` | restored-def | `(deleted; BASE body restored)` |
| `is_context_overflow_error` | restored-helper | `(deleted; restored as a dependency of classify_bedrock_error)` |
| `is_context_overflow_error` | restored-def | `(deleted; BASE body restored)` |

### `agent.bounded_response`

| name | kind | new location |
|---|---|---|
| `Optional` | import | `typing` |
| `read_error_body_or_default` | restored-def | `(deleted; BASE body restored)` |

### `agent.browser_provider`

| name | kind | new location |
|---|---|---|
| `Any` | import | `typing` |
| `Optional` | import | `typing` |

### `agent.browser_registry`

| name | kind | new location |
|---|---|---|
| `Dict` | import | `typing` |
| `List` | import | `typing` |
| `hermes_home_key` | moved-lazy | `hermes_constants` |
| `threading` | import | `threading` |

### `agent.codex_runtime`

| name | kind | new location |
|---|---|---|
| `run_codex_create_stream_fallback` | restored-def | `(deleted; BASE body restored)` |

### `agent.coding_context`

| name | kind | new location |
|---|---|---|
| `_PROFILES` | restored-helper | `(deleted; restored as a dependency of get_profile)` |
| `coding_system_blocks` | restored-def | `(deleted; BASE body restored)` |
| `get_profile` | restored-def | `(deleted; BASE body restored)` |

### `agent.context_compressor`

| name | kind | new location |
|---|---|---|
| `tool_result_id_variants` | moved-lazy | `agent.message_sanitization` |

### `agent.conversation_compression`

| name | kind | new location |
|---|---|---|
| `CompressionExecutorSaturatedError` | restored-def | `(deleted; BASE body restored)` |

### `agent.conversation_loop`

| name | kind | new location |
|---|---|---|
| `COMPRESSION_RETRY_CONTEXT_REDUCED_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `COMPRESSION_RETRY_MESSAGES_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `COMPRESSION_RETRY_TOKENS_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `COMPRESSION_RETRY_TOO_LARGE_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `FailoverReason` | moved-lazy | `agent.error_classifier` |
| `KawaiiSpinner` | moved-lazy | `agent.display` |
| `PARTIAL_STREAM_STUB_ID` | moved-lazy | `hermes_constants` |
| `PRE_API_COMPRESSION_STATUS_TEMPLATE` | moved-lazy | `agent.conversation_compression` |
| `adaptive_rate_limit_backoff` | moved-lazy | `agent.retry_utils` |
| `anchored_context_tokens` | moved-lazy | `agent.model_metadata` |
| `automatic_compaction_status_message` | moved-lazy | `agent.context_engine` |
| `capture_usage_anchor` | moved-lazy | `agent.model_metadata` |
| `classify_api_error` | moved-lazy | `agent.error_classifier` |
| `close_interrupted_tool_sequence` | moved-lazy | `agent.message_sanitization` |
| `coalesce_tool_call_id` | moved-lazy | `agent.message_sanitization` |
| `compose_user_api_content` | moved-lazy | `agent.turn_context` |
| `compression_blocked_transiently` | moved-lazy | `agent.conversation_compression` |
| `compression_skipped_due_to_lock` | moved-lazy | `agent.conversation_compression` |
| `context_compression_timed_out` | moved-lazy | `agent.conversation_compression` |
| `conversation_history_after_compression` | moved-lazy | `agent.conversation_compression` |
| `env_var_enabled` | moved-lazy | `utils` |
| `estimate_messages_tokens_rough` | moved-lazy | `agent.model_metadata` |
| `estimate_request_tokens_rough` | moved-lazy | `agent.model_metadata` |
| `estimate_usage_cost` | moved-lazy | `agent.usage_pricing` |
| `get_context_length_from_provider_error` | moved-lazy | `agent.model_metadata` |
| `has_incomplete_scratchpad` | moved-lazy | `agent.trajectory` |
| `is_output_cap_error` | moved-lazy | `agent.model_metadata` |
| `is_repetition_dominated` | moved-lazy | `agent.repetition_guard` |
| `is_zai_coding_overload_error` | moved-lazy | `agent.retry_utils` |
| `jitt