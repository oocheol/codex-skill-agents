#!/usr/bin/env python3
import os
import sys

def parse_front_matter(content):
    """
    Parses YAML front-matter from file content.
    Returns a dictionary of key-value pairs if found, or None.
    """
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    
    front_matter_lines = []
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
        front_matter_lines.append(lines[i])
        
    if end_idx == -1:
        return None
        
    data = {}
    for line in front_matter_lines:
        if ":" in line:
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip()
    return data

def validate_skill_dir(skill_dir_path):
    errors = []
    
    # Check SKILL.md existence
    skill_md_path = os.path.join(skill_dir_path, "SKILL.md")
    if not os.path.isfile(skill_md_path):
        errors.append("Missing SKILL.md")
        return errors

    # Parse and validate SKILL.md front-matter
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        errors.append(f"Failed to read SKILL.md: {e}")
        return errors

    fm = parse_front_matter(content)
    if fm is None:
        errors.append("SKILL.md does not contain a valid YAML front-matter (enclosed in ---)")
    else:
        if "name" not in fm or not fm["name"]:
            errors.append("SKILL.md front-matter missing 'name'")
        if "description" not in fm or not fm["description"]:
            errors.append("SKILL.md front-matter missing 'description'")
            
    return errors

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    skills_dir = os.path.join(repo_root, "skills")

    print(f"Checking skills directory: {skills_dir}")
    if not os.path.isdir(skills_dir):
        print(f"Error: skills directory not found at {skills_dir}")
        sys.exit(1)

    has_errors = False
    skills = []
    for entry in os.scandir(skills_dir):
        if entry.is_dir():
            skills.append(entry.name)
            skill_path = os.path.join(skills_dir, entry.name)
            errors = validate_skill_dir(skill_path)
            if errors:
                print(f"[-] Skill '{entry.name}' has validation errors:")
                for err in errors:
                    print(f"    - {err}")
                has_errors = True
            else:
                print(f"[+] Skill '{entry.name}' is valid (Step 2: SKILL.md checks)")

    print(f"\nVerification finished. Found {len(skills)} skills.")
    if has_errors:
        print("Validation FAILED!")
        sys.exit(1)
    else:
        print("Validation PASSED!")
        sys.exit(0)

if __name__ == "__main__":
    main()

