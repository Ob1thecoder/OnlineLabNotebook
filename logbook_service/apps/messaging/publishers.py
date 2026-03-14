"""
Redis Streams event publishers for logbook_service → subscription_service.

Events published:
  - user.registered
  - entry.submitted
  - pdf.export.requested
  - ai.assist.requested
  - seat.invite.sent

Implemented once Redis Streams or SQS integration is configured (Phase 2+).
"""
