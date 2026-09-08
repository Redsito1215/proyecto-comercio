# Modelo de datos: Pagos y seguridad

## Tablas lógicas MongoDB
- `users`: name, email_normalized, password_hash, roles (códigos), status, failed_attempts, locked_until, created_at.
- `roles`: code, name, permissions, system.
- `auth_sessions`: user_id, token_hash, expires_at, revoked_at, created_at.
- `audit_events`: actor_id, action, entity_type/id, outcome, metadata sanitizada antes de persistir, occurred_at.
- `payments`: sale_id, method, amount, status, provider, provider_reference, method_ref, brand, last4, idempotency_key, actor_id, timestamps.
- `refunds`: payment_id, amount, status, idempotency_key, provider_reference, actor_id, created_at.
- `settings`: clave única, valor validado, actor y fechas de modificación.

Los pagos en efectivo aprobados referencian una sesión abierta y originan exactamente un
movimiento `sale` en `cash_movements`; la clave de origen impide duplicarlo.

## Índices
- Email y códigos de rol únicos.
- Hash de sesión único con TTL por expiración.
- Claves de idempotencia únicas en pagos y reembolsos.
- Clave única de origen para movimientos de caja asociados a pagos.

## Relaciones y reglas

- Un usuario puede tener varios roles y sesiones; una sesión revocada o vencida no autoriza solicitudes.
- Los roles del sistema mantienen código único y conjunto explícito de permisos.
- Un pago referencia una venta, no supera su saldo pendiente y no almacena PAN ni CVV.
- Un reembolso pertenece a un pago aprobado y no puede superar el importe reembolsable.
- Los eventos de auditoría sanitizan metadatos antes de persistirlos.

## Ciclos de vida

Usuarios y sesiones pueden activarse, bloquearse o revocarse sin borrar su historia. Pagos y reembolsos conservan el resultado recibido. La configuración mantiene actor y fechas de modificación para reconstruir cambios administrativos.
