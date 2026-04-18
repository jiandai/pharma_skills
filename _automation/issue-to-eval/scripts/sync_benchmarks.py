import json
import subprocess
import os
import sys
from import_issue_eval import parse_issue_markdown, save_to_evals

def sync_all_benchmarks():
    """
    Finds all issues labeled 'benchmark' and syncs them to local evals.json.
    """
    try:
        # Search for all issues labeled "benchmark"
        result = subprocess.run(
            ["gh", "issue", "list", "--label", "benchmark", "--json", "number,body,title", "--limit", "100"],
            capture_output=True, text=True, check=True
        )
        issues = json.loads(result.stdout)
        
        if not issues:
            print("No issues found with 'benchmark' label.")
            return

        print(f"Syncing {len(issues)} issues...")
        
        for issue in issues:
            try:
                parsed = parse_issue_markdown(issue["body"])
                
                # Check for critical fields
                if not parsed.get("skill_name") or not parsed.get("prompt"):
                    print(f"Skipping Issue #{issue['number']}: Missing Skill Name or Query.")
                    continue

                eval_entry = {
                    "id": f"github-issue-{issue['number']}",
                    "prompt": parsed.get("prompt", ""),
                    "expected_output": parsed.get("expected_output", ""),
                    "files": parsed.get("files", []),
                    "assertions": parsed.get("assertions", [])
                }
                
                status = save_to_evals(eval_entry, parsed.get("skill_name", ""))
                print(f"Issue #{issue['number']}: {status}")
                
            except Exception as e:
                print(f"Error processing Issue #{issue['number']}: {e}", file=sys.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error calling GitHub CLI: {e.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    sync_all_benchmarks()
