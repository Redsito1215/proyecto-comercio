# Research: Pagos y seguridad

- Contraseñas: `scrypt` mediante Werkzeug, con salt individual.
- Sesiones: token aleatorio de alta entropía; MongoDB guarda SHA-256 y TTL.
- Tarjetas: solo referencias tokenizadas del proveedor; entrada con campos prohibidos se rechaza.
- Idempotencia: clave única y respuesta reutilizable.
- Sandbox: aprobaciones deterministas para pruebas, rotulado como no productivo.
- RBAC: permisos en roles; el decorador valida sesión y permiso fuera de desarrollo.
