"""
AI service layer using the Anthropic SDK.
Implemented in Phase 4 — AI Features.

All AI calls are executed as Celery tasks (never blocking the HTTP cycle).
"""
