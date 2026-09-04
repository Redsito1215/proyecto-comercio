# Tasks: Núcleo de ventas e inventario

**Input**: Documentos de `specs/001-core-ventas-inventario/`

## Phase 1: Setup

- [X] T001 Crear paquetes y archivos base según `specs/001-core-ventas-inventario/plan.md`
- [X] T002 Configurar dependencias Python en `requirements.txt`
- [X] T003 [P] Configurar variables documentadas en `.env.example`
- [X] T004 [P] Definir servicios MongoDB replica set y backend en `docker-compose.yml`
- [X] T005 [P] Crear imagen reproducible en `Dockerfile`

## Phase 2: Foundational

- [X] T006 Crear configuración validada en `backend/config.py`
- [X] T007 Crear conexión, transacciones y health check en `backend/db.py`
- [X] T008 [P] Crear errores JSON comunes en `backend/common/errors.py`
- [X] T009 [P] Crear serialización Decimal128/fechas en `backend/common/serialization.py`
- [X] T010 [P] Crear autorización mínima en `backend/auth/decorators.py`
- [X] T011 Crear índices y validadores en `backend/modules/core/indexes.py`
- [X] T012 Crear aplicación y registro modular en `backend/app.py`
- [X] T013 [P] Probar configuración y decimales en `tests/unit/test_common.py`

## Phase 3: User Story 1 - Cobrar rápidamente (P1) MVP

**Independent Test**: vender dos productos y verificar un único descuento de inventario.

- [ ] T014 [P] [US1] Escribir contrato de productos/ventas en `tests/contract/test_sales_api.py`
- [ ] T015 [P] [US1] Escribir concurrencia e idempotencia en `tests/integration/test_sale_transaction.py`
- [ ] T016 [P] [US1] Implementar esquemas de venta en `backend/modules/core/schemas.py`
- [ ] T017 [US1] Implementar repositorios de producto y venta en `backend/modules/core/repositories.py`
- [ ] T018 [US1] Implementar confirmación transaccional en `backend/modules/core/services.py`
- [ ] T019 [US1] Exponer productos y ventas en `backend/modules/core/routes.py`
- [ ] T020 [P] [US1] Crear pantalla de venta rápida en `frontend/js/modules/core/sales.js`
- [ ] T021 [US1] Integrar venta rápida en `frontend/index.html`

## Phase 4: User Story 2 - Inventario por lote (P1)

**Independent Test**: recibir dos lotes y comprobar salida FEFO y alertas.

- [ ] T022 [P] [US2] Escribir pruebas FEFO en `tests/unit/test_lot_allocation.py`
- [ ] T023 [P] [US2] Escribir integración de recepción en `tests/integration/test_inventory_receipt.py`
- [ ] T024 [US2] Implementar lotes, movimientos y alertas en `backend/modules/core/services.py`
- [ ] T025 [US2] Exponer inventario y alertas en `backend/modules/core/routes.py`
- [ ] T026 [P] [US2] Crear inventario visual en `frontend/js/modules/core/inventory.js`

## Phase 5: User Story 3 - Reposición (P2)

**Independent Test**: recibir parcialmente una orden y conciliar su saldo.

- [ ] T027 [P] [US3] Escribir contrato de compras en `tests/contract/test_purchases_api.py`
- [ ] T028 [P] [US3] Escribir integración parcial en `tests/integration/test_partial_receipt.py`
- [ ] T029 [US3] Implementar órdenes, cobertura y recepción en `backend/modules/core/services.py`
- [ ] T030 [US3] Exponer compras en `backend/modules/core/routes.py`
- [ ] T031 [P] [US3] Crear UI de compras en `frontend/js/modules/core/purchases.js`

## Phase 6: User Story 4 - Conteos y ventas perdidas (P2)

**Independent Test**: aprobar diferencia y registrar demanda no atendida.

- [ ] T032 [P] [US4] Escribir pruebas de conteo en `tests/integration/test_stock_count.py`
- [ ] T033 [US4] Implementar conteos y ajustes en `backend/modules/core/services.py`
- [ ] T034 [US4] Implementar ventas perdidas en `backend/modules/core/routes.py`
- [ ] T035 [P] [US4] Crear UI de conteos en `frontend/js/modules/core/counts.js`

## Phase 7: User Story 5 - Devoluciones (P3)

**Independent Test**: separar devuelto apto y dañado y comprobar destinos.

- [ ] T036 [P] [US5] Escribir pruebas de límites en `tests/unit/test_return_limits.py`
- [ ] T037 [P] [US5] Escribir integración en `tests/integration/test_return_transaction.py`
- [ ] T038 [US5] Implementar devolución transaccional en `backend/modules/core/services.py`
- [ ] T039 [US5] Exponer devolución en `backend/modules/core/routes.py`
- [ ] T040 [P] [US5] Crear UI de devoluciones en `frontend/js/modules/core/returns.js`

## Phase 8: Polish and Quality Gates

- [ ] T041 [P] Aplicar diseño base de Altavia en `frontend/css/app.css`
- [ ] T042 [P] Añadir accesibilidad y responsividad en `frontend/css/app.css`
- [ ] T043 Ejecutar pruebas y corregir regresiones documentadas en `tests/`
- [ ] T044 Ejecutar escenarios de `specs/001-core-ventas-inventario/quickstart.md`
- [ ] T045 Verificar trazabilidad FR→prueba en `specs/001-core-ventas-inventario/checklists/requirements.md`

## Dependencies

Setup → Foundational → US1. Después de Foundational, US2 y US3 pueden desarrollarse en
paralelo; US4 necesita movimientos y US5 necesita ventas e inventario. Polish depende de las
historias elegidas para la entrega.

## Implementation Strategy

El MVP comprende T001–T021. Cada historia se valida independientemente antes de continuar.
Las tareas `[P]` modifican archivos distintos o son pruebas que pueden prepararse en paralelo.
