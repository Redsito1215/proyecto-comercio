# Investigación: Pagos y seguridad

- Contraseñas: `scrypt` mediante Werkzeug, con salt individual.
- Sesiones: token aleatorio de alta entropía; MongoDB guarda SHA-256 y TTL.
- Tarjetas: solo referencias tokenizadas del proveedor; entrada con campos prohibidos se rechaza.
- Idempotencia: clave única y respuesta reutilizable.
- Sandbox: aprobaciones deterministas para pruebas, rotulado como no productivo.
- RBAC: permisos en roles; el decorador valida sesión y permiso fuera de desarrollo.
- Defensa en profundidad: la interfaz oculta acciones no permitidas y el backend responde 403
  y registra `security.permission_denied` cuando se intenta evadirla.
- Efectivo: exige sesión abierta y usa una referencia de origen única para que el reintento no
  duplique el movimiento de caja.
- Informes: auditoría y datos comerciales se filtran antes de generar un PDF; ClickHouse recibe
  hechos analíticos mediante un DAG idempotente de Airflow sin sustituir MongoDB operativo.
