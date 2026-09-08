# Tareas: Núcleo de ventas e inventario

**Entrada**: Documentos de `specs/001-core-ventas-inventario/`

## Fase 1: Preparación

- [X] T001 Crear paquetes y archivos base según `specs/001-core-ventas-inventario/plan.md`
- [X] T002 Configurar dependencias Python en `requirements.txt`
- [X] T003 [P] Configurar variables documentadas en `.env.example`
- [X] T004 [P] Definir servicios MongoDB replica set y backend en `docker-compose.yml`
- [X] T005 [P] Crear imagen reproducible en `Dockerfile`

## Fase 2: Fundamentos

- [X] T006 Crear configuración validada en `backend/config.py`
- [X] T007 Crear conexión, transacciones y health check en `backend/db.py`
- [X] T008 [P] Crear errores JSON comunes en `backend/common/errors.py`
- [X] T009 [P] Crear serialización Decimal128/fechas en `backend/common/serialization.py`
- [X] T010 [P] Crear autorización mínima en `backend/auth/decorators.py`
- [X] T011 Crear índices y validadores en `backend/modules/core/indexes.py`
- [X] T012 Crear aplicación y registro modular en `backend/app.py`
- [X] T013 [P] Probar configuración y decimales en `tests/unit/test_common.py`

## Fase 3: Historia de usuario 1 - Cobrar rápidamente (P1) MVP

**Prueba independiente**: vender dos productos y verificar un único descuento de inventario.

- [X] T014 [P] [US1] Escribir contrato de productos/ventas en `tests/contract/test_sales_api.py`
- [X] T015 [P] [US1] Escribir concurrencia e idempotencia en `tests/integration/test_sale_transaction.py`
- [X] T016 [P] [US1] Implementar esquemas de venta en `backend/modules/core/schemas.py`
- [X] T017 [US1] Implementar repositorios de producto y venta en `backend/modules/core/repositories.py`
- [X] T018 [US1] Implementar confirmación transaccional en `backend/modules/core/services.py`
- [X] T019 [US1] Exponer productos y ventas en `backend/modules/core/routes.py`
- [X] T020 [P] [US1] Crear pantalla de venta rápida en `frontend/js/modules/core/sales.js`
- [X] T021 [US1] Integrar venta rápida en `frontend/index.html`

## Fase 4: Historia de usuario 2 - Inventario por lote (P1)

**Prueba independiente**: recibir dos lotes y comprobar salida FEFO y alertas.

- [X] T022 [P] [US2] Escribir pruebas FEFO en `tests/unit/test_lot_allocation.py`
- [X] T023 [P] [US2] Escribir integración de recepción en `tests/integration/test_inventory_receipt.py`
- [X] T024 [US2] Implementar lotes, movimientos y alertas en `backend/modules/core/services.py`
- [X] T025 [US2] Exponer inventario y alertas en `backend/modules/core/routes.py`
- [X] T026 [P] [US2] Crear inventario visual en `frontend/js/modules/core/inventory.js`

## Fase 5: Historia de usuario 3 - Reposición (P2)

**Prueba independiente**: recibir parcialmente una orden y conciliar su saldo.

- [X] T027 [P] [US3] Escribir contrato de compras en `tests/contract/test_purchases_api.py`
- [X] T028 [P] [US3] Escribir integración parcial en `tests/integration/test_partial_receipt.py`
- [X] T029 [US3] Implementar órdenes, cobertura y recepción en `backend/modules/core/services.py`
- [X] T030 [US3] Exponer compras en `backend/modules/core/routes.py`
- [X] T031 [P] [US3] Crear UI de compras en `frontend/js/modules/core/purchases.js`

## Fase 6: Historia de usuario 4 - Conteos y ventas perdidas (P2)

**Prueba independiente**: aprobar diferencia y registrar demanda no atendida.

- [X] T032 [P] [US4] Escribir pruebas de conteo en `tests/integration/test_stock_count.py`
- [X] T033 [US4] Implementar conteos y ajustes en `backend/modules/core/services.py`
- [X] T034 [US4] Implementar ventas perdidas en `backend/modules/core/routes.py`
- [X] T035 [P] [US4] Crear UI de conteos en `frontend/js/modules/core/counts.js`

## Fase 7: Historia de usuario 5 - Devoluciones (P3)

**Prueba independiente**: separar devuelto apto y dañado y comprobar destinos.

- [X] T036 [P] [US5] Escribir pruebas de límites en `tests/unit/test_return_limits.py`
- [X] T037 [P] [US5] Escribir integración en `tests/integration/test_return_transaction.py`
- [X] T038 [US5] Implementar devolución transaccional en `backend/modules/core/services.py`
- [X] T039 [US5] Exponer devolución en `backend/modules/core/routes.py`
- [X] T040 [P] [US5] Crear UI de devoluciones en `frontend/js/modules/core/returns.js`

## Fase 8: Pulido y controles de calidad

- [X] T041 [P] Aplicar diseño base de Altavia en `frontend/css/app.css`
- [X] T042 [P] Añadir accesibilidad y responsividad en `frontend/css/app.css`
- [X] T043 Ejecutar pruebas y corregir regresiones documentadas en `tests/`
- [X] T044 Ejecutar escenarios de `specs/001-core-ventas-inventario/quickstart.md`
- [X] T045 Verificar trazabilidad FR→prueba en `specs/001-core-ventas-inventario/checklists/requirements.md`

## Dependencias

Preparación → Fundamentos → HU1. Después de Fundamentos, HU2 y HU3 pueden desarrollarse en
paralelo; US4 necesita movimientos y US5 necesita ventas e inventario. Polish depende de las
historias elegidas para la entrega.

## Estrategia de implementación

El MVP comprende T001–T021. Cada historia se valida independientemente antes de continuar.
Las tareas `[P]` modifican archivos distintos o son pruebas que pueden prepararse en paralelo.

- [x] T-G01 Exponer la administración de categorías, proveedores y ubicaciones desde Gestión.
- [x] T-G02 Añadir contratos y validaciones para catálogos operativos reutilizables.
- [X] T046 Validar el flujo comercial completo desde una base vacía.
- [X] T047 Cubrir atomicidad, idempotencia y reglas negativas de stock, caja, devolución y merma.
- [X] T048 Migrar índices únicos opcionales y números de venta sin bloquear documentos históricos.
- [X] T049 Exponer movimientos de inventario con producto, origen, actor y filtros.
- [X] T050 Añadir la vista responsive de movimientos dentro de Inventario y compras.
- [X] T051 Cubrir el contrato y la integración de la consulta de movimientos.
- [X] T052 Sustituir el proveedor de texto libre por un selector del catálogo activo en órdenes de compra.
