# Data Model: Pagos y seguridad

## Tablas lógicas MongoDB
- `users`: name, email_normalized, password_hash, role_ids, status, failed_attempts, locked_until, created_at.
- `roles`: code, name, permissions, system.
- `auth_sessions`: user_id, token_hash, expires_at, revoked_at, created_at.
- `audit_events`: actor_id, action, entity_type/id, outcome, metadata_sanitized, occurred_at.
- `payments`: sale_id, method, amount, status, provider, provider_reference, method_ref, brand, last4, idempotency_key, actor_id, timestamps.
- `refunds`: payment_id, amount, status, idempotency_key, provider_reference, actor_id, created_at.

## Índices
- Email y códigos de rol únicos.
- Hash de sesión único con TTL por expiración.
- Claves de idempotencia únicas en pagos y reembolsos.
