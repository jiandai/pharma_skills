# Skill Benchmark Runner

Automated benchmarking tool that compares AI agent performance **with** vs. **without** a skill, then posts scored results directly to the originating GitHub issue.

## How It Works

1. **Scans**: Locates all skill folders containing `evals/evals.json`.
2. **Filters**: Checks linked GitHub issues to see if a benchmark for the **current skill version AND current model** already exists.
3. **Prioritizes**: Selects exactly **one** pending evaluation based on the order of appearance in the `evals.json` file.
4. **Executes**: Launches two sub-agents in parallel (with vs. without skill).
5. **Scores**: Evaluates both outputs against the defined assertions.
6. **Posts**: Comments the structured comparison table directly to the GitHub issue.

## Usage

### As a Cowork Scheduled Task

This skill is designed to be used as a [Cowork](https://claude.ai) scheduled task. Import `SKILL.md` as the task prompt and set it to manual trigger.

### As a Standalone Skill

Point any agents.md-compatible agent at this folder and ask it to "run benchmarks" or "compare skill performance".

## Report Format

Each benchmark posts a comment containing:

| Field | Description |
|---|---|
| **Eval ID** | Links back to the GitHub issue (e.g. `github-issue-2`) |
| **Model** | Which Claude model both agents used |
| **Skill version** | Git commit SHA of the skill's `SKILL.md` at time of run |
| **Scorecard** | Side-by-side pass/partial/fail counts |
| **Assertion breakdown** | Per-assertion comparison |
| **Verdict** | Summary of where the skill helped (or didn't) |

## Requirements

- GitHub CLI (`gh`) authenticated with write access to the repo, **or** Claude in Chrome as fallback
- Access to the Agent tool for parallel sub-agent execution

## License

MIT
