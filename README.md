# Comercio Inteligente

Sistema integral para ventas rápidas, inventario por lotes, clientes, precios, pronóstico, promociones, caja, mermas, pagos tokenizados, seguridad e informes.

## Arquitectura

- Flask/Python 3.12 para API y frontend estático.
- MongoDB 8 con replica set para operación y transacciones.
- ClickHouse para hechos e instantáneas analíticas.
- Airflow para la carga horaria MongoDB -> ClickHouse.
- ReportLab para informes PDF auditables.
- Docker Compose para todos los servicios.

La documentación funcional sigue GitHub Spec Kit en `.specify/` y `specs/001` a `specs/007`.

## Inicio rápido

1. Copie `.env.example` como `.env` y cambie `FLASK_SECRET_KEY`.
2. Inicie la aplicación:

   `docker compose up -d --build`

3. Cargue el catálogo inicial idempotente:

   `docker compose --profile tools run --rm seed`

4. Abra `http://127.0.0.1:5001`.

## Perfil analítico

Inicie ClickHouse y Airflow:

`docker compose --profile analytics up -d --build`

- ClickHouse HTTP: `http://127.0.0.1:8123`
- Airflow: `http://127.0.0.1:8088`
- DAG: `comercio_inteligente_etl`, programado cada hora.
- Las credenciales iniciales de Airflow aparecen una vez en `docker compose logs airflow`.

El perfil `analytics` es opcional para la operación diaria y obligatorio para la analítica histórica. Los informes operativos siguen disponibles si ClickHouse está temporalmente fuera de línea.

## Informes

La pantalla **Informes** permite combinar ventas, inventario, márgenes, clientes, mermas, pagos y pronósticos. Primero presenta una vista previa y después genera el PDF desde una instantánea almacenada en `report_runs` y registrada en auditoría.

## Pagos

El adaptador incluido es `local-sandbox`. Acepta tokens de prueba `tok_approved_*` y `tok_declined_*`; no procesa tarjetas reales. El sistema rechaza campos PAN/CVV y no persiste el token completo.

## Pruebas

- Unitarias y contrato:

  `docker compose exec -T backend pytest tests/unit tests/contract -q`

- Integración en base aislada:

  `docker compose exec -T -e MONGO_DB=comercio_inteligente_test backend pytest tests/integration -q`

Las pruebas destructivas verifican que la base termine en `_test` antes de limpiar colecciones.

## Preparación de producción

- Configure `APP_ENV=production`, secretos reales y HTTPS en el proxy.
- Sustituya `local-sandbox` por un proveedor certificado que entregue tokens.
- Use PostgreSQL para metadatos de Airflow si el despliegue deja de ser local.
- Configure respaldos, rotación de secretos, monitoreo y retención de auditoría.
