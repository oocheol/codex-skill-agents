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

def parse_simple_yaml(content):
    """
    Parses a simple YAML structure with 1-level of indentation.
    Supported types: string (optionally quoted), boolean.
    """
    data = {}
    current_key = None
    for line in content.splitlines():
        if '#' in line:
            line = line.split('#', 1)[0]
        line = line.rstrip()
        if not line:
            continue
        
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        
        if not stripped.endswith(":") and ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip()
            val = val.strip()
            
            # Remove wrapping quotes
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
                
            if val.lower() == 'true':
                val = True
            elif val.lower() == 'false':
                val = False
                
            if indent > 0 and current_key:
                if not isinstance(data.get(current_key), dict):
                    data[current_key] = {}
                data[current_key][key] = val
            else:
                data[key] = val
        elif stripped.endswith(":"):
            key = stripped[:-1].strip()
            if indent == 0:
                current_key = key
                data[current_key] = {}
    return data

def validate_skill_dir(skill_dir_path):
    errors = []
    
    # 1. Check SKILL.md existence
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
            
    # 2. Check agents/openai.yaml existence and schema
    agents_dir = os.path.join(skill_dir_path, "agents")
    yaml_path = os.path.join(agents_dir, "openai.yaml")
    if not os.path.isdir(agents_dir):
        errors.append("Missing 'agents' directory")
    elif not os.path.isfile(yaml_path):
        errors.append("Missing 'agents/openai.yaml' file")
    else:
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_content = f.read()
            yaml_data = parse_simple_yaml(yaml_content)
        except Exception as e:
            errors.append(f"Failed to read/parse 'agents/openai.yaml': {e}")
            return errors
        
        # Validate schema keys
        if "interface" not in yaml_data or not isinstance(yaml_data["interface"], dict):
            errors.append("'agents/openai.yaml' is missing 'interface' section")
        else:
            interface = yaml_data["interface"]
            if "display_name" not in interface or not interface["display_name"]:
                errors.append("'agents/openai.yaml' missing 'interface.display_name'")
            if "short_description" not in interface or not interface["short_description"]:
                errors.append("'agents/openai.yaml' missing 'interface.short_description'")
            if "default_prompt" not in interface or not interface["default_prompt"]:
                errors.append("'agents/openai.yaml' missing 'interface.default_prompt'")
                
        if "policy" not in yaml_data or not isinstance(yaml_data["policy"], dict):
            errors.append("'agents/openai.yaml' is missing 'policy' section")
        else:
            policy = yaml_data["policy"]
            if "allow_implicit_invocation" not in policy or not isinstance(policy["allow_implicit_invocation"], bool):
                errors.append("'agents/openai.yaml' missing or invalid 'policy.allow_implicit_invocation' (must be boolean)")
            
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

