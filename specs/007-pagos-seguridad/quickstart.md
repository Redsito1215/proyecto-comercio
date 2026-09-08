# Guía rápida: Pagos y seguridad

1. Consulte `/api/v1/security/bootstrap/status`; cree el administrador inicial únicamente si está habilitado.
2. Inicie sesión y use `Authorization: Bearer <token>`; compruebe los permisos efectivos devueltos.
3. Cree roles y usuarios desde **Gestión** y verifique que navegación y acciones respetan sus permisos.
4. Para efectivo, abra primero una caja en la ubicación de la venta. Para medios electrónicos use
   un token sandbox (`tok_approved_*` o `tok_declined_*`) y una clave de idempotencia.
5. Repita la misma solicitud y confirme que no se duplica el pago ni el movimiento de efectivo.
6. Consulte y filtre la auditoría en **Seguridad**, y descargue su PDF.
7. Previsualice un informe compuesto en **Informes** y genere el PDF auditable.
8. Ejecute las unitarias con `docker compose exec -T backend pytest -q tests/unit`. Después
   limpie exclusivamente `comercio_inteligente_test` y ejecute allí `tests/contract` y
   `tests/integration`. Nunca apunte pruebas destructivas a la base operativa.
