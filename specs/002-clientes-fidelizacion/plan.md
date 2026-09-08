# Plan de implementación: Clientes y fidelización

**Rama**: `002-clientes-fidelizacion` | **Fecha**: 2026-09-03 | **Especificación**: [spec.md](spec.md)

## Resumen

Implementar el registro y consulta de clientes, consentimiento por propósito y canal,
segmentación explicable, señales de abandono individual y cupones de cumpleaños. El módulo
utiliza las ventas confirmadas del núcleo comercial y muestra por qué se asignó cada segmento
o alerta, sin convertir una regla estadística en una afirmación definitiva sobre el cliente.

## Contexto técnico

- **Lenguajes**: Python 3.12 y JavaScript ES2022.
- **Backend**: Flask 3, PyMongo 4 y validación de entrada mediante esquemas.
- **Persistencia**: MongoDB 8 en replica set, con índices únicos parciales.
- **Frontend**: módulo responsive integrado en el shell visual compartido.
- **Pruebas**: pytest unitario, de contrato e integración con MongoDB.
- **Privacidad**: consentimiento revocable; no se realiza envío externo de email o SMS.
- **Dependencias**: ventas de 001, márgenes de 003 y promociones de 005.

## Verificación de la constitución

- [x] Los datos personales se limitan a información necesaria y autorizada.
- [x] El consentimiento conserva propósito, canal, origen, fecha y revocación.
- [x] Segmentos y señales incluyen explicación, fecha y nivel de confianza.
- [x] Las acciones protegidas se autorizan en el servidor y se auditan.
- [x] Los cálculos no dependen únicamente del gasto ni de un plazo fijo universal.
- [x] El módulo dispone de pruebas reproducibles y ejecución con Docker Compose.

## Arquitectura y estructura

```text
backend/modules/customers/
├── routes.py       # API HTTP y autorización
├── schemas.py      # validación y normalización
├── services.py     # clientes, consentimientos y cupones
├── analytics.py    # valor, segmentos y abandono
└── indexes.py      # unicidad y consultas operativas

frontend/js/modules/customers/
tests/{unit,contract,integration}/
```

## Persistencia e índices

- `customers`: identidad comercial, contacto, cumpleaños y estado.
- `customer_consents`: autorización vigente o revocada por propósito y canal.
- `customer_segments`: frecuencia, gasto, margen, puntuación y explicación.
- `churn_signals`: intervalo esperado, retraso, confianza, razón y estado.
- `coupons`: cupón de cumpleaños con vigencia y límite de uso.
- Email y documento usan índices únicos parciales para admitir datos opcionales.

## Flujos de implementación

1. Registrar o actualizar un cliente normalizando email y documento.
2. Registrar consentimiento y conservar su procedencia; la revocación bloquea comunicaciones.
3. Asociar opcionalmente ventas confirmadas y recalcular métricas.
4. Combinar frecuencia, gasto y margen para producir un segmento explicable.
5. Estimar el intervalo habitual y emitir una señal conservadora si existe retraso.
6. Crear un cupón de cumpleaños solo con consentimiento y reglas vigentes.

## Fases y artefactos

- **Fase 0 — Investigación**: valor, abandono y privacidad en [research.md](research.md).
- **Fase 1 — Diseño**: colecciones e índices en [data-model.md](data-model.md).
- **Fase 2 — Contrato**: operaciones públicas en [contracts/openapi.yaml](contracts/openapi.yaml).
- **Fase 3 — Implementación**: servicios, analítica, API e interfaz en [tasks.md](tasks.md).
- **Fase 4 — Validación**: recorrido reproducible en [quickstart.md](quickstart.md).

## Estrategia de pruebas

- Unitarias: valor del cliente e intervalo individual de abandono.
- Contrato: altas, consultas, consentimiento, recálculo y cupón.
- Integración: persistencia, índices, asociación con ventas y reglas negativas.
- Regresión: un cliente sin consentimiento no genera comunicación pendiente.

## Riesgos y controles

- **Duplicados**: normalización e índices únicos parciales.
- **Falsos abandonos**: confianza explícita e historial mínimo.
- **Promociones invasivas**: consentimiento comprobado al crear la acción.
- **Clasificación opaca**: componentes y explicación persistidos con el segmento.

## Verificación constitucional posterior al diseño

PASS. El diseño protege consentimiento y privacidad, explica las decisiones analíticas,
mantiene trazabilidad y deja cualquier intervención bajo revisión humana.
