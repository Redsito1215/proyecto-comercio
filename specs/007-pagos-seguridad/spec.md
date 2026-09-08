# Especificación funcional: Pagos y seguridad

**Rama funcional**: `007-pagos-seguridad`
**Creada**: 2026-09-04
**Estado**: Completada y verificada

## Historias de usuario

### US1 - Cobrar electrónicamente con rapidez (P1)
Como cajero quiero registrar efectivo, tarjeta, billetera o transferencia de forma idempotente y conocer el resultado sin duplicar cargos.

**Prueba independiente**: procesar pagos aprobados y rechazados, repetir una clave de idempotencia y comprobar que existe un solo resultado persistido.

**Escenarios de aceptación**:

1. **Dada** una venta confirmada con saldo pendiente, **cuando** se procesa un medio válido, **entonces** se registra el resultado y se actualiza el saldo.
2. **Dada** una clave ya utilizada, **cuando** se repite la solicitud, **entonces** se devuelve el pago previo sin duplicarlo.
3. **Dado** un pago en efectivo, **entonces** se exige caja abierta y se crea un solo movimiento conciliado.

### US2 - Proteger credenciales y tarjetas (P1)
Como propietario quiero usuarios con contraseña robustamente derivada, sesiones expirables y ningún PAN/CVV almacenado.

**Prueba independiente**: crear el administrador inicial, iniciar sesión y revisar que solo existan hash de contraseña, hash de sesión y referencias tokenizadas.

**Escenarios de aceptación**:

1. **Dada** una instalación sin administrador, **cuando** se completa la inicialización, **entonces** no puede crearse un segundo administrador inicial.
2. **Dadas** credenciales válidas, **cuando** se inicia sesión, **entonces** se entrega un token opaco y MongoDB conserva únicamente su hash.
3. **Cuando** una solicitud contiene PAN o CVV, **entonces** se rechaza y esos datos no se persisten.

### US3 - Controlar acceso y auditar (P1)
Como auditor quiero roles de mínimo privilegio y un registro inmutable de accesos, cambios sensibles y pagos.

**Prueba independiente**: autenticar usuarios con roles diferentes, intentar una acción no autorizada y consultar el evento de auditoría correspondiente.

**Escenarios de aceptación**:

1. **Dado** un usuario sin permiso, **cuando** intenta una operación protegida, **entonces** recibe 403 y se registra el intento bloqueado.
2. **Dado** un administrador, **cuando** crea roles o usuarios, **entonces** las respuestas nunca contienen hashes ni contraseñas.
3. **Cuando** se genera un informe o PDF de auditoría, **entonces** se aplican permisos y filtros antes de entregar el documento.

### Casos límite

- Inicialización concurrente del administrador.
- Sesión expirada o revocada.
- Cinco intentos fallidos y posterior período de bloqueo.
- Pago superior al saldo pendiente de la venta.
- Reembolso superior al importe aprobado.
- Campos prohibidos ocultos dentro de una solicitud.
- Usuario que intenta acceder directamente a una ruta oculta en la interfaz.

## Requisitos funcionales
- **FR-001**: MUST aceptar efectivo, tarjeta tokenizada, billetera y transferencia.
- **FR-002**: MUST usar idempotencia en creación y confirmación para evitar cobros duplicados.
- **FR-003**: MUST registrar estado pendiente, aprobado, rechazado o reembolsado y referencia del proveedor.
- **FR-004**: MUST verificar que el total aprobado no supere el saldo de la venta.
- **FR-005**: MUST prohibir PAN, CVV y banda magnética en solicitudes y persistencia.
- **FR-006**: MUST conservar solo token/referencia opaca, marca y últimos cuatro cuando los entregue el proveedor.
- **FR-007**: MUST derivar contraseñas con salt y algoritmo resistente.
- **FR-008**: MUST bloquear temporalmente tras intentos fallidos repetidos.
- **FR-009**: MUST emitir sesiones aleatorias, almacenar únicamente su hash y aplicar expiración/revocación.
- **FR-010**: MUST autorizar mediante roles y permisos explícitos.
- **FR-011**: El administrador MUST poder consultar usuarios y roles sin exponer credenciales.
- **FR-012**: El administrador MUST poder mantener parámetros generales del negocio y auditar cada cambio.
- **FR-013**: MUST auditar autenticación, usuarios, permisos denegados, pagos y reembolsos.
- **FR-014**: MUST ocultar secretos y datos personales en respuestas y logs.
- **FR-015**: MUST distinguir claramente el adaptador sandbox de un proveedor real.
- **FR-016**: MUST incluir cabeceras HTTP defensivas.
- **FR-017**: MUST exigir una caja abierta y crear exactamente un movimiento de caja por cada pago en efectivo aprobado.
- **FR-018**: El registro de pagos MUST permitir seleccionar una venta confirmada con saldo pendiente mostrando número, cliente, total y valor por cobrar.
- **FR-019**: Todo pago aprobado MUST permitir generar un comprobante PDF interno con negocio, venta, cliente, líneas, total, medio, importe pagado y saldo, rotulado como documento no tributario.

## Criterios de éxito
- **SC-001**: Ninguna colección contiene PAN o CVV.
- **SC-002**: Repetir una confirmación con la misma clave devuelve el mismo pago sin duplicarlo.
- **SC-003**: Un usuario sin permiso recibe 403 fuera del entorno de desarrollo.
- **SC-004**: Cinco intentos fallidos bloquean temporalmente la cuenta.
- **SC-005**: Toda operación sensible produce un evento de auditoría.
- **SC-006**: La interfaz oculta módulos y acciones no permitidos y el backend conserva la autorización definitiva.
- **SC-007**: Un pago en efectivo aprobado queda conciliado con su sesión de caja sin duplicarse al reintentar.

## Supuestos
- El adaptador incluido es sandbox local; producción requiere credenciales de un adquirente certificado.
- HTTPS termina en el proxy de despliegue; la aplicación aplica cabeceras compatibles.

## Fuera de alcance

- Procesar tarjetas reales con el adaptador de demostración.
- Almacenar números completos de tarjeta, CVV o banda magnética.
- Confiar en la ocultación visual como sustituto de la autorización del backend.
