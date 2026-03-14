"""
Celery tasks for AI features.
Implemented in Phase 4 — AI Features.
"""
from config.celery import app


@app.task(bind=True, queue="ai", max_retries=3)
def writing_assist_task(self, entry_id: str, notes: str) -> dict:
    """Stub — full implementation in Phase 4."""
    raise NotImplementedError


@app.task(bind=True, queue="ai", max_retries=3)
def completeness_check_task(self, entry_id: str) -> dict:
    """Stub — full implementation in Phase 4."""
    raise NotImplementedError


@app.task(bind=True, queue="ai", max_retries=3)
def generate_report_task(self, entry_ids: list[str]) -> dict:
    """Stub — full implementation in Phase 4."""
    raise NotImplementedError
