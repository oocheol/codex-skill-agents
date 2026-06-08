# Codex Skill Agents

Role-based Agent Skills for OpenAI Codex maintainers.

This repository packages a small set of practical Codex skills for software
maintenance workflows: implementation, architecture review, frontend work,
security review, evidence collection, and readiness checks.

The goal is simple: help open source maintainers use Codex as a repeatable
review and maintenance assistant instead of re-prompting the same role
instructions for every pull request, issue, or release.

## Skills

| Skill | Use it for |
| --- | --- |
| `senior-developer` | Production-quality implementation and pragmatic refactors |
| `backend-architect` | API, database, reliability, and backend system design |
| `frontend-developer` | UI implementation, accessibility, responsiveness, and browser QA |
| `security-engineer` | Threat modeling, secure code review, and remediation guidance |
| `evidence-collector` | Screenshot-backed QA, interaction testing, and proof gathering |
| `reality-checker` | Final readiness checks against claims, specs, and evidence |

Each skill has:

- `SKILL.md`: the compact Codex-facing playbook
- `agents/openai.yaml`: UI metadata for Codex-compatible surfaces
- `references/source-agent.md`: the original upstream role prompt adapted from
  `msitarzewski/agency-agents`

## Install

### PowerShell

```powershell
.\scripts\install.ps1
```

### Bash

```bash
./scripts/install.sh
```

By default, both scripts install into:

- Windows: `%USERPROFILE%\.codex\skills`
- macOS/Linux: `$HOME/.codex/skills`

You can override the destination:

```powershell
.\scripts\install.ps1 -Destination "C:\path\to\.codex\skills"
```

```bash
./scripts/install.sh /path/to/.codex/skills
```

Restart Codex after installing so the new skills are discovered.

## Usage Examples

```text
Use $security-engineer to review this pull request for auth and data leakage risks.
```

```text
Use $evidence-collector to verify this UI change across desktop and mobile.
```

```text
Use $reality-checker to decide whether this feature is really ready to merge.
```

```text
Use $backend-architect to design the API and data model before implementation.
```

## Why This Exists

Open source maintainers repeat the same high-friction work constantly:

- reviewing pull requests
- checking security-sensitive changes
- validating frontend behavior
- triaging whether a feature is actually complete
- writing release and maintenance notes
- making architecture decisions under time pressure

Codex can help with this, but it works best when the workflow is explicit and
reusable. These skills make those maintenance roles portable, inspectable, and
versioned.

## Repository Layout

```text
codex-skill-agents/
├── .github/
│   └── workflows/
│       └── validate.yml
├── skills/
│   ├── senior-developer/
│   ├── backend-architect/
│   ├── frontend-developer/
│   ├── security-engineer/
│   ├── evidence-collector/
│   └── reality-checker/
├── scripts/
│   ├── install.ps1
│   ├── install.sh
│   └── validate_skills.py
```

## Development and Validation

To ensure all skills maintain proper structure, front-matter metadata, schema formats, and valid relative links, we provide an automated validation script:

```bash
python scripts/validate_skills.py
```

It checks:
1. `SKILL.md` existence, front-matter syntax, and mandatory keys.
2. `agents/openai.yaml` schema compliance.
3. Relative Markdown link health in all documentation.
4. Consistency between folder name and skill metadata.
5. Dry-run installation script verification (`install.sh` / `install.ps1`).

You can also run validator self-tests using:

```bash
python scripts/validate_skills.py --self-test
```

This validation suite runs automatically via GitHub Actions on every push and pull request.

## Attribution

These skills are adapted from the role prompts in
[`msitarzewski/agency-agents`](https://github.com/msitarzewski/agency-agents).
The original source prompt for each role is preserved in
`references/source-agent.md`.

## License

MIT. See [LICENSE](LICENSE).
