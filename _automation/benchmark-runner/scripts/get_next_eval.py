import json
import subprocess
import argparse
import sys
import os
import re

def get_git_sha(skill_dir):
    try:
        # Get the SHA of the SKILL.md file in the skill directory
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        result = subprocess.run(
            ["git", "log", "-n", "1", "--format=%H", "--", skill_md_path],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting SHA for {skill_dir}: {e}", file=sys.stderr)
        return "unknown"

def check_github_comments(issue_id, target_sha, target_model):
    try:
        # Parse issue number from github-issue-N
        match = re.search(r'(\d+)$', issue_id)
        if not match:
            return False
        issue_number = match.group(1)

        # We assume gh is authenticated. If not, this script should fail gracefully.
        result = subprocess.run(
            ["gh", "issue", "view", issue_number, "--json", "comments"],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        
        for comment in data.get("comments", []):
            body = comment.get("body", "")
            if "Automated Benchmark Results" in body:
                # Check for exact matches of SHA and Model in the markdown table/metadata
                has_sha = f"Skill version: `{target_sha}`" in body or f"**Skill version** | `{target_sha}`" in body
                has_model = f"**Model** | `{target_model}`" in body or f"**Model** | {target_model}" in body
                
                if has_sha and has_model:
                    return True
        return False
    except Exception as e:
        # If gh fails or issue doesn't exist, we treat it as "needs benchmark"
        print(f"Warning: Could not check comments for issue {issue_id}: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="The name of the model currently being used")
    args = parser.parse_args()

    # Discover skills (folders with SKILL.md and evals/evals.json)
    skills = []
    for item in os.listdir("."):
        if os.path.isdir(item) and not item.startswith(".") and not item.startswith("_"):
            skill_md = os.path.join(item, "SKILL.md")
            evals_json = os.path.join(item, "evals", "evals.json")
            if os.path.exists(skill_md) and os.path.exists(evals_json):
                skills.append(item)
    
    # Process skills in alphabetical order
    skills.sort()

    for skill_dir in skills:
        evals_path = os.path.join(skill_dir, "evals", "evals.json")
        try:
            with open(evals_path, 'r') as f:
                eval_data = json.load(f)
            
            skill_name = eval_data.get("skill_name", skill_dir)
            skill_sha = get_git_sha(skill_dir)
            
            # Iterate through evals in file order
            for eval_case in eval_data.get("evals", []):
                eval_id = eval_case.get("id")
                
                # Check if this eval case is already completed for this SHA and Model
                if not check_github_comments(eval_id, skill_sha, args.model):
                    # Found the first pending eval case
                    # Enrich with skill metadata
                    eval_case["_skill_name"] = skill_name
                    eval_case["_skill_sha"] = skill_sha
                    eval_case["_skill_dir"] = skill_dir
                    
                    # Pre-read the main skill content
                    with open(os.path.join(skill_dir, "SKILL.md"), "r") as s:
                        eval_case["_skill_content"] = s.read()

                    # Bundle supporting resources (all other .md and .py files in the skill dir)
                    # This avoids the agent having to fetch references/examples separately.
                    bundled = {}
                    for root, _, files in os.walk(skill_dir):
                        for f in files:
                            if (f.endswith(".md") or f.endswith(".py")) and f != "evals.json":
                                rel_path = os.path.relpath(os.path.join(root, f), skill_dir)
                                try:
                                    with open(os.path.join(root, f), "r") as res_file:
                                        bundled[rel_path] = res_file.read()
                                except:
                                    pass
                    eval_case["_bundled_resources"] = bundled
                    
                    print(json.dumps(eval_case, indent=2))
                    return

        except Exception as e:
            print(f"Error processing {evals_path}: {e}", file=sys.stderr)

    print("STATUS: UP_TO_DATE")

if __name__ == "__main__":
    main()
