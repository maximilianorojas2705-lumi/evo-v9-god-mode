# Self-Improving Coding Agent runner
"""
An agent runner that handles benchmark evaluation and self-improvement cycles.
"""

import os
import re
import sys
import json
import shutil
import random
import logging
import asyncio
import platform
import argparse
import subprocess

from uuid import uuid4
from typing import Type
from pathlib import Path
from datetime import datetime
from asyncio.subprocess import Process

from base_agent.src.benchmarks import benchmark_registry
from base_agent.src.benchmarks.base import BaseBenchmark, BenchmarkTracker, Problem
from base_agent.src.utils.archive_analysis import (
    ArchiveAnalyzer,
    compute_statistics,
    ScoreType,
)
from base_agent.src.llm.api import create_completion
from base_agent.src.llm.base import Message
from base_agent.src.types.llm_types import Model, TextContent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global locks
benchmark_trackers = {}
benchmark_locks = {}

# Utility functions ------------------------------------------------------------


def setup_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Self referential agent")
    parser.add_argument(
        "--experiment-id", "-id", type=int, help="ID of experiment to resume"
    )
    parser.add_argument(
        "--iterations", "-n", type=int, default=20, help="Number of iterations to run"
    )
    parser.add_argument(
        "--workers", type=int, default=8, help="Number of parallel problem workers"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-command to perform")

    # Just run through a single benchmark for testing
    test_parser = subparsers.add_parser(
        "test", help="Just run the benchmark on the latest agent iteration"
    )
    test_parser.add_argument("--name", default="gsm8k", help="Benchmark ID to run")

    return parser


def get_next_dir_number(base_dir: str | Path) -> int:
    """
    Returns the next free directory name of the form `run_{i}` in some base_dir.
    """
    base_path = Path(base_dir)
    numbered_dirs = []
    for path in base_path.iterdir():
        if path.is_dir():
            try:
                if path.name.startswith("run_"):
                    numbered_dirs.append(int(path.name.lstrip("run_")))
            except ValueError:
                continue
    # If no numbered directories exist, start with 1
    if not numbered_dirs:
        return 1
    return max(numbered_dirs) + 1


def select_base_agent(
    analyzer: ArchiveAnalyzer,
    current_iteration: int,
    score_type: ScoreType = "mean_score",
) -> int:
    """
    Select which previous agent iteration to use as the base for improvement.

    Args:
        analyzer: ArchiveAnalyzer instance
        current_iteration: The current iteration number
        score_type: Utility score or mean score

    Returns:
        The iteration number to use as base for improvement
    """
    # Get performance data with utility scores
    scores_df, summaries_df = analyzer.get_problem_scores_by_iteration()
    # print(scores_df, summaries_df)
    if scores_df.empty or summaries_df.empty:
        return 0  # Default to first agent if no data

    # Compute statistics including confidence intervals
    stats = compute_statistics(scores_df, summaries_df, score_type=score_type)
    # print(stats)
    if stats.empty:
        return 0

    # Find the best performing iteration
    # Mean score here corresponds to either utility_score or perf based on score_type
    best_idx = stats["target_score"].idxmax()
    best_stats = stats.loc[best_idx]

    # Get the lower confidence bound of the best performing agent
    best_lower_bound = best_stats["ci_lower"]

    # Check each iteration from current back to best (or 0), looking for first
    # agent that meets our criteria
    for i in range(current_iteration, -1, -1):
        if i not in stats.index:
            continue

        current_mean = stats.loc[i, "target_score"]
        logger.info(
            f"Agent {i} mean {score_type} score: {current_mean}; best lower bound: {best_lower_bound}"
        )
        if current_mean >= best_lower_bound:
            return i

        # If we've gone past the best iteration and haven't found a suitable
        # agent, use the best
        try:
            if i <= best_idx:
                return best_idx
        except Exception as e:
            logger.warning(e)
            continue

    logger.info("Defaulting to base agent iteration 0")
    return 0  # Fallback to first agent if something goes wrong


async def run_docker_command(*args) -> tuple[bool, str, str]:
    """Run a command inside a docker container"""
    logger.debug("Running docker command:")
    logger.debug(" ".join(args))
    proc: Process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    success = True
    if proc.returncode != 0:
        logger.debug(f"Command {args[0]} failed: {stderr.decode()}")
        success = False
    return success, stdout.decode().strip(), stderr.decode().strip()


async def wait_for_container_ready(container_name: str, timeout: float = 30):
    """Waits until a container is ready after starting it up"""
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        try:
            # Get container status in JSON format
            _, stdout, _ = await run_docker_command(
                "docker",
                "inspect",
                "--format",
                "{{json .State.Status}}",
                container_name,
            )
            status = json.loads(stdout)

            if status == "running":
                # Additional health check - try a basic command
                try:
                    await run_docker_command("docker", "exec", container_name, "ps")
                    return  # Container is truly ready
                except Exception:
                    pass  # Container not quite ready yet

        except Exception:
            pass  # Container might not exist yet

        await asyncio.sleep(0.1)  # Short delay before retry

    raise TimeoutError(
        f"Container {container_name} did not become ready within {timeout} seconds"
    )


def load_metadata(exp_dir: Path) -> dict:
    """Load the experiment metadata, creating if doesn't exist"""
    metadata_file = exp_dir / "metadata.json"
    if not metadata_file.exists():
        metadata = {
            "experiment_start_timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "executable": sys.executable,
            "agent_iteration": 0,
            "git_commit": None,
            # NOTE: the current_benchmark_idx field will be updated later, and
            # is set to -1 for improvement tasks, and 0, 1, 2, ... otherwise.
            # "current_benchmark_idx": None,
        }
        try:
            metadata["git_commit"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip()
        except subprocess.CalledProcessError:
            pass

        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
    else:
        with open(metadata_file) as f:
            metadata = json.load(f)
    return metadata


def update_metadata(exp_dir: Path, **kwargs) -> None:
    """Update specific metadata fields"""
    metadata = load_metadata(exp_dir)
    metadata.update(kwargs)
    with open(exp_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)


async def update_benchmark_progress(
    exp_dir: Path, benchmark_name: str, problem_id: str, total_problems: int
) -> None:
    """Update the metadata to mark a problem as completed"""
    metadata_file = exp_dir / "metadata.json"

    # Use a file lock to ensure thread safety
    async with asyncio.Lock():
        with open(metadata_file) as f:
            metadata = json.load(f)

        # Initialize benchmark progress if not exists
        if "benchmark_progress" not in metadata:
            metadata["benchmark_progress"] = {}

        if benchmark_name not in metadata["benchmark_progress"]:
            metadata["benchmark_progress"][benchmark_name] = {
                "total": total_problems,
                "completed": 0,
                "problems_completed": [],
            }

        # Ensure total is up-to-date
        metadata["benchmark_progress"][benchmark_name]["total"] = total_problems

        # Update the progress
        if (
            problem_id
            not in metadata["benchmark_progress"][benchmark_name]["problems_completed"]
        ):
            metadata["benchmark_progress"][benchmark_name]["problems_completed"].append(
                problem_id
            )
            metadata["benchmark_progress"][benchmark_name]["completed"] += 1

        # Save metadata
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)


async def generate_contextual_summary(
    problem_statement: str,
    llm_answer: str,
    trace: str,
    score: float,
    parse_errors: str | None = None,
    answer_discussion: str | None = None,
) -> str:
    """
    Generates a summary of the long agent trace for archival and indexing purposes.

    Incorporates the original problem statement, the agent's final answer,
    score, any parsing errors and answer discussion to help better
    contextualise the trace summary.
    """
    scoring_context = (
        f"The agent's answer got a score of {score}"
        "(For binary correct/incorrect answers 0 represents a wrong answer and 1 represents a correct answer. "
        "For other problem types, a higher score is better.)"
    )

    if parse_errors:
        scoring_context += f"\nThere were issues parsing the answer: {parse_errors}"

    if answer_discussion:
        scoring_context += f"\nHere is some additional information about the answer to this problem:\n{answer_discussion}\n"

    summary_prompt = f"""Below is a trace of an agent's execution on the following problem:

Problem:
{problem_statement}

Agent's Answer:
{llm_answer}

Execution Result:
{scoring_context}

Trace:
{trace}

Please write a critical analysis of the agent's performance, taking into account both the solution process and the final outcome. Consider:
- Did the agent follow a logical approach?
- Were there unnecessary steps or inefficiencies?
- If the answer was wrong, where did the agent's reasoning fail?
- If there were parsing errors, what caused them?
- What specific improvements could make the agent more effective?

Keep your analysis concise (no more than 1-2 paragraphs max) but thorough.
"""

    summary = await create_completion(
        messages=[
            Message(
                role="system",
                content=[
                    TextContent(
                        text="You are a critical yet constructive and creative evaluator of AI agent performance."
                    )
                ],
            ),
            Message(role="user", content=[TextContent(text=summary_prompt)]),
        ],
        model=Model.GEMINI_FLASH_2,
    )

    # Assume we'll get a single text completion
    return summary.content[0].text


# New Job class for the queue -------------------------------------------------
class Job:
    """Represents a benchmark problem to be processed"""

    def __init__(self, benchmark_name: str, problem: Problem, benchmark: BaseBenchmark):
        self.benchmark_name = benchmark_name
        self.problem = problem
        self.benchmark = benchmark
        self.id = f"{benchmark_name}:{problem.problem_id}"

    def __str__(self):
        return self.id


# Process a single job --------------------------------------------------------
async def process_job(
    exp_dir: Path,
    agent_dir: Path,
 