# Guía rápida: Precios y márgenes

1. `docker compose up -d --build`
2. Abra `http://127.0.0.1:5001` y entre a **Precios y márgenes**.
3. Consulte el tablero, simule un precio y aplíquelo indicando motivo.
4. Ejecute `pytest tests/unit tests/contract` y luego las integraciones con `MONGO_DB=comercio_inteligente_test`.
