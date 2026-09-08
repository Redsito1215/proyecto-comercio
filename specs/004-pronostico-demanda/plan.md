# Plan de implementación: Pronóstico de demanda

**Rama**: `004-pronostico-demanda` | **Fecha**: 2026-09-03 | **Especificación**: [spec.md](spec.md)

## Resumen

Implementar corridas versionadas de pronóstico por producto y ubicación. La demanda observada
combina ventas, devoluciones y ventas perdidas, y se contextualiza con disponibilidad, precio,
promociones y sustitutos. El resultado presenta valor esperado, intervalo, confianza, factores
y cantidad sugerida; nunca genera automáticamente una orden de compra.

## Contexto técnico

- **Lenguajes**: Python 3.12 y JavaScript ES2022.
- **Backend**: Flask 3, PyMongo 4 y motor determinista aislado.
- **Persistencia**: MongoDB 8 para corridas y resultados versionados.
- **Fuentes**: ventas, devoluciones, ventas perdidas, stock, precios y promociones.
- **Frontend**: tablero responsive con explicación, confianza e intervalo.
- **Pruebas**: pytest unitario, de contrato e integración.
- **Restricción**: toda recomendación requiere revisión humana.

## Verificación de la constitución

- [x] Cada resultado incluye factores, incertidumbre y versión del método.
- [x] Una venta alta temporal no se interpreta como demanda permanente.
- [x] Las ventas perdidas durante agotados forman parte de la señal.
- [x] La fecha de corte permite reproducir una corrida.
- [x] El pronóstico no crea órdenes de compra.
- [x] El motor puede probarse sin depender de la interfaz.

## Arquitectura y estructura

```text
backend/modules/forecasting/
├── routes.py       # ejecución y consulta
├── schemas.py      # horizonte, período y filtros
├── services.py     # agregación y persistencia
├── engine.py       # cálculo robusto y explicable
└── indexes.py      # unicidad y corridas recientes

frontend/js/modules/forecasting/
tests/{unit,contract,integration}/
```

## Persistencia e índices

- `forecast_runs`: corte, horizonte, historia, ubicación, versión, estado y actor.
- `forecasts`: producto, esperado, límites, confianza, factores, disponible y sugerencia.
- La serie diaria se deriva de fuentes operativas y no se duplica.
- Un índice único por corrida, producto y ubicación evita resultados repetidos.

## Flujo de cálculo

1. Validar corte, horizonte, período histórico y ubicación.
2. Agregar unidades vendidas netas y ventas perdidas por día y producto.
3. Marcar agotados, cambios de precio, promociones y sustitutos.
4. Calcular una base robusta que limite picos aislados.
5. Producir esperado, límites, confianza y factores.
6. Restar disponibilidad y obtener una sugerencia no negativa.
7. Persistir corrida y resultados con versión del método.

## Fases y artefactos

- **Fase 0 — Investigación**: decisiones analíticas en [research.md](research.md).
- **Fase 1 — Diseño**: corridas, resultados e índices en [data-model.md](data-model.md).
- **Fase 2 — Contrato**: ejecución y consulta en [contracts/openapi.yaml](contracts/openapi.yaml).
- **Fase 3 — Implementación**: motor, API e interfaz en [tasks.md](tasks.md).
- **Fase 4 — Validación**: casos reproducibles en [quickstart.md](quickstart.md).

## Estrategia de pruebas

- Unitarias: base robusta, intervalos, confianza y ventas perdidas.
- Contrato: creación, validaciones y consulta de resultados.
- Integración: agregación operativa y persistencia versionada.
- Regresión: un pico aislado no domina y una corrida no crea compras.

## Riesgos y controles

- **Demanda censurada**: ventas perdidas y menor confianza si faltan registros.
- **Sobrecompra temporal**: estadística robusta y factores visibles.
- **Datos insuficientes**: intervalo amplio y confianza baja.
- **Resultados irreproducibles**: corte y versión obligatorios.

## Verificación constitucional posterior al diseño

PASS. El pronóstico es explicable, versionado y conservador; presenta incertidumbre y mantiene
la decisión de abastecimiento fuera de automatizaciones irreversibles.
