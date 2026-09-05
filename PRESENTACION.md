# Guía de presentación — Comercio Inteligente

## Objetivo

Demostrar que un comercio puede cobrar rápido, controlar inventario y márgenes, conocer a sus
clientes, anticipar demanda, personalizar promociones y reducir pérdidas sin sacrificar
seguridad ni trazabilidad.

## Arquitectura que debe explicarse

- **Frontend responsive**: experiencia única para operación, inteligencia y gestión.
- **Flask**: API REST modular con validación, errores uniformes y permisos en servidor.
- **MongoDB replica set**: operación transaccional, inventario, ventas y auditoría.
- **Airflow**: ejecución horaria del proceso analítico.
- **ClickHouse**: consultas históricas y agregaciones para informes.
- **ReportLab**: generación de PDF desde una instantánea auditable.
- **Docker Compose**: arranque reproducible de todos los componentes.

## Recorrido recomendado (12–15 minutos)

1. **Acceso y resumen (1 min)**: iniciar sesión y explicar RBAC, sesiones opacas y bloqueo.
2. **Gestión (2 min)**: mostrar categorías, proveedores, sucursales, usuarios y configuración.
3. **Inventario y compra (2 min)**: enseñar stock, lotes, vencimientos y una orden de compra.
4. **Venta y pago (2 min)**: buscar un producto, confirmar la venta y cobrar con token sandbox.
5. **Cliente (1 min)**: abrir un perfil y explicar recurrencia, rentabilidad y abandono individual.
6. **Precio y demanda (2 min)**: mostrar margen, comparación competitiva y pronóstico explicable.
7. **Promoción (1 min)**: demostrar protección de margen, consentimiento y grupo control.
8. **Caja y merma (1 min)**: mostrar arqueo, diferencias y señales que no presuponen fraude.
9. **Informe (2 min)**: previsualizar varias secciones y generar el PDF.
10. **Analítica (1 min)**: abrir Airflow, enseñar el DAG y confirmar ClickHouse disponible.

## Preparación antes de exponer

```powershell
cd C:\examenfinal\proyecto-comercio-inteligente
docker compose --profile analytics up -d --build
docker compose --profile tools run --rm seed
docker compose ps
```

Abrir:

- Aplicación: `http://127.0.0.1:5001`
- Airflow: `http://127.0.0.1:8088`

Las credenciales del administrador comercial se crean en **Primera instalación** y no deben
guardarse en Git. Las credenciales locales de Airflow se consultan con:

```powershell
docker compose logs airflow --tail 300 | Select-String "Login with username"
```

## Evidencias técnicas

- 7 paquetes Spec Kit, de `001` a `007`, sin un Spec adicional.
- 72 pruebas automatizadas: 28 unitarias, 25 de contrato y 19 de integración.
- Flujo integral automatizado: cliente → venta → inventario → caja → pago → PDF.
- No se persisten PAN, CVV ni tokens completos de tarjeta.
- Idempotencia en ventas, pagos, movimientos y recepciones.
- Auditoría para accesos, cambios sensibles, pagos e informes.

## Respuestas breves para preguntas frecuentes

**¿Por qué MongoDB?** Permite documentos flexibles para los módulos comerciales y usa
transacciones al ejecutarse como replica set.

**¿Por qué ClickHouse además de MongoDB?** MongoDB conserva la operación; ClickHouse separa
las consultas analíticas para no degradar la caja ni el inventario.

**¿Por qué Airflow?** Hace visible, repetible y auditable la carga desde la base operativa hacia
la analítica.

**¿El pronóstico compra automáticamente?** No. Presenta incertidumbre y explicaciones; la
decisión final permanece en una persona autorizada.

**¿Los pagos son reales?** No. El adaptador es sandbox y demuestra tokenización sin manejar
datos completos de tarjetas. Para producción se sustituye por una pasarela certificada.

## Cierre sugerido

El sistema conecta la operación diaria con decisiones explicables: cada venta actualiza
inventario, cada interacción mejora el conocimiento del cliente, cada riesgo conserva evidencia
y cada informe puede rastrearse hasta su instantánea original.
