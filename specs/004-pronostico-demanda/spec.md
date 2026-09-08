# Especificación funcional: Pronóstico de demanda

**Rama funcional**: `004-pronostico-demanda`
**Creada**: 2026-09-03
**Estado**: Completada y verificada

## Historias de usuario

### US1 - Estimar demanda explicable (P1)
Como comprador quiero un pronóstico que distinga ventas observadas de demanda no atendida y explique los factores empleados.

**Prueba independiente**: generar una corrida con ventas históricas y comprobar que cada producto muestra esperado, intervalo, confianza y explicación.

**Escenarios de aceptación**:

1. **Dado** un historial suficiente, **cuando** se ejecuta el pronóstico, **entonces** se genera un resultado versionado por producto y ubicación.
2. **Dado** poco historial, **cuando** se calcula, **entonces** se declara baja confianza en lugar de presentar certeza falsa.

### US2 - Evitar sobrecompra temporal (P1)
Como gerente quiero reconocer picos provocados por promociones, variación de precio o ausencia de sustitutos para no perpetuarlos.

**Prueba independiente**: comparar una serie estable con otra que contiene un pico promocional y verificar que la base robusta limita su influencia.

**Escenarios de aceptación**:

1. **Dado** un pico aislado, **cuando** se calcula la base, **entonces** no domina por sí solo toda la recomendación.
2. **Dada** una variación de precio, **entonces** aparece entre los factores explicativos.

### US3 - Detectar demanda oculta (P2)
Como encargado quiero sumar ventas perdidas durante agotados y mostrar incertidumbre cuando faltan datos.

**Prueba independiente**: registrar una venta perdida por agotamiento y comprobar que se incorpora como señal de demanda censurada.

**Escenarios de aceptación**:

1. **Dado** un producto agotado con solicitudes registradas, **cuando** se pronostica, **entonces** esas solicitudes elevan la señal observada.
2. **Cuando** se muestra la compra sugerida, **entonces** el usuario puede revisarla y no se crea automáticamente una orden.

### Casos límite

- Producto sin ventas ni ventas perdidas.
- Devoluciones que reducen las unidades netas del período.
- Sustituto agotado en la misma fecha.
- Existencia superior al límite superior calculado.
- Horizonte o período histórico fuera de los límites permitidos.

## Requisitos funcionales
- **FR-001**: MUST agregar ventas confirmadas por producto, ubicación y día.
- **FR-002**: MUST incorporar ventas perdidas y períodos sin stock como demanda censurada.
- **FR-003**: MUST conservar precio, promoción, disponibilidad y sustitutos como variables explicativas.
- **FR-004**: MUST excluir anulaciones y ajustar devoluciones.
- **FR-005**: MUST producir horizonte, valor central, intervalo y confianza.
- **FR-006**: MUST explicar los factores que elevaron o redujeron el resultado.
- **FR-007**: MUST diferenciar tendencia temporal de señal persistente.
- **FR-008**: MUST registrar versión del método, fecha y datos de corte.
- **FR-009**: MUST permitir revisión humana antes de convertir pronóstico en compra.
- **FR-010**: MUST conservar cada corrida y permitir consultar el último resultado por ubicación.

## Criterios de éxito
- **SC-001**: Cada pronóstico incluye intervalo, confianza y al menos una explicación.
- **SC-002**: Los agotados con ventas perdidas no aparecen como demanda cero.
- **SC-003**: Ningún pronóstico crea órdenes automáticamente.
- **SC-004**: El tablero permite detectar riesgo de agotado y sobrestock en menos de 15 segundos.

## Supuestos
- Los datos operativos proceden de 001, precios de 003 y promociones de 005.
- La primera versión usa un modelo determinista explicable y deja preparado el reemplazo por modelos posteriores.

## Fuera de alcance

- Crear órdenes de compra automáticamente.
- Presentar el resultado como garantía de ventas futuras.
- Entrenar modelos o procesar datos fuera del entorno local.
