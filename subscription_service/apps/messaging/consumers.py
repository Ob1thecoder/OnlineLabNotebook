"""
Redis Streams event consumer for subscription_service.

Events consumed from logbook_service:
  - user.registered
  - entry.submitted
  - pdf.export.requested
  - ai.assist.requested
  - seat.invite.sent

Events published to logbook_service:
  - plan.upgraded
  - plan.downgraded
  - plan.cancelled
  - seat.limit.reached
  - payment.failed

Implemented once Redis Streams or SQS integration is configured (Phase 2+).
"""
