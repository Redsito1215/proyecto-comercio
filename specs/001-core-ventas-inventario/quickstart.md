# Guía rápida: Validación del núcleo

## Requisitos

- Docker Desktop con Compose.
- Puertos de web y MongoDB disponibles.
- Archivo `.env` derivado de `.env.example`.

## Arranque

```powershell
cd C:\examenfinal\proyecto-comercio-inteligente
docker compose up -d --build
docker compose ps
```

## Pruebas

```powershell
docker compose exec -T backend pytest -q tests/unit
docker compose exec -T mongo mongosh --quiet --eval "db.getSiblingDB('comercio_inteligente_test').dropDatabase()"
docker compose exec -T -e MONGO_DB=comercio_inteligente_test backend pytest -q tests/contract tests/integration
```

## Escenarios de aceptación

1. Crear categoría, producto perecedero, proveedor y ubicación.
2. Crear una orden y recibir dos lotes con caducidades distintas.
3. Vender unidades y confirmar que se usa primero el lote que vence antes.
4. Repetir la confirmación con la misma clave y comprobar que no se duplica.
5. Contar inventario, aprobar una diferencia y revisar el movimiento compensatorio.
6. Registrar solicitud sin stock y consultar la venta perdida.
7. Devolver unidades aptas y dañadas y verificar inventario y merma.

## Resultado esperado

Los documentos, existencias y movimientos quedan conciliados; ninguna operación repetida
duplica efectos y todo cambio sensible conserva responsable, fecha, origen y motivo.
