# Quickstart: Clientes y fidelización

1. Levantar `docker compose up -d --build`.
2. Crear dos clientes con consentimiento distinto.
3. Asociar ventas frecuentes y una venta grande aislada.
4. Recalcular métricas y comprobar explicación de segmentos.
5. Simular retraso respecto del intervalo habitual.
6. Generar cupón de cumpleaños; verificar que el cliente sin consentimiento no recibe notificación.
7. Ejecutar las unitarias sin modificar `MONGO_DB`; limpiar exclusivamente
   `comercio_inteligente_test` y ejecutar allí contratos e integraciones.
