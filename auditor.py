#!/usr/bin/env python3
"""
Claude Skill Auditor — 8-Dimensional Skill Analysis Engine
============================================================

A forensic auditing tool that analyzes Claude Code skills across 8 dimensions
with weighted scoring, automated pattern detection, and rich HTML reporting.

Usage:
    python auditor.py https://github.com/user/skill-repo
    python auditor.py /path/to/local/skill --report
    python auditor.py https://github.com/user/skill-repo --html -o audit.html

Author: Hermes Agent
License: MIT
"""

import os, sys, json, re, base64, textwrap, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

__version__ = "1.0.0"

# ─── Scoring Dimensions ─────────────────────────────────────────────────────

DIMENSIONS = [
    {
        "id": "code_quality",
        "name": "Code Integrity",
        "weight": 1.0,
        "description": "Syntax correctness, error handling, security posture, code style",
        "checks": ["Syntax validation", "Error handling", "Security review", "PEP 8 compliance"],
    },
    {
        "id": "documentation",
        "name": "Documentation",
        "weight": 1.0,
        "description": "README/SKILL.md completeness, install guide, examples, FAQ",
        "checks": ["Install guide", "Usage examples", "Parameter reference", "FAQ"],
    },
    {
        "id": "architecture",
        "name": "Architecture",
        "weight": 0.8,
        "description": "File structure, dependency management, engineering config",
        "checks": ["Standalone scripts", ".gitignore present", "No duplicates", "Modular design"],
    },
    {
        "id": "ux",
        "name": "User Experience",
        "weight": 0.9,
        "description": "Install ease, parameter intuitiveness, output clarity",
        "checks": ["One-command install", "--help available", "Clear output", "Error messages"],
    },
    {
        "id": "resilience",
        "name": "Resilience",
        "weight": 0.8,
        "description": "Retry logic, rate limiting, timeout handling, edge cases",
        "checks": ["Retry mechanism", "Rate limit handling", "Timeout config", "Edge cases"],
    },
    {
        "id": "portability",
        "name": "Cross-Platform",
        "weight": 0.6,
        "description": "Windows/macOS/Linux compatibility, encoding, path handling",
        "checks": ["Path abstraction", "UTF-8 encoding", "Shell compatibility", "No hardcoded paths"],
    },
    {
        "id": "maintainability",
        "name": "Maintainability",
        "weight": 0.6,
        "description": "Comments, centralized config, versioning, changelog",
        "checks": ["Code comments", "Centralized config", "Version tracking", "Changelog"],
    },
    {
        "id": "innovation",
        "name": "Innovation & Value",
        "weight": 0.5,
        "description": "Unique value proposition, differentiation, comparison evidence",
        "checks": ["Solves real problem", "Competitive analysis", "Unique features", "Use cases"],
    },
]


class SkillAuditor:
    """Core auditor engine that fetches, analyzes, and scores skills."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self._cache = {}

    def fetch_from_github(self, repo_url: str) -> dict:
        """Fetch repository metadata and contents from GitHub API."""
        match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", repo_url)
        if not match:
            raise ValueError(f"Cannot parse GitHub URL: {repo_url}")

        owner, name = match.group(1), match.group(2)
        api_base = f"https://api.github.com/repos/{owner}/{name}"

        # Repo metadata
        repo = self._api_get(api_base)
        default_branch = repo.get("default_branch", "main")

        # File contents
        files = {}
        for fname in ["SKILL.md", "README.md", "CLAUDE.md", "skill/SKILL.md"]:
            for branch in [default_branch, "main", "master"]:
                url = f"https://raw.githubusercontent.com/{owner}/{name}/{branch}/{fname}"
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "auditor/1.0"})
                    resp = urllib.request.urlopen(req, timeout=10)
                    files[fname] = resp.read().decode("utf-8", errors="replace")
                    break
                except Exception:
                    continue

        # Repository contents listing
        try:
            contents = self._api_get(f"{api_base}/contents")
            contents_list = [c["name"] for c in contents if isinstance(c, dict)]
        except Exception:
            contents_list = []

        # Python file contents
        py_files = {}
        for item in contents_list:
            if item.endswith(".py"):
                for branch in [default_branch, "main", "master"]:
                    url = f"https://raw.githubusercontent.com/{owner}/{name}/{branch}/{item}"
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": "auditor/1.0"})
                        resp = urllib.request.urlopen(req, timeout=5)
                        py_files[item] = resp.read().decode("utf-8", errors="replace")
                        break
                    except Exception:
                        continue

        return {
            "name": repo.get("name", name),
            "full_name": repo.get("full_name", f"{owner}/{name}"),
            "description": repo.get("description", ""),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "language": repo.get("language", ""),
            "topics": repo.get("topics", []),
            "license": repo.get("license", {}).get("spdx_id", "N/A") if repo.get("license") else "N/A",
            "created": repo.get("created_at", "")[:10],
            "updated": repo.get("updated_at", "")[:10],
            "files": files,
            "py_files": py_files,
            "contents": contents_list,
        }

    def fetch_from_local(self, path: str) -> dict:
        """Read skill from local filesystem."""
        base = Path(path)
        if not base.is_dir():
            raise NotADirectoryError(f"Directory not found: {path}")

        files = {}
        py_files = {}
        contents = []

        for f in base.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".py", ".json", ".yaml", ".toml", ".txt", ".cfg"):
                rel = str(f.relative_to(base))
                contents.append(rel)
                try:
                    text = f.read_text("utf-8", errors="replace")
                    if f.suffix == ".py":
                        py_files[rel] = text
                    else:
                        files[rel] = text
                except Exception:
                    continue

        return {
            "name": base.name,
            "full_name": f"local/{base.name}",
            "description": "Local skill directory",
            "stars": 0,
            "forks": 0,
            "language": "N/A",
            "topics": [],
            "license": "N/A",
            "created": "",
            "updated": "",
            "files": files,
            "py_files": py_files,
            "contents": sorted(contents),
        }

    def _api_get(self, url: str) -> dict:
        """Make a GitHub API GET request."""
        if url in self._cache:
            return self._cache[url]
        req = urllib.request.Request(url, headers={"User-Agent": "auditor/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        self._cache[url] = data
        return data

    def analyze(self, repo_data: dict) -> dict:
        """Execute full 8-dimensional analysis."""
        content = ""
        for fname in ["SKILL.md", "README.md", "CLAUDE.md"]:
            content += repo_data["files"].get(fname, "") + "\n\n"

        combined_py = "\n".join(repo_data.get("py_files", {}).values())
        has_code = bool(repo_data.get("py_files")) or "```python" in content or "```bash" in content
        has_readme = any(k in repo_data["files"] for k in ["SKILL.md", "README.md"])
        has_install = bool(re.search(r"install|pip |npm |git clone|brew ", content, re.I))
        has_examples = bool(re.search(r"example|demo|usage|how to", content, re.I))
        has_help = bool(re.search(r"--help|-h|Usage|usage:", content))
        has_retry = bool(re.search(r"retry|max_retries|backoff", combined_py + content, re.I))
        has_error = bool(re.search(r"try:|except |HTTPError|ConnectionError", combined_py))
        has_gitignore = ".gitignore" in repo_data.get("contents", [])
        has_standalone = any(f.endswith(".py") for f in repo_data.get("contents", []))
        has_comparison = bool(re.search(r"comparison|vs |alternative|versus", content, re.I))
        has_faq = bool(re.search(r"\?\s*\n|FAQ|frequently asked", content, re.I))
        has_pathlib = "Path(" in combined_py or "pathlib" in combined_py or "os.path.join" in combined_py
        has_utf8 = bool(re.search(r"utf-?8|encoding", content + combined_py, re.I))
        has_comments = "# " in combined_py or '"""' in combined_py
        has_config_center = bool(re.search(r"=== config|# config|CONFIG|config\s*=", combined_py + content, re.I))
        has_os_path = "os.path" in combined_py

        scores = {}
        for dim in DIMENSIONS:
            s = 5.0  # baseline
            findings = []
            suggestions = []

            if dim["id"] == "code_quality":
                if has_code: s += 1.0
                if has_retry: s += 1.5
                if has_error: s += 1.0
                if not has_error and not has_retry:
                    suggestions.append("Implement try/except blocks with network retry logic")
                    findings.append("No error handling detected — skill may crash on network failures")
                if has_standalone: s += 0.5
                if combined_py and "***" in combined_py:
                    s -= 2.0
                    findings.append("CRITICAL: Unresolved placeholder '***' found in source code")
                s = max(1.0, min(10.0, s))

            elif dim["id"] == "documentation":
                if has_readme: s += 2.0
                if has_install: s += 1.0
                if has_examples: s += 1.0
                if has_faq: s += 0.5
                if not has_install:
                    suggestions.append("Add installation instructions to README")
                if not has_examples:
                    suggestions.append("Include usage examples with common scenarios")
                if not has_faq:
                    suggestions.append("Add FAQ section addressing common questions")
                s = max(1.0, min(10.0, s))

            elif dim["id"] == "architecture":
                if has_standalone: s += 2.0
                if has_gitignore: s += 1.0
                if has_code: s += 0.5
                if not has_gitignore:
                    suggestions.append("Add .gitignore to exclude generated files and caches")
                if not has_standalone:
                    suggestions.append("Extract scripts into standalone executable files")
                s = max(1.0, min(10.0, s))

            elif dim["id"] == "ux":
                if has_install: s += 1.5
                if has_help: s += 1.5
                if has_examples: s += 1.0
                s = max(1.0, min(10.0, s))
                if not has_help:
                    suggestions.append("Add --help flag or usage documentation")

            elif dim["id"] == "resilience":
                if has_retry: s += 3.0
                if has_error: s += 2.0
                if not has_retry:
                    suggestions.append("Implement exponential backoff retry for API calls")
                if not has_error:
                    suggestions.append("Add try/except blocks around network operations")
                s = max(1.0, min(10.0, s))

            elif dim["id"] == "portability":
                if has_pathlib or has_os_path: s += 1.5
                if has_utf8: s += 1.5
                if has_standalone: s += 0.5
                if not has_pathlib and not has_os_path:
                    suggestions.append("Use pathlib or os.path.join for cross-platform paths")
                if not has_utf8:
                    suggestions.append("Specify UTF-8 encoding to avoid Windows encoding issues")
                s = max(1.0, min(10.0, s))

            elif dim["id"] == "maintainability":
                if has_comments: s += 2.0
                if has_config_center: s += 2.0
                if not has_comments:
                    suggestions.append("Add docstrings and inline comments to explain logic")
                if not has_config_center:
                    suggestions.append("Centralize configuration constants at module top")
                s = max(1.0, min(10.0, s))

            elif dim["id"] == "innovation":
                stars = repo_data.get("stars", 0)
                if stars >= 100: s = 8.0
                elif stars >= 10: s = 6.5
                elif stars >= 1: s = 5.5
                if has_comparison: s += 1.5
                if repo_data.get("description"): s += 0.5
                if not has_comparison:
                    suggestions.append("Add comparison table showing advantages over alternatives")
                s = max(1.0, min(10.0, s))

            scores[dim["id"]] = {
                "name": dim["name"],
                "score": round(s, 1),
                "weight": dim["weight"],
                "weighted": round(s * dim["weight"], 1),
                "description": dim["description"],
                "checks": dim["checks"],
            }

        total_weighted = sum(s["weighted"] for s in scores.values())
        total_weight = sum(d["weight"] for d in DIMENSIONS)
        total = round(total_weighted / total_weight, 1)

        # Grade
        if total >= 9.0: grade, label = "S", "Exemplary"
        elif total >= 8.0: grade, label = "A", "Excellent"
        elif total >= 7.0: grade, label = "B", "Good"
        elif total >= 6.0: grade, label = "C", "Fair"
        elif total >= 4.0: grade, label = "D", "Poor"
        else: grade, label = "F", "Failing"

        # Collect all suggestions
        all_suggestions = []
        seen = set()
        for dim in DIMENSIONS:
            s_data = scores[dim["id"]]
            # Generate suggestions based on score
            if s_data["score"] < 6:
                all_suggestions.append(f"[{dim['name']}] Score {s_data['score']}/10 — needs significant improvement")
            elif s_data["score"] < 8:
                all_suggestions.append(f"[{dim['name']}] Score {s_data['score']}/10 — room for improvement")

        if repo_data.get("stars", 0) == 0:
            all_suggestions.append("[Visibility] Repository has no stars — consider promoting on social platforms")

        if not repo_data.get("topics"):
            all_suggestions.append("[SEO] No GitHub topics set — add relevant tags for discoverability")

        all_suggestions.append("[Recommendation] Run auditor again after applying fixes to track progress")

        return {
            "scores": scores,
            "total_score": total,
            "grade": grade,
            "grade_label": label,
            "suggestions": all_suggestions,
            "repo_data": repo_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
            "version": __version__,
        }


# ─── Report Generators ──────────────────────────────────────────────────────

def generate_terminal_report(result: dict):
    """Generate a beautiful terminal report."""
    r = result["repo_data"]
    scores = result["scores"]

    sep = "=" * 54
    print(f"\n{sep}")
    print(f"  CLAUDE SKILL AUDITOR — Analysis Report")
    print(f"  {r['full_name']}")
    print(f"{sep}")
    print(f"  Repository:   {r.get('description', 'N/A')[:60]}")
    print(f"  Stars:        {r.get('stars', 0)}  |  Language: {r.get('language', 'N/A')}")
    print(f"  Files:        {len(r.get('contents', []))}  |  Created: {r.get('created', 'N/A')}")
    print()

    for dim in DIMENSIONS:
        s = scores[dim["id"]]
        bar_len = int(s["score"])
        bar = "█" * bar_len + "░" * (10 - bar_len)
        print(f"  {dim['name']:<20s} [{bar}] {s['score']}/10  (w:{dim['weight']})")

    print()
    total = result["total_score"]
    grade = result["grade"]
    bar_total = "█" * int(total) + "░" * (10 - int(total))
    print(f"  {'TOTAL':<20s} [{bar_total}] {total}/10  Grade: {grade}")
    print(f"{sep}\n")

    if result["suggestions"]:
        print("  KEY FINDINGS & RECOMMENDATIONS:")
        for i, sug in enumerate(result["suggestions"][:5], 1):
            print(f"    {i}. {sug}")
        print()

    print(f"  Generated by Claude Skill Auditor v{result['version']}")
    print(f"  {result['timestamp']}")
    print(f"{sep}\n")


def generate_html_report(result: dict) -> str:
    """Generate a polished, dark-themed HTML report."""
    r = result["repo_data"]
    scores = result["scores"]
    total = result["total_score"]
    grade = result["grade"]

    # Score color
    def c(s):
        if s >= 8: return "#00e676"
        if s >= 6: return "#ffc107"
        if s >= 4: return "#ff9800"
        return "#ef5350"

    grade_colors = {"S": "#FFD700", "A": "#00e676", "B": "#42a5f5", "C": "#ffc107", "D": "#ff9800", "F": "#ef5350"}

    # Dimension rows
    rows = ""
    for dim in DIMENSIONS:
        s = scores[dim["id"]]
        color = c(s["score"])
        bar_w = int(s["score"] * 10)
        rows += f"""
        <tr>
            <td style="padding:12px 16px;color:#e0e0e0;font-weight:600;border-bottom:1px solid #2a2a4a;">{dim["name"]}</td>
            <td style="padding:12px 16px;color:#888;font-size:13px;border-bottom:1px solid #2a2a4a;">{dim["description"][:60]}</td>
            <td style="padding:12px 16px;border-bottom:1px solid #2a2a4a;">
                <div style="background:#2a2a4a;border-radius:10px;height:22px;overflow:hidden;">
                    <div style="background:{color};width:{bar_w}%;height:100%;border-radius:10px;"></div>
                </div>
            </td>
            <td style="padding:12px 16px;font-weight:700;text-align:center;color:{color};border-bottom:1px solid #2a2a4a;">{s["score"]}</td>
        </tr>"""

    # File tags
    files_html = ""
    for f in r.get("contents", []):
        icon = "📄"
        if f.endswith(".py"): icon = "🐍"
        elif f.endswith(".md"): icon = "📝"
        elif f.endswith(".json"): icon = "📋"
        elif f.startswith("."): icon = "⚙️"
        files_html += f'<span style="background:#1a1a3e;color:#aaa;padding:4px 14px;border-radius:20px;margin:4px;display:inline-block;font-size:13px;border:1px solid #2a2a4a;">{icon} {f}</span>'

    # Suggestions
    sug_html = ""
    for i, sug in enumerate(result["suggestions"][:8], 1):
        sug_html += f'<li style="margin:10px 0;color:#ccc;font-size:14px;line-height:1.5;">🔍 <strong style="color:#fff;">{i}.</strong> {sug}</li>'

    # Metadata
    topics = ", ".join(r.get("topics", [])) or "<em>none</em>"
    meta = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div><span style="color:#666;">Repository</span><br/><span style="color:#eee;">{r["full_name"]}</span></div>
        <div><span style="color:#666;">Stars</span><br/><span style="color:#FFD700;">⭐ {r.get("stars", 0)}</span></div>
        <div><span style="color:#666;">Language</span><br/><span style="color:#eee;">{r.get("language", "N/A")}</span></div>
        <div><span style="color:#666;">License</span><br/><span style="color:#eee;">{r.get("license", "N/A")}</span></div>
        <div style="grid-column:span 2;"><span style="color:#666;">Topics</span><br/><span style="color:#64B5F6;">{topics}</span></div>
        <div style="grid-column:span 2;"><span style="color:#666;">Description</span><br/><span style="color:#999;font-size:13px;">{r.get("description", "N/A")[:120]}</span></div>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skill Audit - {r["full_name"]}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Inter',sans-serif; background:#0f0f23; color:#ccc; }}
.container {{ max-width:860px; margin:0 auto; padding:24px; }}
.glass {{ background:rgba(22,22,50,0.85); backdrop-filter:blur(12px); border:1px solid #2a2a4a; border-radius:20px; padding:28px; margin:20px 0; }}
.badge {{ display:inline-flex; align-items:center; gap:8px; background:#1a1a3e; padding:6px 16px; border-radius:20px; font-size:13px; color:#888; border:1px solid #2a2a4a; }}
</style>
</head>
<body>
<div class="container">

    <!-- Header -->
    <div style="text-align:center;padding:30px 0 10px;">
        <div style="font-size:13px;color:#666;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Claude Skill Auditor</div>
        <h1 style="font-size:26px;color:#fff;font-weight:700;">{r["full_name"]}</h1>
        <div style="color:#888;font-size:14px;margin-top:6px;">{r.get("description", "")[:80]}</div>
        <div style="margin:20px 0;">
            <span class="badge">🔍 v{result["version"]}</span>
            <span class="badge">📅 {result["timestamp"][:10]}</span>
            <span class="badge">📂 {len(r.get("contents", []))} files</span>
        </div>
        <div style="display:inline-block;width:90px;height:90px;line-height:90px;border-radius:50%;text-align:center;font-size:40px;font-weight:800;
            background:{grade_colors.get(grade, '#888')}15;color:{grade_colors.get(grade, '#888')};border:3px solid {grade_colors.get(grade, '#888')};
            margin:10px 0;">{grade}</div>
        <div style="font-size:48px;font-weight:300;color:#fff;margin:5px 0;">{total}<span style="font-size:24px;color:#666;">/10</span></div>
    </div>

    <!-- Metadata -->
    <div class="glass">
        <div style="font-size:16px;font-weight:600;color:#fff;margin-bottom:16px;">📋 Repository Overview</div>
        {meta}
    </div>

    <!-- File Structure -->
    <div class="glass">
        <div style="font-size:16px;font-weight:600;color:#fff;margin-bottom:16px;">📁 File Structure</div>
        <div>{files_html}</div>
    </div>

    <!-- Score Matrix -->
    <div class="glass">
        <div style="font-size:16px;font-weight:600;color:#fff;margin-bottom:16px;">📊 8-Dimension Score Matrix</div>
        <table style="width:100%;border-collapse:collapse;">
            <tr><th style="text-align:left;padding:10px 16px;color:#666;font-weight:500;border-bottom:2px solid #2a2a4a;">Dimension</th>
                <th style="text-align:left;padding:10px 16px;color:#666;font-weight:500;border-bottom:2px solid #2a2a4a;">Focus</th>
                <th style="padding:10px 16px;color:#666;font-weight:500;border-bottom:2px solid #2a2a4a;">Score</th>
                <th style="text-align:center;padding:10px 16px;color:#666;font-weight:500;border-bottom:2px solid #2a2a4a;">Value</th></tr>
            {rows}
            <tr>
                <td colspan="4" style="padding:16px;text-align:center;">
                    <span style="font-size:18px;font-weight:600;color:#fff;">Weighted Total: </span>
                    <span style="font-size:22px;font-weight:700;color:{c(total)};">{total}/10</span>
                    <span style="margin-left:16px;font-size:18px;font-weight:600;color:#fff;">Grade: </span>
                    <span style="font-size:22px;font-weight:700;color:{grade_colors.get(grade, '#888')};">{grade}</span>
                </td>
            </tr>
        </table>
    </div>

    <!-- Recommendations -->
    <div class="glass">
        <div style="font-size:16px;font-weight:600;color:#fff;margin-bottom:16px;">🎯 Recommendations</div>
        <ol style="padding-left:20px;">{sug_html}</ol>
    </div>

    <!-- Footer -->
    <div style="text-align:center;padding:30px;color:#444;font-size:12px;">
        Generated by <strong style="color:#666;">Claude Skill Auditor</strong> v{result['version']} · {result["timestamp"]}
    </div>
</div>
</body>
</html>"""


# ─── CLI Entry Point ─────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Claude Skill Auditor — 8-Dimensional Skill Analysis Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python auditor.py https://github.com/user/skill-repo
              python auditor.py /path/to/local/skill --html -o report.html
              python auditor.py https://github.com/user/skill-repo --quiet
        """),
    )
    parser.add_argument("target", nargs="?", help="GitHub URL or local path")
    parser.add_argument("--html", "-H", action="store_true", help="Generate HTML report")
    parser.add_argument("--output", "-o", default="skill-audit-report.html", help="HTML output path")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress terminal report")
    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    if not args.target:
        parser.print_help()
        return

    auditor = SkillAuditor(verbose=not args.quiet)

    # Fetch
    is_url = "github.com" in args.target
    source_type = "GitHub" if is_url else "local"
    print(f"🔍 Connecting to {source_type} source: {args.target}")
    print(f"📦 Fetching repository data...")

    try:
        if is_url:
            data = auditor.fetch_from_github(args.target)
        else:
            data = auditor.fetch_from_local(args.target)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print(f"✅ Retrieved {len(data.get('contents', []))} files, {len(data.get('py_files', {}))} Python scripts")
    print()

    # Analyze
    print("⚙️  Running 8-dimensional analysis...")
    result = auditor.analyze(data)
    print(f"✅ Analysis complete — Score: {result['total_score']}/10  Grade: {result['grade']}")
    print()

    # Terminal report
    if not args.quiet:
        generate_terminal_report(result)

    # HTML report
    if args.html:
        html = generate_html_report(result)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📄 HTML report saved: {args.output}")

    print(f"✨ Audit complete.")


if __name__ == "__main__":
    main()
