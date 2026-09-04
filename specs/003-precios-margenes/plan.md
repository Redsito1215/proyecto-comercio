# Implementation Plan: Precios y márgenes

Python 3.12, Flask, MongoDB/Decimal128, JavaScript y pytest. `backend/modules/pricing/` calculará márgenes, simulará/aplicará precios y almacenará comparaciones; `frontend/js/modules/pricing/` reutilizará el shell visual de Altavia.

## Constitution Check
- PASS: precisión decimal, explicación, auditoría, seguridad, pruebas y despliegue Docker.

## Structure
`backend/modules/pricing/{schemas,analytics,services,routes,indexes}.py`, `frontend/js/modules/pricing/`, `tests/{unit,contract,integration}/`.

## Design Artifacts
- [research.md](research.md)
- [data-model.md](data-model.md)
- [contracts/openapi.yaml](contracts/openapi.yaml)
- [quickstart.md](quickstart.md)
