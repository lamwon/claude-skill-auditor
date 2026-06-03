# -*- coding: utf-8 -*-
"""Generate example report for README showcase"""
import sys, json
sys.path.insert(0, "D:\\Hermes\\claude-skill-auditor")
from auditor import generate_html_report

# Mock data for a hypothetical well-polished skill
repo_data = {
    "full_name": "user/example-rag-skill",
    "description": "Retrieval-Augmented Generation skill for Claude Code with ChromaDB integration",
    "stars": 342,
    "forks": 18,
    "language": "Python",
    "topics": ["rag", "chromadb", "claude-code", "retrieval", "embeddings", "vector-search"],
    "license": "MIT",
    "created": "2025-08-15",
    "updated": "2026-05-20",
    "contents": [".gitignore", "README.md", "SKILL.md", "rag_skill.py", "embeddings.py", "config.yaml", "examples/", "tests/"],
}

scores = {
    "code_quality": {"name": "Code Integrity", "score": 9.5, "weight": 1.0, "weighted": 9.5, "description": "Syntax correctness, error handling, security", "checks": []},
    "documentation": {"name": "Documentation", "score": 8.5, "weight": 1.0, "weighted": 8.5, "description": "README/SKILL.md completeness", "checks": []},
    "architecture": {"name": "Architecture", "score": 8.0, "weight": 0.8, "weighted": 6.4, "description": "File structure, dependencies", "checks": []},
    "ux": {"name": "User Experience", "score": 8.5, "weight": 0.9, "weighted": 7.65, "description": "Install ease, output clarity", "checks": []},
    "resilience": {"name": "Resilience", "score": 9.0, "weight": 0.8, "weighted": 7.2, "description": "Retry logic, rate limiting", "checks": []},
    "portability": {"name": "Cross-Platform", "score": 7.5, "weight": 0.6, "weighted": 4.5, "description": "Cross-platform compatibility", "checks": []},
    "maintainability": {"name": "Maintainability", "score": 8.0, "weight": 0.6, "weighted": 4.8, "description": "Comments, config, versioning", "checks": []},
    "innovation": {"name": "Innovation & Value", "score": 8.5, "weight": 0.5, "weighted": 4.25, "description": "Unique value proposition", "checks": []},
}

result = {
    "scores": scores,
    "total_score": 8.4,
    "grade": "A",
    "grade_label": "Excellent",
    "suggestions": [
        "[Documentation] Score 8.5/10 — add video demo or GIF walkthrough",
        "[Cross-Platform] Score 7.5/10 — verify Windows compatibility with pathlib",
        "[Architecture] Score 8.0/10 — consider adding pytest test suite",
        "[Recommendation] Add GitHub Actions CI badge for test coverage",
        "[Recommendation] Run auditor again after applying fixes to track progress",
    ],
    "repo_data": repo_data,
    "timestamp": "2026-06-02 16:30 UTC",
    "version": "1.0.0",
}

html = generate_html_report(result)
with open("D:\\Hermes\\claude-skill-auditor\\examples\\example-audit-report.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"Example report generated: {len(html)} bytes")
