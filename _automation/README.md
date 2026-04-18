# Automation Skills

This directory contains automated workflows for managing, evaluating, and reporting on the `pharma_skills` ecosystem.

## Skills

| Folder | Name | Purpose |
|---|---|---|
| [`benchmark-runner/`](benchmark-runner/) | **Benchmark Runner** | Runs parallel "With Skill" vs. "Without Skill" evaluations to quantify skill performance. Posts results to GitHub issues. |
| [`issue-to-eval/`](issue-to-eval/) | **Issue to Eval** | Automatically syncs GitHub issues labeled `benchmark` into local `evals.json` suites. Supports updating existing tests if the issue content changes. |
| [`weekly-summary/`](weekly-summary/) | **Weekly Summary** | Aggregates repository activity (commits, PRs, issues) over the last 7 days and generates a concise status update for Slack. |

## Usage

Each skill contains a `SKILL.md` file that provides specific instructions for LLM agents to execute the workflow. To run a skill, point an agent at its directory or reference its `SKILL.md` content directly.
