---
name: claude-skill-auditor
description: 8-dimensional skill analysis engine for Claude Code. Audits any skill repository with weighted scoring, forensic code inspection, and HTML report generation.
tags: [audit, review, skill-quality, code-analysis, forensics, claude-code]
---

# Claude Skill Auditor

A forensic analysis engine that evaluates Claude Code skills across 8 weighted dimensions. Supports GitHub URL and local paths. Outputs terminal summaries and rich HTML reports.

## Usage

```bash
# Audit a GitHub skill repository
python auditor.py https://github.com/user/skill-name --html

# Audit a local skill directory
python auditor.py /path/to/skill/folder --html

# Quiet mode (HTML only, no terminal output)
python auditor.py https://github.com/user/skill-name --html --quiet
```

## Query in Claude Code

Ask Claude to audit any skill:

> "Audit this skill: https://github.com/user/skill-repo"
> "Run the skill auditor on my current project"
> "Give me a quality assessment of https://github.com/user/skill-repo"

## Output

Terminal report:

```
  Code Integrity        [██████████] 10/10  (w:1.0)
  Documentation         [████████░░] 8/10   (w:1.0)
  ...
  TOTAL                 [████████░░] 8.0/10  Grade: A

  KEY FINDINGS:
    1. [Documentation] Score 7/10 — needs improvement
```

HTML report: dark-themed, print-friendly, embeddable.

## How It Works

1. **Fetch** — retrieves repo metadata, README, SKILL.md, and Python files
2. **Analyze** — 8-dimension weighted scoring with 40+ checkpoints
3. **Report** — generates terminal and HTML output with actionable recommendations

## Requirements

- Python 3.6+ (standard library only)
- Internet access (GitHub URL mode)
