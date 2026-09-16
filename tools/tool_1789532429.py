# -*- coding: utf-8 -*-
"""
Improved version of tool_1789516825.py using Voyager and BabyAGI patterns
to generate highly viral TikTok scripts.
"""

import json
import random
import uuid
from typing import List, Dict, Any

# ---- Voyager integration (placeholder for the real Voyager SDK) ----
try:
    from voyager import VoyagerAgent, TaskQueue, TaskResult
except ImportError:
    # Mock classes for illustration; replace with real Voyager SDK imports.
    class TaskResult:
        def __init__(self, task_id: str, output: str):
            self.task_id = task_id
            self.output = output

    class TaskQueue:
        def __init__(self):
            self._tasks = []

        def add_task(self, description: str, metadata: Dict[str, Any] = None) -> str:
            task_id = str(uuid.uuid4())
            self._tasks.append({"id": task_id, "desc": description, "meta": metadata or {}})
            return task_id

        def pop_task(self) -> Dict[str, Any]:
            return self._tasks.pop(0) if self._tasks else None

        def is_empty(self) -> bool:
            return len(self._tasks) == 0

    class VoyagerAgent:
        def __init__(self, name: str = "TikTokScriptAgent"):
            self.name = name

        def execute(self, task_desc: str, context: Dict[str, Any]) -> TaskResult:
            # Simple mock execution: just echo the task description with random flair.
            output = f"[{self.name}] {task_desc} — generated with style {random.choice(['🔥','✨','🚀'])}"
            return TaskResult(task_id=str(uuid.uuid4()), output=output)


# ---- BabyAGI core loop adapted for TikTok script generation ----
class BabyTikTokAgent:
    """
    Autonomous agent that decomposes the goal "create a viral TikTok script"
    into subtasks, executes them via Voyager, and iteratively refines the script.
    """

    def __init__(self, goal: str):
        self.goal = goal
        self.agent = VoyagerAgent()
        self.task_queue = TaskQueue()
        self.completed_tasks: List[TaskResult] = []
        self.script_parts: Dict[str, str] = {}

    # ---------- Task generation (BabyAGI style) ----------
    def generate_initial_tasks(self):
        """
        Decompose the main goal into core TikTok script components.
        """
        components = [
            ("hook", "Generate a hook that captures attention in the first 3 seconds."),
            ("problem", "Describe a relatable problem or pain point."),
            ("solution", "Present a quick, surprising solution."),
            ("story", "Add a short personal anecdote or example."),
            ("cta", "Create a clear call‑to‑action encouraging likes, follows, or shares."),
        ]
        for name, desc in components:
            self.task_queue.add_task(
                description=f"{name}: {desc}",
                metadata={"component": name}
            )

    def prioritize_tasks(self):
        """
        Simple priority: keep the order of creation; can be expanded with scoring.
        """
        # In this mock version, tasks are already ordered; no action needed.
        pass

    # ---------- Task execution ----------
    def execute_next_task(self):
        task = self.task_queue.pop_task()
        if not task:
            return None

        # Provide context from previously generated parts
        context = {k: v for k, v in self.script_parts.items() if k != task["meta"]["component"]}

        result = self.agent.execute(task["desc"], context)
        self.completed_tasks.append(result)

        # Store result in script_parts
        component = task["meta"]["component"]
        self.script_parts[component] = result.output
        return result

    # ---------- Refinement loop ----------
    def refine_script(self):
        """
        After initial generation, ask Voyager to improve coherence and virality.
        """
        refinement_prompt = (
            "Take the following TikTok script parts and rewrite them into a single, "
            "cohesive, high‑energy script that follows the AIDA (Attention‑Interest‑Desire‑Action) "
            "framework, maximising shareability and emotional impact:\n"
            + json.dumps(self.script_parts, ensure_ascii=False, indent=2)
        )
        result = self.agent.execute(refinement_prompt, {})
        self.script_parts["final_script"] = result.output
        self.completed_tasks.append(result)

    # ---------- Orchestrator ----------
    def run(self):
        # Step 1: generate and enqueue initial tasks
        self.generate_initial_tasks()

        # Step 2: execute tasks until queue empty
        while not self.task_queue.is_empty():
            self.prioritize_tasks()
            self.execute_next_task()

        # Step 3: refine final script
        self.refine_script()

        return self.script_parts.get("final_script", "")


# ---- Helper functions for external use ----
def generate_viral_tiktok_script(topic: str) -> str:
    """
    Public API: given a topic (e.g., 'DIY coffee hack'), produce a viral TikTok script.
    """
    goal = f"Create a viral TikTok script about '{topic}'."
    agent = BabyTikTokAgent(goal=goal)

    # Inject the topic as part of the context for the hook generation
    agent.script_parts["topic"] = topic

    final_script = agent.run()
    return final_script


# ---- Example usage (remove or comment out when importing as a module) ----
if __name__ == "__main__":
    sample_topic = "3 easy ways to boost your phone battery life"
    script = generate_viral_tiktok_script(sample_topic)
    print("\n--- Generated Viral TikTok Script ---\n")
    print(script)