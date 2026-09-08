# Especificación funcional: Precios y márgenes

**Rama funcional**: `003-precios-margenes`
**Creada**: 2026-09-03
**Estado**: Completada y verificada

## Escenarios de usuario y pruebas

### Historia de usuario 1 - Conocer el margen real (P1)
Como responsable comercial quiero ver costo, precio, margen monetario y porcentual por producto para decidir con evidencia.

**Prueba independiente**: Consultar productos con distintos costos y verificar cálculos y clasificación visual.

**Escenarios de aceptación**:

1. **Dado** un producto con precio y costo, **cuando** se consulta el tablero, **entonces** se muestran margen porcentual y estado.
2. **Dado** un producto sin costo confiable, **cuando** se calcula su margen, **entonces** aparece como “Sin costo” sin inventar rentabilidad.

### Historia de usuario 2 - Cambiar precios con control (P1)
Como gerente quiero simular y aplicar un precio sin cruzar el margen mínimo autorizado.

**Prueba independiente**: Rechazar un precio bajo el piso, aceptar uno válido y conservar el historial.

**Escenarios de aceptación**:

1. **Dado** un precio propuesto rentable, **cuando** se aplica con motivo, **entonces** cambia el precio vigente y se conserva el historial.
2. **Dado** un precio que viola el mínimo, **cuando** se intenta aplicar, **entonces** se rechaza sin modificar el producto.

### Historia de usuario 3 - Comparar mercado (P2)
Como analista quiero registrar precios de competidores con fuente y fecha para medir la brecha sin convertirlos automáticamente en precio propio.

**Prueba independiente**: Registrar observaciones y obtener mínimo, mediana y posición relativa.

**Escenarios de aceptación**:

1. **Dadas** varias observaciones, **cuando** se consulta la comparación, **entonces** se conserva fuente, fecha y competidor.
2. **Cuando** cambia una referencia externa, **entonces** el precio propio no cambia automáticamente.

### Casos límite

- Precio igual a cero o costo ausente.
- Observaciones repetidas de un competidor en fechas diferentes.
- Producto inexistente, inactivo o identificador mal formado.
- Redondeo monetario al calcular porcentajes y brechas.

## Requisitos
- **FR-001**: El sistema MUST calcular margen como precio menos costo y porcentaje sobre precio.
- **FR-002**: El sistema MUST mostrar explícitamente productos sin costo confiable.
- **FR-003**: Cada producto MUST admitir un porcentaje mínimo de margen.
- **FR-004**: La simulación MUST devolver resultado, piso y advertencias sin modificar datos.
- **FR-005**: La aplicación MUST rechazar precios bajo el piso salvo flujo de autorización posterior.
- **FR-006**: Todo cambio MUST conservar precio anterior, nuevo, motivo, actor y vigencia.
- **FR-007**: El sistema MUST registrar observaciones externas con competidor, canal, fuente y fecha.
- **FR-008**: Las comparaciones MUST indicar antigüedad y no sobrescribir precios automáticamente.
- **FR-009**: Las ventas MUST conservar el precio y costo históricos de cada línea.
- **FR-010**: La interfaz MUST distinguir margen saludable, ajustado, crítico y desconocido.

## Criterios de éxito
- **SC-001**: Un usuario identifica productos con margen crítico en menos de 15 segundos.
- **SC-002**: El 100 % de cambios de precio conserva trazabilidad.
- **SC-003**: Ningún cambio ordinario deja el margen bajo el mínimo configurado.
- **SC-004**: Todos los cálculos monetarios usan Decimal128 y redondeo explícito.

## Supuestos
- El costo medio y precio actual provienen del núcleo 001.
- La captura competitiva inicial es manual; no se realiza scraping.
- Las promociones excepcionales se implementan en 005.

## Fuera de alcance

- Cambios automáticos de precio sin aprobación humana.
- Integración directa con sitios de competidores.
- Monedas múltiples dentro de una misma operación.
