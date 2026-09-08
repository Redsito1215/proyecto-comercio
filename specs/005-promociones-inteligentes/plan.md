# Plan de implementación: Promociones inteligentes

**Rama**: `005-promociones-inteligentes` | **Fecha**: 2026-09-03 | **Especificación**: [spec.md](spec.md)

## Resumen

Implementar promociones rentables con audiencia explicable, consentimiento vigente, grupo de
control determinista, cupones limitados y medición de resultados. El sistema prepara una
notificación pendiente, pero no simula el envío mediante un proveedor externo inexistente.

## Contexto técnico

- **Lenguajes**: Python 3.12 y JavaScript ES2022.
- **Backend**: Flask 3, PyMongo 4 y elegibilidad desacoplada.
- **Persistencia**: MongoDB 8 con audiencia, cupones, redenciones y outbox.
- **Frontend**: asistente responsive para creación, audiencia, activación y métricas.
- **Pruebas**: pytest unitario, de contrato e integración.
- **Dependencias**: clientes/consentimientos de 002 y precios/márgenes de 003.
- **Estados implementados**: `draft`, `audience_ready` y `active`.

## Verificación de la constitución

- [x] El margen mínimo se valida antes de preparar la campaña.
- [x] La audiencia conserva elegibilidad y explicación.
- [x] El consentimiento se comprueba al preparar la audiencia.
- [x] El grupo de control se asigna mediante hash estable.
- [x] La redención es idempotente y respeta límites de uso.
- [x] Las métricas distinguen tratamiento y control.

## Arquitectura y estructura

```text
backend/modules/promotions/
├── routes.py       # campaña, audiencia, activación y métricas
├── schemas.py      # vigencia, descuento y redención
├── services.py     # ciclo de vida, cupones y medición
├── eligibility.py  # consentimiento, afinidad y asignación
└── indexes.py      # unicidad e idempotencia

frontend/js/modules/promotions/
tests/{unit,contract,integration}/
```

## Persistencia e índices

- `promotions`: definición, productos, segmento, descuento, vigencia y estado.
- `promotion_audience`: elegibilidad, razón, grupo y consentimiento observado.
- `promotion_coupons`: código, cliente, vigencia, uso y estado.
- `promotion_redemptions`: venta, descuento y actor de cada canje.
- `notification_outbox`: intención de comunicación sin afirmar un envío externo.
- Unicidad por audiencia, código de cupón y combinación cupón/venta.

## Flujo funcional

1. Crear una promoción en borrador con productos, descuento y vigencia.
2. Simular el precio descontado y rechazar productos bajo margen mínimo.
3. Evaluar clientes y excluir quienes no tengan consentimiento vigente.
4. Asignar control o tratamiento de forma determinista y persistir la razón.
5. Crear cupones y elementos de outbox solo para tratamiento elegible.
6. Activar la campaña cuando la audiencia esté preparada.
7. Registrar redenciones idempotentes y calcular conversión, ingreso y margen.

## Fases y artefactos

- **Fase 0 — Investigación**: experimento, rentabilidad y consentimiento en [research.md](research.md).
- **Fase 1 — Diseño**: colecciones e índices en [data-model.md](data-model.md).
- **Fase 2 — Contrato**: campaña, audiencia, activación y métricas en [contracts/openapi.yaml](contracts/openapi.yaml).
- **Fase 3 — Implementación**: actividades terminadas en [tasks.md](tasks.md).
- **Fase 4 — Validación**: ejecución reproducible en [quickstart.md](quickstart.md).

## Estrategia de pruebas

- Unitarias: elegibilidad, asignación estable y margen promocional.
- Contrato: ciclo de vida, audiencia, activación, métricas y redención.
- Integración: consentimiento, cupones, outbox y resultados por grupo.
- Regresión: control no recibe cupón y un reintento no duplica redención.

## Riesgos y controles

- **Descuento destructivo**: validación por producto contra margen mínimo.
- **Sesgo experimental**: asignación reproducible antes de medir resultados.
- **Contacto sin permiso**: comprobación de consentimiento en cada preparación.
- **Métrica engañosa**: comparación separada de tratamiento y control.

## Verificación constitucional posterior al diseño

PASS. La promoción preserva rentabilidad, consentimiento, explicación y trazabilidad, y sus
resultados se presentan como evidencia medible en lugar de causalidad automática.
