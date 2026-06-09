#!/usr/bin/env python3
import argparse
import os
import sys
import re
import tempfile
import shutil
import subprocess
import platform

def check_markdown_links(file_path):
    """
    Parses a Markdown file and finds relative links.
    Checks if their local target files exist on disk.
    
    Skips:
    - Absolute URLs (http/https/mailto/ftp)
    - Anchors/IDs starting with '#'
    - Query parameters or hash anchors in relative paths
    """
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"Failed to read file for link checking: {e}"]
        
    # Regular expression to find markdown links: [text](url)
    link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
    links = link_pattern.findall(content)
    
    file_dir = os.path.dirname(file_path)
    for text, url in links:
        url = url.strip()
        # Skip absolute links
        if url.startswith(("http://", "https://", "mailto:", "ftp:")):
            continue
        # Skip absolute system paths or anchors
        if url.startswith("#"):
            continue
            
        # Remove anchor part of the link if present (e.g., file.md#section)
        clean_url = url.split('#', 1)[0]
        if not clean_url:
            continue
            
        # Target path relative to the file directory
        target_path = os.path.join(file_dir, clean_url)
        # Normalize path
        target_path = os.path.normpath(target_path)
        
        if not os.path.exists(target_path):
            errors.append(f"Broken relative link: '[{text}]({url})' -> target not found at '{clean_url}'")
            
    return errors

def parse_front_matter(content):
    """
    Parses simple YAML front-matter from a file content.
    Expects front-matter to be enclosed between '---' lines at the start of the file.
    Returns a dictionary of parsed key-value pairs, or None if invalid.
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
            val = val.strip()
            # Unwrap quoted values so `name: "foo"` matches the folder name "foo"
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                val = val[1:-1]
            data[key.strip()] = val
    return data

def parse_simple_yaml(content):
    """
    Parses a simple YAML structure with up to 1-level of indentation.
    Designed for config files (like agents/openai.yaml).
    
    Supported:
    - Key-value pairs (key: value)
    - Comments starting with '#' (stripped out)
    - 1-level nesting (indented keys under a parent key ending with ':')
    - String quoting and basic boolean conversions
    """
    data = {}
    current_key = None
    for line in content.splitlines():
        # Strip inline comments only when '#' appears outside quoted strings
        in_quote = None
        comment_idx = None
        for i, ch in enumerate(line):
            if ch in ('"', "'") and in_quote is None:
                in_quote = ch
            elif ch == in_quote:
                in_quote = None
            elif ch == '#' and in_quote is None:
                comment_idx = i
                break
        if comment_idx is not None:
            line = line[:comment_idx]
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

def validate_skill_dir(skill_dir_path, skill_name):
    """
    Validates a single skill directory.
    Performs the following checks:
    1. SKILL.md existence, front-matter parsing, and required fields.
    2. Naming consistency between directory name and front-matter name.
    3. Relative link health inside SKILL.md.
    4. references/source-agent.md existence and relative link health.
    5. agents/openai.yaml existence and schema conformity.
    """
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
        elif fm["name"] != skill_name:
            errors.append(f"Consistency error: SKILL.md name '{fm['name']}' does not match folder name '{skill_name}'")
            
        if "description" not in fm or not fm["description"]:
            errors.append("SKILL.md front-matter missing 'description'")
            
    # 1.1 Check relative links in SKILL.md
    link_errors = check_markdown_links(skill_md_path)
    for err in link_errors:
        errors.append(f"SKILL.md: {err}")

    # 1.2 Check references/source-agent.md existence and relative links
    ref_dir = os.path.join(skill_dir_path, "references")
    ref_md_path = os.path.join(ref_dir, "source-agent.md")
    if not os.path.isdir(ref_dir):
        errors.append("Missing 'references' directory")
    elif not os.path.isfile(ref_md_path):
        errors.append("Missing 'references/source-agent.md' file")
    else:
        ref_link_errors = check_markdown_links(ref_md_path)
        for err in ref_link_errors:
            errors.append(f"references/source-agent.md: {err}")
            
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
            elif f"${skill_name}" not in interface["default_prompt"]:
                errors.append(f"Consistency error: 'interface.default_prompt' does not mention '${skill_name}'")
                
        if "policy" not in yaml_data or not isinstance(yaml_data["policy"], dict):
            errors.append("'agents/openai.yaml' is missing 'policy' section")
        else:
            policy = yaml_data["policy"]
            if "allow_implicit_invocation" not in policy or not isinstance(policy["allow_implicit_invocation"], bool):
                errors.append("'agents/openai.yaml' missing or invalid 'policy.allow_implicit_invocation' (must be boolean)")
            
    return errors

def run_self_tests():
    print("Running validator self-tests...")
    temp_dir = tempfile.mkdtemp()
    try:
        mock_skill_dir = os.path.join(temp_dir, "mock-skill")
        os.makedirs(mock_skill_dir)
        
        # 1. Create a malformed SKILL.md
        skill_md_content = """---
name: wrong-name
description:
---
This is a test skill.
Link to [invalid](non-existent.md)
"""
        with open(os.path.join(mock_skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(skill_md_content)
            
        # 2. Create agents dir but malformed openai.yaml
        os.makedirs(os.path.join(mock_skill_dir, "agents"))
        openai_yaml_content = """interface:
  display_name: "Mock Skill"
  short_description: "A mock skill for testing"
  default_prompt: "Run this without using the dollar sign name"
policy:
  # Missing allow_implicit_invocation
"""
        with open(os.path.join(mock_skill_dir, "agents", "openai.yaml"), "w", encoding="utf-8") as f:
            f.write(openai_yaml_content)
            
        # Run validate_skill_dir on the mock directory
        errors = validate_skill_dir(mock_skill_dir, "mock-skill")
        
        expected_errors = [
            "Consistency error: SKILL.md name 'wrong-name' does not match folder name 'mock-skill'",
            "SKILL.md front-matter missing 'description'",
            "SKILL.md: Broken relative link: '[invalid](non-existent.md)' -> target not found at 'non-existent.md'",
            "Missing 'references' directory",
            "Consistency error: 'interface.default_prompt' does not mention '$mock-skill'",
            "'agents/openai.yaml' missing or invalid 'policy.allow_implicit_invocation' (must be boolean)"
        ]
        
        missing_errors = []
        for expected in expected_errors:
            found = False
            for err in errors:
                if expected in err:
                    found = True
                    break
            if not found:
                missing_errors.append(expected)
                
        if missing_errors:
            print("[-] Self-test FAILED! The validator did not detect the following expected errors:")
            for err in missing_errors:
                print(f"    - {err}")
            print("Detected errors were:")
            for err in errors:
                print(f"    - {err}")
            sys.exit(1)
        else:
            print("[+] Self-test PASSED! All expected malformations were successfully detected.")
    finally:
        shutil.rmtree(temp_dir)

def run_installer_tests():
    print("\nRunning installer validation tests...")
    temp_dir = tempfile.mkdtemp()
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(script_dir)
        
        is_windows = platform.system() == "Windows"
        
        if is_windows:
            ps_script = os.path.join(script_dir, "install.ps1")
            print(f"Testing PowerShell installer: {ps_script}")
            cmd = [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", ps_script,
                "-Destination", temp_dir
            ]
        else:
            sh_script = os.path.join(script_dir, "install.sh")
            print(f"Testing Bash installer: {sh_script}")
            try:
                os.chmod(sh_script, 0o755)
            except Exception:
                pass
            cmd = ["bash", sh_script, temp_dir]
            
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)
        if res.returncode != 0:
            print(f"[-] Installer failed with exit code {res.returncode}")
            print(f"Stdout:\n{res.stdout}")
            print(f"Stderr:\n{res.stderr}")
            sys.exit(1)
            
        print("[+] Installer executed successfully.")
        
        expected_skills = ["backend-architect", "evidence-collector", "frontend-developer", "reality-checker", "security-engineer", "senior-developer"]
        for skill in expected_skills:
            skill_dest_path = os.path.join(temp_dir, skill)
            if not os.path.isdir(skill_dest_path):
                print(f"[-] Installed skill directory '{skill}' not found at destination.")
                sys.exit(1)
            
            errors = validate_skill_dir(skill_dest_path, skill)
            if errors:
                print(f"[-] Installed skill '{skill}' has validation errors:")
                for err in errors:
                    print(f"    - {err}")
                sys.exit(1)
                
        print("[+] All installed skills are structurally valid.")
    finally:
        shutil.rmtree(temp_dir)

def main():
    parser = argparse.ArgumentParser(description="Validate Codex skill directories.",
                                     allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true",
                        help="run the validator self-tests and exit")
    parser.add_argument("--skip-installer-tests", action="store_true",
                        help="skip the installer validation tests")
    args = parser.parse_args()

    if args.self_test:
        run_self_tests()
        sys.exit(0)

    skip_installer = args.skip_installer_tests

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
            errors = validate_skill_dir(skill_path, entry.name)
            if errors:
                print(f"[-] Skill '{entry.name}' has validation errors:")
                for err in errors:
                    print(f"    - {err}")
                has_errors = True
            else:
                print(f"[+] Skill '{entry.name}' is valid")

    print(f"\nVerification finished. Found {len(skills)} skills.")
    if has_errors:
        print("Validation FAILED!")
        sys.exit(1)
    else:
        print("Validation PASSED!")

    if not skip_installer:
        run_installer_tests()
    sys.exit(0)

if __name__ == "__main__":
    main()

