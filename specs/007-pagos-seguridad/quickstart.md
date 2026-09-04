# Quickstart: Pagos y seguridad

1. Cree el primer administrador por `/api/v1/security/bootstrap` si no existen usuarios.
2. Inicie sesión y use `Authorization: Bearer <token>` fuera de desarrollo.
3. Cree un pago con token sandbox (`tok_approved_*` o `tok_declined_*`) y una clave de idempotencia.
4. Confirme que la respuesta indica proveedor `local-sandbox`, nunca un adquirente real.
5. Consulte auditoría en **Seguridad**.
