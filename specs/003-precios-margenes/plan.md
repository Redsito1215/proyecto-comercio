# Plan de implementación: Precios y márgenes

**Rama**: `003-precios-margenes` | **Fecha**: 2026-09-03 | **Especificación**: [spec.md](spec.md)

## Resumen

Implementar cálculo monetario exacto de costo, precio y margen; simulación sin escritura;
cambio controlado de precios; y comparación con observaciones fechadas de competidores. Cada
cambio conserva su evidencia y ninguna observación externa modifica precios automáticamente.

## Contexto técnico

- **Lenguajes**: Python 3.12 y JavaScript ES2022.
- **Backend**: Flask 3, PyMongo 4 y operaciones analíticas puras.
- **Dinero**: `Decimal`/`Decimal128`, redondeo `ROUND_HALF_UP` a dos decimales.
- **Persistencia**: MongoDB 8; historial de precios de solo anexado.
- **Frontend**: tablero responsive de márgenes, simulación y mercado.
- **Pruebas**: pytest unitario, de contrato e integración.
- **Dependencia**: productos y costos de inventario de la Spec 001.

## Verificación de la constitución

- [x] Los importes evitan aritmética binaria de punto flotante.
- [x] Los cambios conservan precio anterior, costo, margen, motivo, actor y vigencia.
- [x] Las simulaciones no alteran el catálogo.
- [x] Las observaciones externas son evidencia, no órdenes automáticas.
- [x] Los permisos y la auditoría se aplican en el backend.
- [x] Las pruebas son reproducibles mediante Docker Compose.

## Arquitectura y estructura

```text
backend/modules/pricing/
├── routes.py       # márgenes, simulaciones y cambios
├── schemas.py      # validación decimal y comercial
├── services.py     # persistencia y reglas de precio
├── analytics.py    # cálculo y clasificación de margen
└── indexes.py      # historial y observaciones

frontend/js/modules/pricing/
tests/{unit,contract,integration}/
```

## Persistencia e índices

- `products`: precio, costo promedio, margen mínimo y fecha de actualización.
- `price_changes`: valor anterior y nuevo, costo, margen, motivo, actor y vigencia.
- `competitor_prices`: competidor, canal, precio, fuente, fecha y responsable.
- Los índices por producto y fecha recuperan historial y comparación recientes.

## Flujos de implementación

1. Consultar productos y calcular margen porcentual sobre precio de venta.
2. Clasificar productos por margen sin ocultar costo ni fórmula.
3. Simular un precio y mostrar su efecto sin persistir cambios.
4. Validar el margen mínimo del precio propuesto.
5. Aplicar el cambio autorizado y anexarlo a `price_changes`.
6. Registrar una observación competitiva y comparar sin automatizar decisiones.

## Fases y artefactos

- **Fase 0 — Investigación**: fórmula, precisión e historial en [research.md](research.md).
- **Fase 1 — Diseño**: extensiones e índices en [data-model.md](data-model.md).
- **Fase 2 — Contrato**: API de precios y mercado en [contracts/openapi.yaml](contracts/openapi.yaml).
- **Fase 3 — Implementación**: secuencia verificable en [tasks.md](tasks.md).
- **Fase 4 — Validación**: recorrido local y Docker en [quickstart.md](quickstart.md).

## Estrategia de pruebas

- Unitarias: fórmula, límites, redondeo y clasificación.
- Contrato: márgenes, simulaciones, cambios y competencia.
- Integración: historial persistente, producto actualizado e índices.
- Regresión: simular no escribe y vulnerar el margen mínimo se rechaza.

## Riesgos y controles

- **Errores monetarios**: Decimal128 y redondeo explícito.
- **Pérdida de historia**: registro append-only y valor vigente separado.
- **Fuente externa antigua**: fecha y procedencia visibles.
- **Cambio inseguro**: permiso, motivo y margen mínimo obligatorios.

## Verificación constitucional posterior al diseño

PASS. El plan conserva exactitud monetaria, explicación y evidencia histórica, y mantiene la
decisión final de precio bajo autorización humana.
