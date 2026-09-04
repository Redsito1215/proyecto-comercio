# Implementation Plan: Clientes y fidelización

Python 3.12, Flask, MongoDB replica set, JavaScript y pytest. El módulo `backend/modules/customers/` expondrá perfiles, consentimientos, segmentación explicable y señales de abandono. La UI reutilizará el shell Altavia bajo `frontend/js/modules/customers/`.

## Constitution Check
- PASS: consentimiento, privacidad, explicación, auditoría, pruebas y Docker están cubiertos.

## Structure
`backend/modules/customers/{schemas,repositories,services,routes,indexes}.py`, `frontend/js/modules/customers/`, `tests/{unit,contract,integration}/`.

## Design Artifacts
- [research.md](research.md)
- [data-model.md](data-model.md)
- [contracts/openapi.yaml](contracts/openapi.yaml)
- [quickstart.md](quickstart.md)
