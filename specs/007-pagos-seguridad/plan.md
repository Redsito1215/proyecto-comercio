# Implementation Plan: Pagos y seguridad

Flask y MongoDB implementarán usuarios, sesiones opacas, RBAC, auditoría y pagos mediante un adaptador sandbox. Werkzeug proveerá derivación de contraseñas; `secrets` y SHA-256 protegerán tokens de sesión. La interfaz seguirá el dock Altavia.

## Constitution Check
- PASS: mínimo privilegio, no almacenamiento de tarjeta, idempotencia, auditoría, transacciones y pruebas.

## Structure
`backend/modules/security/`, `backend/modules/payments/`, `frontend/js/modules/security/`, `tests/{unit,contract,integration}/`.
