"""Catálogo de informes simples RS-01…RS-20.

Un informe simple es un listado operativo sobre una única fuente de MongoDB. Puede
enriquecer cada fila con el nombre del producto o del cliente, pero no agrega ni
cruza periodos: para eso están los informes compuestos de ``compuestos.py``.

Cada entrada declara el permiso que exige, de modo que el catálogo se filtra por
usuario antes de ofrecerlo y la ejecución vuelve a verificarlo en la ruta.
"""

SIMPLE_REPORTS = [
    {
        "id": "RS-01",
        "name": "Ventas confirmadas del periodo",
        "spec": "001-core-ventas-inventario",
        "para_que": "Revisar qué ventas se cerraron y por cuánto en un rango de fechas.",
        "quien": "Cajero, gerente comercial",
        "permission": "sales.read",
        "filters": ["date", "search"],
        "columns": ["Número", "Fecha", "Ubicación", "Estado", "Cliente", "Total"],
    },
    {
        "id": "RS-02",
        "name": "Productos por debajo del umbral de existencias",
        "spec": "001-core-ventas-inventario",
        "para_que": "Detectar qué productos se están agotando para reponerlos a tiempo.",
        "quien": "Responsable de almacén, comprador",
        "permission": "inventory.read",
        "filters": ["threshold", "search"],
        "columns": ["SKU", "Producto", "Ubicación", "Disponible", "Reservado", "Costo medio"],
    },
    {
        "id": "RS-03",
        "name": "Lotes próximos a caducar",
        "spec": "001-core-ventas-inventario",
        "para_que": "Priorizar la salida de mercancía antes de que venza y se convierta en merma.",
        "quien": "Responsable de almacén",
        "permission": "inventory.read",
        "filters": ["days", "search"],
        "columns": ["Lote", "SKU", "Producto", "Ubicación", "Disponible", "Caduca", "Días restantes"],
    },
    {
        "id": "RS-04",
        "name": "Movimientos de inventario",
        "spec": "001-core-ventas-inventario",
        "para_que": "Trazar cada entrada y salida de existencias con su origen y responsable.",
        "quien": "Responsable de almacén, auditor",
        "permission": "inventory.read",
        "filters": ["date", "search"],
        "columns": ["Fecha", "SKU", "Producto", "Ubicación", "Tipo", "Cantidad", "Costo unitario", "Origen"],
    },
    {
        "id": "RS-05",
        "name": "Órdenes de compra abiertas",
        "spec": "001-core-ventas-inventario",
        "para_que": "Ver qué pedidos a proveedores siguen sin llegar completos a bodega.",
        "quien": "Comprador, jefe de compras",
        "permission": "purchases.read",
        "filters": ["date", "search"],
        "columns": ["Número", "Proveedor", "Ubicación", "Estado", "Total", "Líneas pendientes", "Creada"],
    },
    {
        "id": "RS-06",
        "name": "Ventas perdidas por agotado",
        "spec": "001-core-ventas-inventario",
        "para_que": "Cuantificar la demanda que no se pudo atender por falta de existencias.",
        "quien": "Comprador, gerente comercial",
        "permission": "inventory.read",
        "filters": ["date", "search"],
        "columns": ["Fecha", "SKU", "Producto", "Cantidad solicitada", "Motivo"],
    },
    {
        "id": "RS-07",
        "name": "Clientes activos y su segmento",
        "spec": "002-clientes-fidelizacion",
        "para_que": "Consultar la cartera vigente con su segmento, frecuencia y valor calculado.",
        "quien": "Vendedor, gerente comercial",
        "permission": "customers.read",
        "filters": ["search"],
        "columns": ["Cliente", "Correo", "Segmento", "Frecuencia", "Gasto", "Margen", "Explicación"],
    },
    {
        "id": "RS-08",
        "name": "Señales de abandono de clientes",
        "spec": "002-clientes-fidelizacion",
        "para_que": "Identificar clientes retrasados respecto de su propio intervalo de compra.",
        "quien": "Responsable comercial",
        "permission": "customers.read",
        "filters": ["search"],
        "columns": ["Cliente", "Estado", "Intervalo esperado", "Días sin comprar", "Retraso", "Confianza", "Motivo"],
    },
    {
        "id": "RS-09",
        "name": "Consentimientos de clientes",
        "spec": "002-clientes-fidelizacion",
        "para_que": "Comprobar quién autorizó comunicaciones antes de enviar una campaña.",
        "quien": "Encargado de fidelización, auditor",
        "permission": "customers.read",
        "filters": ["search"],
        "columns": ["Cliente", "Propósito", "Canal", "Estado", "Origen", "Actualizado"],
    },
    {
        "id": "RS-10",
        "name": "Historial de cambios de precio",
        "spec": "003-precios-margenes",
        "para_que": "Auditar qué precios cambiaron, con qué margen resultante y bajo qué motivo.",
        "quien": "Gerente comercial, auditor",
        "permission": "products.read",
        "filters": ["date", "search"],
        "columns": ["Fecha", "SKU", "Producto", "Precio anterior", "Precio nuevo", "Margen %", "Motivo"],
    },
    {
        "id": "RS-11",
        "name": "Observaciones de precios de competencia",
        "spec": "003-precios-margenes",
        "para_que": "Consultar la referencia externa registrada con su fuente y fecha.",
        "quien": "Analista comercial",
        "permission": "products.read",
        "filters": ["date", "search"],
        "columns": ["Observado", "SKU", "Producto", "Competidor", "Canal", "Precio observado", "Fuente"],
    },
    {
        "id": "RS-12",
        "name": "Compra sugerida de la última corrida",
        "spec": "004-pronostico-demanda",
        "para_que": "Revisar la recomendación de reposición antes de convertirla en orden de compra.",
        "quien": "Comprador",
        "permission": "inventory.read",
        "filters": ["search"],
        "columns": ["SKU", "Producto", "Esperado", "Intervalo", "Confianza", "Disponible", "Sugerido"],
    },
    {
        "id": "RS-13",
        "name": "Promociones registradas y su estado",
        "spec": "005-promociones-inteligentes",
        "para_que": "Saber qué campañas están en borrador, listas o activas y con qué vigencia.",
        "quien": "Gerente comercial",
        "permission": "products.read",
        "filters": ["date", "search"],
        "columns": ["Promoción", "Segmento", "Canal", "Descuento %", "Estado", "Desde", "Hasta"],
    },
    {
        "id": "RS-14",
        "name": "Cupones de promoción emitidos",
        "spec": "005-promociones-inteligentes",
        "para_que": "Controlar qué cupones se emitieron, a quién y cuántos usos les quedan.",
        "quien": "Gerente comercial, auditor",
        "permission": "products.read",
        "filters": ["search"],
        "columns": ["Código", "Cliente", "Estado", "Usos", "Límite", "Desde", "Hasta"],
    },
    {
        "id": "RS-15",
        "name": "Sesiones de caja y sus diferencias",
        "spec": "006-caja-mermas-fraude",
        "para_que": "Revisar apertura, cierre y descuadre de cada turno con su responsable.",
        "quien": "Supervisor de caja, auditor",
        "permission": "payments.read",
        "filters": ["date"],
        "columns": ["Caja", "Ubicación", "Estado", "Fondo inicial", "Esperado", "Contado", "Diferencia", "Abierta"],
    },
    {
        "id": "RS-16",
        "name": "Mermas registradas",
        "spec": "006-caja-mermas-fraude",
        "para_que": "Medir cuántas unidades y cuánto costo se perdieron y por qué causa.",
        "quien": "Gerente, responsable de almacén",
        "permission": "inventory.read",
        "filters": ["date", "search"],
        "columns": ["Fecha", "SKU", "Producto", "Ubicación", "Tipo", "Cantidad", "Costo unitario", "Costo total", "Motivo"],
    },
    {
        "id": "RS-17",
        "name": "Alertas de riesgo",
        "spec": "006-caja-mermas-fraude",
        "para_que": "Revisar señales abiertas de descuadre sin afirmar fraude, con su evidencia.",
        "quien": "Auditor",
        "permission": "payments.read",
        "filters": ["date"],
        "columns": ["Fecha", "Tipo", "Severidad", "Estado", "Entidad", "Mensaje", "Resolución"],
    },
    {
        "id": "RS-18",
        "name": "Pagos procesados",
        "spec": "007-pagos-seguridad",
        "para_que": "Conciliar cobros por medio, estado y proveedor sin exponer datos de tarjeta.",
        "quien": "Cajero, gerente comercial",
        "permission": "payments.read",
        "filters": ["date", "search"],
        "columns": ["Fecha", "Venta", "Medio", "Estado", "Importe", "Proveedor", "Referencia", "Últimos 4"],
    },
    {
        "id": "RS-19",
        "name": "Usuarios y roles asignados",
        "spec": "007-pagos-seguridad",
        "para_que": "Revisar quién tiene acceso al sistema y con qué privilegios.",
        "quien": "Administrador, auditor",
        "permission": "security.users.read",
        "filters": ["search"],
        "columns": ["Nombre", "Correo", "Roles", "Estado", "Intentos fallidos", "Creado"],
    },
    {
        "id": "RS-20",
        "name": "Auditoría de eventos sensibles",
        "spec": "007-pagos-seguridad",
        "para_que": "Rastrear accesos, cambios y pagos con su actor y resultado.",
        "quien": "Auditor",
        "permission": "security.audit.read",
        "filters": ["date", "search"],
        "columns": ["Fecha", "Actor", "Acción", "Entidad", "Identificador", "Resultado"],
    },
]

SIMPLE_BY_ID = {report["id"]: report for report in SIMPLE_REPORTS}


def describe(report):
    return {**report, "tipo": "simple", "data_layer": "mongodb"}


def check_width(report, rows):
    """Falla ruidosamente si un ejecutor devuelve más o menos campos que columnas.

    Sin esta comprobación una fila desalineada produciría un PDF con las celdas
    corridas, que parece un informe válido y por eso cuesta detectarlo. La usan
    tanto los informes simples como los compuestos.
    """
    expected = len(report["columns"])
    for row in rows:
        if len(row) != expected:
            raise ValueError(f'{report["id"]}: se devolvieron {len(row)} campos y el catálogo declara {expected} columnas')
    return rows
