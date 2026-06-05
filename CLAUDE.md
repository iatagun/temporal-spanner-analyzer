# temporal-spanner-analyzer

This project implements Baligács (2026) "Temporal Cliques Admit Linear Spanners".
CSV → PMI graph → maximal cliques → linear spanner (≤7n) → trends/comparison.

## Skill

Use the project-specific skill for conventions, architecture, bug history, and standards:

`.opencode/skills/temporal-spanner-analyzer/SKILL.md`

Load it with:

`/skill temporal-spanner-analyzer`

## Quick Commands

```bash
# Start backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Start frontend (separate terminal)
cd frontend && npm run dev

# Run tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_integration.py -v -k test_upload
```
