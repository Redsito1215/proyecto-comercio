# Implementation Plan: Pagos y seguridad

Flask y MongoDB implementan usuarios, sesiones opacas, RBAC, auditoría y pagos mediante un
adaptador sandbox. Werkzeug provee derivación de contraseñas; `secrets` y SHA-256 protegen
tokens de sesión. La interfaz responsive aplica los permisos efectivos tanto a la navegación
como a cada acción, mientras el backend conserva la autorización definitiva. Los pagos en
efectivo se concilian transaccionalmente con la caja abierta.

## Constitution Check
- PASS: mínimo privilegio, no almacenamiento de tarjeta, idempotencia, auditoría, transacciones y pruebas.

## Structure
`backend/modules/security/`, `backend/modules/payments/`, `frontend/js/modules/security/`, `tests/{unit,contract,integration}/`.
