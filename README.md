# 🔬 Claude Skill Auditor

### *8-Dimensional Skill Analysis Engine for Claude Code*

<p align="center">
  <img src="https://img.shields.io/badge/python-3.6+-blue?style=flat-square&logo=python" alt="Python 3.6+" />
  <img src="https://img.shields.io/badge/dependencies-zero-success?style=flat-square" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="MIT License" />
  <img src="https://img.shields.io/badge/Claude%20Code-ready-8B5CF6?style=flat-square&logo=claude" alt="Claude Ready" />
  <img src="https://img.shields.io/github/stars/lamwon/claude-skill-auditor?style=flat-square&color=gold" alt="Stars" />
</p>

<p align="center">
  <b>A forensic skill auditing tool that scores Claude Code skills across 8 weighted dimensions,<br/>generates actionable recommendations, and produces professional HTML reports.</b>
</p>

<p align="center">
  <code>python auditor.py https://github.com/user/skill-repo --html</code>
</p>

---

## 🎯 Why This Exists

Claude Code skills vary wildly in quality. Some are masterfully engineered; others contain syntax errors, missing documentation, or no error handling.

**Claude Skill Auditor** exists to bring objectivity to skill quality assessment. It's the code review you wish every skill author had done before publishing.

| Problem | Solution |
|---------|----------|
| ❌ Skills with broken code | ✅ Syntax and error handling detection |
| ❌ Missing documentation | ✅ Documentation completeness scoring |
| ❌ No error handling | ✅ Resilience analysis with retry detection |
| ❌ Poor maintainability | ✅ Code structure and comment analysis |
| ❌ Zero discoverability | ✅ SEO recommendations (topics, README) |

---

## ✨ Features

| Feature | Details |
|---------|---------|
| **8-Dimension Scoring** | Code Integrity, Documentation, Architecture, UX, Resilience, Cross-Platform, Maintainability, Innovation |
| **Weighted Matrix** | Each dimension weighted by impact (1.0x–0.5x) |
| **GitHub URL Mode** | Fetch and analyze any public skill repository |
| **Local Path Mode** | Analyze skills on your filesystem |
| **Terminal Report** | Beautiful ASCII bar chart output |
| **HTML Report** | Dark-themed, interactive, print-friendly |
| **Zero Dependencies** | Pure Python 3.6+ standard library |
| **Claude Code Integration** | Install as a Claude Code skill for on-demand use |

---

## 🚀 Quick Start

### One-liner

```bash
# Analyze any Claude Code skill from GitHub
python auditor.py https://github.com/anthropics/claude-for-legal --html
```

### Or clone and run

```bash
git clone https://github.com/lamwon/claude-skill-auditor.git
cd claude-skill-auditor

# Terminal summary only
python auditor.py https://github.com/anthropics/claude-for-legal

# Full HTML report
python auditor.py https://github.com/anthropics/claude-for-legal --html

# Custom output path
python auditor.py https://github.com/user/repo --html -o my-audit.html

# Local directory
python auditor.py /path/to/skill/folder --html

# Quiet mode (no terminal output, just generate report)
python auditor.py https://github.com/user/repo --html --quiet
```

---

## 📊 Sample Output

```
══════════════════════════════════════════════════════
  CLAUDE SKILL AUDITOR — Analysis Report
  anthropics/claude-for-legal
══════════════════════════════════════════════════════
  Repository:    Legal skill for Claude Code
  Stars:         7723  |  Language: Python
  Files:         42    |  Created: 2024-01-15

  Code Integrity        [██████████] 10/10  (w:1.0)
  Documentation         [████████░░] 8/10   (w:1.0)
  Architecture          [████████░░] 8/10   (w:0.8)
  User Experience       [███████░░░] 7/10   (w:0.9)
  Resilience            [████████░░] 8/10   (w:0.8)
  Cross-Platform        [███████░░░] 7/10   (w:0.6)
  Maintainability       [████████░░] 8/10   (w:0.6)
  Innovation & Value    [████████░░] 8/10   (w:0.5)

  TOTAL                 [████████░░] 8.0/10  Grade: A
══════════════════════════════════════════════════════
```

---

## 📋 The 8 Dimensions

| # | Dimension | Weight | What It Checks |
|---|-----------|--------|----------------|
| 1 | **Code Integrity** | 1.0× | Syntax, error handling, security, style |
| 2 | **Documentation** | 1.0× | README completeness, examples, FAQ, install guide |
| 3 | **Architecture** | 0.8× | File structure, dependency mgmt, `.gitignore` |
| 4 | **User Experience** | 0.9× | Install simplicity, `--help`, output clarity |
| 5 | **Resilience** | 0.8× | Retry logic, rate limiting, timeout, edge cases |
| 6 | **Cross-Platform** | 0.6× | Windows/Mac/Linux, encoding, path handling |
| 7 | **Maintainability** | 0.6× | Comments, centralized config, versioning |
| 8 | **Innovation** | 0.5× | Unique value, differentiation, comparison |

### 📈 Grading Scale

| Grade | Range | Meaning |
|-------|-------|---------|
| **S** | 9.0–10.0 | 🏆 Exemplary — production-ready, well-architected |
| **A** | 8.0–8.9 | ✅ Excellent — minor improvements recommended |
| **B** | 7.0–7.9 | 👍 Good — solid foundation, some gaps |
| **C** | 6.0–6.9 | ⚠️ Fair — functional but needs work |
| **D** | 4.0–5.9 | 🔴 Poor — major issues identified |
| **F** | < 4.0 | ❌ Failing — fundamental problems |

---

## 🔧 Integrating with Claude Code

### Install as a Claude Skill

```bash
# Clone into Claude Code skills directory
git clone https://github.com/lamwon/claude-skill-auditor.git ~/.claude/skills/skill-auditor
```

Then in Claude Code:
```
/audit-skill https://github.com/user/skill-repo
```

Or during conversation:
```
Can you audit this skill for me? https://github.com/user/skill-repo
```

---

## 💡 Use Cases

| Who | When |
|-----|------|
| **Skill Authors** | Before publishing to GitHub — get objective feedback first |
| **Open Source Maintainers** | Review skill PRs with automated scoring |
| **Team Leads** | Enforce quality standards across your skill library |
| **Claude Power Users** | Quickly evaluate if a skill is worth installing |
| **Recruiters** | Assess a candidate's skill-building abilities |

---

## 🏗 Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  GitHub API  │────▶│  SkillAuditor │────▶│  Score Engine   │
│  or Local FS │     │  (Fetcher)    │     │  (8 Dimensions) │
└─────────────┘     └──────────────┘     └────────────────┘
                                                  │
                    ┌─────────────────────────────┤
                    ▼                             ▼
            ┌──────────────┐             ┌────────────────┐
            │  Terminal     │             │  HTML Report    │
            │  Report       │             │  Generator      │
            └──────────────┘             └────────────────┘
```

---

## 📄 License

MIT — use freely, contribute gladly.

---

<p align="center">
  <b>⭐ Star this repository if you find it useful ⭐</b>
  <br/>
  <sub>Built with ❤️ by <a href="https://github.com/lamwon">lamwon</a></sub>
</p>
