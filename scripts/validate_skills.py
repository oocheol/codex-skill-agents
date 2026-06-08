#!/usr/bin/env python3
import os
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    skills_dir = os.path.join(repo_root, "skills")

    print(f"Checking skills directory: {skills_dir}")
    if not os.path.isdir(skills_dir):
        print(f"Error: skills directory not found at {skills_dir}")
        sys.exit(1)

    skills = []
    for entry in os.scandir(skills_dir):
        if entry.is_dir():
            skills.append(entry.name)

    print(f"Found {len(skills)} skills: {', '.join(skills)}")
    sys.exit(0)

if __name__ == "__main__":
    main()
