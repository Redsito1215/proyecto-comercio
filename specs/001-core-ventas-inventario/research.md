# Investigación: Núcleo de ventas e inventario

## MongoDB como tablas lógicas

**Decision**: Usar colecciones separadas equivalentes a tablas para maestros, documentos y
libros de movimientos; las líneas comerciales se separan cuando requieren consulta y auditoría.

**Rationale**: Facilita el diagrama académico, índices, validaciones y trazabilidad sin renunciar
al motor MongoDB exigido.

**Alternatives considered**: Documentos totalmente embebidos, descartados por crecimiento y
consultas; base relacional, descartada por restricción del proyecto.

## Consistencia

**Decision**: Ejecutar MongoDB como replica set y usar transacciones para flujos que cambian más
de una tabla lógica. Todo comando crítico recibe una clave de idempotencia única.

**Rationale**: Venta, recepción, ajuste y devolución no pueden quedar parcialmente aplicados.

**Alternatives considered**: Compensación posterior, reservada solo para integraciones externas.

## Valor monetario

**Decision**: Almacenar importes como Decimal128 y porcentajes con escala definida; nunca float.

**Rationale**: Evita errores acumulativos en totales, costo y margen.

## Rotación de lotes

**Decision**: FEFO para perecederos y FIFO para productos sin caducidad, con exclusión de lotes
vencidos, bloqueados o retirados.

**Rationale**: Reduce merma y preserva trazabilidad.

## Interfaz y API

**Decision**: API JSON versionada y frontend estático modular con el lenguaje visual de Altavia
Trade, sin compartir datos ni configuración de ese sistema.

**Rationale**: Mantiene separación de responsabilidades y permite pruebas de contrato.
