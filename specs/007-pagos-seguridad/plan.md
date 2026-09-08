# Plan de implementación: Pagos y seguridad

**Rama**: `007-pagos-seguridad` | **Fecha**: 2026-09-04 | **Especificación**: [spec.md](spec.md)

## Resumen

Implementar inicialización única del administrador, usuarios y roles, sesiones opacas, RBAC,
auditoría sanitizada, configuración general, pagos idempotentes y reembolsos controlados. Los
pagos electrónicos usan un adaptador sandbox y no almacenan PAN ni CVV. La especificación
también integra informes filtrables, PDF y estado de la canalización analítica.

## Contexto técnico

- **Lenguajes**: Python 3.12 y JavaScript ES2022.
- **Backend**: Flask 3, PyMongo 4, Werkzeug, `secrets` y SHA-256.
- **Persistencia**: MongoDB 8 en replica set; ClickHouse únicamente para analítica derivada.
- **Orquestación**: Airflow ejecuta cargas idempotentes sin sustituir la base operativa.
- **PDF**: generación en servidor después de filtrar y sanitizar la información.
- **Frontend**: navegación y acciones responsive según permisos efectivos.
- **Pruebas**: pytest unitario, de contrato, integración y flujo completo.

## Verificación de la constitución

- [x] La inicialización crea un solo administrador inicial.
- [x] Las contraseñas usan `scrypt` con salt individual.
- [x] MongoDB conserva el hash del token, no el token de sesión.
- [x] PAN y CVV se rechazan y nunca se persisten.
- [x] Pagos y reembolsos usan claves de idempotencia únicas.
- [x] El backend valida permisos aunque la interfaz oculte la acción.
- [x] Auditoría e informes sanitizan los datos antes de mostrarlos o exportarlos.

## Arquitectura y estructura

```text
backend/modules/security/   # usuarios, roles, sesiones, auditoría y PDF
backend/modules/payments/   # pagos, reembolsos y adaptador sandbox
backend/modules/reports/    # vista previa, PDF y estado analítico
backend/auth/               # decoradores de autenticación y autorización
frontend/js/modules/        # seguridad, administración, pagos e informes
analytics/airflow/          # DAG de carga analítica idempotente
tests/{unit,contract,integration}/
```

## Persistencia e índices

- `users`: identidad, hash de contraseña, roles, estado e intentos fallidos.
- `roles`: código, nombre, permisos y condición de rol del sistema.
- `auth_sessions`: hash del token, expiración y revocación; índice TTL.
- `audit_events`: actor, acción, entidad, resultado y metadatos sanitizados.
- `payments` y `refunds`: resultado, referencia segura, actor e idempotencia.
- `settings`: clave validada, valor, actor y fechas.
- Email, rol, sesión e idempotencias usan índices únicos apropiados.

## Flujos de seguridad y pagos

1. Consultar el estado de instalación y permitir bootstrap solo si no existe administrador.
2. Autenticar, aplicar bloqueo por intentos y entregar un token opaco con expiración.
3. Resolver permisos desde roles y validar cada endpoint mediante decorador.
4. Registrar accesos, cambios y denegaciones con metadatos sanitizados.
5. Procesar un pago con clave idempotente y referencia tokenizada del método.
6. Para efectivo, exigir caja abierta y crear exactamente un movimiento conciliado.
7. Validar saldo y límites antes de registrar un reembolso idempotente.
8. Filtrar auditoría e informes antes de previsualizar o generar PDF.

## Informes y canalización analítica

- MongoDB sigue siendo la fuente operativa y auditable.
- El constructor selecciona secciones y período antes de previsualizar.
- El PDF se genera desde la misma consulta filtrada mostrada al usuario.
- Airflow carga hechos derivados de manera repetible en ClickHouse.
- El estado analítico informa disponibilidad sin bloquear la operación comercial.

## Fases y artefactos

- **Fase 0 — Investigación**: credenciales, sesiones, tarjetas, RBAC e informes en [research.md](research.md).
- **Fase 1 — Diseño**: colecciones e índices en [data-model.md](data-model.md).
- **Fase 2 — Contrato**: seguridad, pagos e informes en [contracts/openapi.yaml](contracts/openapi.yaml).
- **Fase 3 — Implementación**: tareas y controles completados en [tasks.md](tasks.md).
- **Fase 4 — Validación**: recorrido de seguridad y pagos en [quickstart.md](quickstart.md).

## Estrategia de pruebas

- Unitarias: contraseñas, campos prohibidos, idempotencia y generación PDF.
- Contrato: bootstrap, login, usuarios, roles, pagos, auditoría e informes.
- Integración: RBAC, sesiones, caja, reembolsos y flujo completo.
- Regresión negativa: segundo bootstrap, token revocado, permiso omitido y PAN/CVV.

## Riesgos y controles

- **Robo de sesión**: token de alta entropía, hash persistido, expiración y revocación.
- **Datos de tarjeta**: rechazo temprano y persistencia solo de referencia/últimos cuatro.
- **Doble cargo o devolución**: clave idempotente e índice único.
- **Evasión de interfaz**: autorización definitiva en el servidor y auditoría del 403.
- **Datos sensibles en PDF**: filtros y sanitización antes del renderizado.

## Verificación constitucional posterior al diseño

PASS. El diseño aplica mínimo privilegio, defensa en profundidad, datos de pago mínimos,
idempotencia, trazabilidad y separación entre operación MongoDB y analítica derivada.
