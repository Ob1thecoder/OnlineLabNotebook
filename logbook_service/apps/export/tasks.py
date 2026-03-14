"""
Celery tasks for PDF export with timestamp certificate and SHA-256 hash.
Implemented in Phase 5 — Compliance & Export.
"""
from config.celery import app


@app.task(bind=True, queue="export", max_retries=3)
def generate_pdf_task(self, entry_id: str, user_id: str) -> dict:
    """
    Generates a tamper-evident PDF for an entry.
    Stub — full implementation in Phase 5.
    """
    raise NotImplementedError
