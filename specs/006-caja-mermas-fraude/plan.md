# Plan de implementación: Caja, mermas y señales de fraude

**Rama**: `006-caja-mermas-fraude` | **Fecha**: 2026-09-03 | **Especificación**: [spec.md](spec.md)

## Resumen

Implementar apertura y cierre de caja, libro inmutable de movimientos, arqueos parciales,
registro transaccional de mermas y señales por diferencias repetidas. Las alertas se expresan
como situaciones que requieren revisión y nunca como acusaciones automáticas contra personas.

## Contexto técnico

- **Lenguajes**: Python 3.12 y JavaScript ES2022.
- **Backend**: Flask 3, PyMongo 4 y transacciones MongoDB.
- **Dinero**: Decimal128 para saldos, diferencias y costos.
- **Persistencia**: MongoDB 8 en replica set con libro de movimientos append-only.
- **Frontend**: tablero responsive de caja, arqueo, merma y alertas.
- **Pruebas**: pytest unitario, de contrato e integración.
- **Dependencias**: inventario de 001, pagos en efectivo de 007 y ubicaciones administrables.

## Verificación de la constitución

- [x] Los movimientos originales no se borran ni se reescriben.
- [x] El saldo esperado se deriva del libro de caja.
- [x] El arqueo conserva esperado, contado, diferencia, motivo y actor.
- [x] Las alertas utilizan lenguaje neutral y evidencia verificable.
- [x] La merma y el descuento de inventario forman una sola operación transaccional.
- [x] Las acciones sensibles exigen permiso y quedan auditadas.

## Arquitectura y estructura

```text
backend/modules/controls/
├── routes.py       # tablero, caja, merma y alertas
├── schemas.py      # importes, conteos, causas y resolución
├── services.py     # sesiones, movimientos y transacciones
├── risk.py         # reglas puras de diferencia y recurrencia
└── indexes.py      # sesión abierta e idempotencia

frontend/js/modules/controls/
tests/{unit,contract,integration}/
```

## Persistencia e índices

- `cash_sessions`: caja, ubicación, apertura, saldos, diferencia y cierre.
- `cash_movements`: dirección, importe, origen, clave idempotente, actor y fecha.
- `cash_counts`: captura ciega del contado y diferencia calculada.
- `loss_events`: producto, lote, unidades, costo, causa y evidencia.
- `risk_alerts`: tipo, severidad, evidencia, estado, asignación y resolución.
- Un índice único parcial impide dos sesiones abiertas por caja.

## Límites transaccionales y flujos

1. Abrir una sesión con fondo inicial si la caja no tiene otra sesión abierta.
2. Anexar movimientos autorizados y recalcular el saldo esperado.
3. Registrar arqueos sin modificar movimientos anteriores.
4. Cerrar conservando el saldo esperado, contado, diferencia y responsable.
5. Registrar una merma junto con el descuento de inventario y su movimiento.
6. Evaluar diferencias relevantes o repetidas y crear una señal con evidencia.
7. Resolver la alerta con conclusión y actor, preservando el registro original.
8. Conciliar un pago en efectivo con un único movimiento de origen `sale`.

## Fases y artefactos

- **Fase 0 — Investigación**: libro, arqueo, alertas y correcciones en [research.md](research.md).
- **Fase 1 — Diseño**: colecciones e índices en [data-model.md](data-model.md).
- **Fase 2 — Contrato**: caja, pérdidas y alertas en [contracts/openapi.yaml](contracts/openapi.yaml).
- **Fase 3 — Implementación**: tareas funcionales e integración en [tasks.md](tasks.md).
- **Fase 4 — Validación**: flujo reproducible en [quickstart.md](quickstart.md).

## Estrategia de pruebas

- Unitarias: saldo esperado, diferencia, umbral y recurrencia.
- Contrato: apertura, movimientos, arqueo, cierre, merma y alertas.
- Integración: transacciones de inventario, caja y pagos en efectivo.
- Regresión: rechazo sin caja, reintentos idempotentes y cierre conciliado.

## Riesgos y controles

- **Caja inconsistente**: libro append-only y saldo derivado.
- **Doble movimiento**: clave idempotente y origen único.
- **Merma parcial**: transacción conjunta con inventario.
- **Acusación injustificada**: evidencia, revisión humana y lenguaje neutral.

## Verificación constitucional posterior al diseño

PASS. El plan conserva trazabilidad, precisión e idempotencia, limita privilegios y separa una
señal de revisión de cualquier conclusión sobre fraude.
