# Implementation Plan: Núcleo de ventas e inventario

**Branch**: `001-core-ventas-inventario` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

## Summary

Implementar el núcleo transaccional de productos, ventas, lotes, inventario, compras, conteos,
devoluciones y ventas perdidas. MongoDB se documentará como tablas lógicas y operará como
replica set para aplicar transacciones e idempotencia. La API será consumida por una interfaz
basada en los patrones visuales de `C:\proyect6softwa` y todo se ejecutará con Docker Compose.

## Technical Context

- **Language/Version**: Python 3.12; JavaScript ES2022
- **Primary Dependencies**: Flask 3, PyMongo 4, Pydantic 2, pytest 8
- **Storage**: MongoDB 8 replica set; volúmenes Docker persistentes
- **Testing**: pytest, pruebas de contrato HTTP e integración con MongoDB
- **Target Platform**: navegador moderno y contenedores Linux sobre Docker Desktop
- **Project Type**: aplicación web modular con backend API y frontend estático
- **Performance Goals**: búsqueda visible <1 s; confirmación típica <2 s; venta de cinco líneas <60 s
- **Constraints**: español, importes decimales, Ecuador, operaciones idempotentes, sin stock negativo
- **Scale/Scope**: comercio pequeño/mediano, hasta 100 mil productos y 1 millón de movimientos/año

## Constitution Check

- [x] El alcance pertenece a `001-core-ventas-inventario`.
- [x] Ventas y movimientos son atómicos, idempotentes y auditables.
- [x] Las recomendaciones muestran motivo y requieren decisión humana.
- [x] Autorización se valida en servidor y los secretos usan variables de entorno.
- [x] Se definen pruebas y arranque reproducible con Docker Compose.
- [x] MongoDB opera como replica set y conserva documentos históricos.

## Project Structure

```text
backend/
├── app.py
├── config.py
├── db.py
├── auth/
├── common/
└── modules/core/
    ├── routes.py
    ├── schemas.py
    ├── services.py
    ├── repositories.py
    └── indexes.py

frontend/
├── index.html
├── css/
└── js/modules/core/

tests/
├── contract/
├── integration/
└── unit/
```

## Phase 0: Research

Las decisiones y alternativas están en [research.md](research.md). No quedan aclaraciones
pendientes.

## Phase 1: Design and Contracts

- Modelo lógico y validaciones: [data-model.md](data-model.md)
- Contrato HTTP: [contracts/openapi.yaml](contracts/openapi.yaml)
- Validación reproducible: [quickstart.md](quickstart.md)

## Transaction Boundaries

- Confirmar venta: venta + líneas + lotes + existencia + movimientos + auditoría.
- Recibir compra: recepción + orden + lotes + existencia + movimientos + auditoría.
- Aprobar ajuste: conteo + existencia + movimiento compensatorio + auditoría.
- Confirmar devolución: devolución + cantidades devueltas + lote/merma + movimientos.

## Post-Design Constitution Check

PASS. El diseño conserva trazabilidad, evita reescritura histórica, requiere autorización,
define idempotencia y no introduce excepciones a la constitución.
