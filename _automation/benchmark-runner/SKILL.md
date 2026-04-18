---
name: benchmark-runner
description: Auto-discover all skills with evals in RConsortium/pharma_skills, benchmark each with vs. without skill using parallel sub-agents, and post scored results to the linked GitHub issue. Use whenever someone says "run benchmarks", "compare skill performance", "eval the skills", or wants to measure whether a skill improves output quality.
---

# Skill Benchmark Runner

Benchmark every skill in the `RConsortium/pharma_skills` repository that has an `evals/evals.json` file. For each eval case, run two Claude sub-agents in parallel — one using the skill, one without — then post a scored comparison as a comment on the originating GitHub issue.

Repository: `RConsortium/pharma_skills` (https://github.com/RConsortium/pharma_skills)

---

## Step 1 — Get the Next Evaluation Case

Run the dispatcher script to identify the highest-priority pending evaluation:

```bash
python3 _automation/benchmark-runner/scripts/get_next_eval.py --model {CURRENT_MODEL_NAME}
```

- If the output is `STATUS: UP_TO_DATE`, stop and report that all benchmarks are finished.
- If the output is a JSON object, parse it. It contains the `prompt`, `files`, `assertions`, and metadata (`_skill_name`, `_skill_sha`, `_skill_content`, `_bundled_resources`).

---

## Step 2 — Run two sub-agents in parallel

Use the Agent tool to launch both agents simultaneously for the selected eval case.

**Agent A — WITH the skill:**
- Provide the full contents of `_skill_content`.
- Provide all files from `_bundled_resources` (e.g., `reference.md`, `examples.md`, `scripts/gsd_report_template.py`).
- Provide any referenced `files` from the eval case.
- Give the `prompt` from the eval case.
- Instruct: "Follow the skill workflow to complete this task. Produce all expected outputs."

**Agent B — WITHOUT the skill:**
- Give the exact same `prompt` and `files`.
- Instruct: "Complete this task using only your base knowledge and tools. Do NOT use any SKILL.md or skill instructions. Produce all expected outputs."

Both agents use the same model (whichever model this session is running).

---

## Step 3 — Score each output against assertions

For each agent's output, evaluate against every assertion in the eval case:
- Pass — assertion clearly met
- Fail — assertion clearly not met
- Partial — partially met

Score = (passes + 0.5 x partials) / total assertions, as a fraction and percentage.

---

## Step 4 — Format the benchmark report

Write a Markdown file at `/tmp/benchmark_comment_{skill}_{eval_id}.md` using this template:

```markdown
## Automated Benchmark Results — `{_skill_name}`

### Run Metadata

| Field | Value |
|---|---|
| **Eval ID** | `{id}` |
| **Run date** | {YYYY-MM-DD HH:MM UTC} |
| **Model** | `{model name}` |
| **Skill version** | `{_skill_sha}` |
| **Triggered by** | Scheduled/Manual |

### Scorecard

| | With Skill | Without Skill |
|---|---|---|
| **Score** | {score_A} ({pct_A}%) | {score_B} ({pct_B}%) |
| **Assertions** | {pass_A} Pass {partial_A} Partial {fail_A} Fail | {pass_B} Pass {partial_B} Partial {fail_B} Fail |

### Assertion Breakdown

| Assertion | With Skill | Without Skill |
|---|---|---|
| {assertion_text_1} | {Pass/Partial/Fail} | {Pass/Partial/Fail} |
| {assertion_text_2} | {Pass/Partial/Fail} | {Pass/Partial/Fail} |

### Key Observations

- {2-4 bullet points comparing both agents}

### Verdict

{1-2 sentence overall verdict}

---
*Posted automatically by `benchmark-runner` · Repo: https://github.com/RConsortium/pharma_skills*
```

---

## Step 5 — Post to the linked GitHub issue

Extract the issue number from the `id` (e.g., `"github-issue-21"` -> **#21**).

Post using the `gh` CLI:
```bash
gh issue comment {issue_number} --repo RConsortium/pharma_skills --body-file /tmp/benchmark_comment_{skill}_{eval_id}.md
```

---

## Execution Flow

```
Run get_next_eval.py (Detects SHA, Model, and File Order)
  |-- If STATUS: UP_TO_DATE -> Exit
  |-- If JSON -> 
       |-- Agent A (with skill) ---+
       |-- Agent B (without skill)-+--- run in parallel
       |-- Score both against assertions
       |-- Format Markdown report
       |-- Post comment to GitHub issue #{N}
```

## Success Criteria

- Only one high-priority evaluation is processed per run
- Deduplication correctly accounts for both Skill SHA and Model Name
- LLM token usage is minimized by offloading discovery to a script
- Results are posted as comments on the correct GitHub issues
