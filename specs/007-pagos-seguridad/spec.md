# Feature Specification: Pagos y seguridad

**Feature Branch**: `007-pagos-seguridad`  
**Created**: 2026-09-04  
**Status**: Ready for implementation

## User Stories

### US1 - Cobrar electrónicamente con rapidez (P1)
Como cajero quiero registrar efectivo, tarjeta, billetera o transferencia de forma idempotente y conocer el resultado sin duplicar cargos.

### US2 - Proteger credenciales y tarjetas (P1)
Como propietario quiero usuarios con contraseña robustamente derivada, sesiones expirables y ningún PAN/CVV almacenado.

### US3 - Controlar acceso y auditar (P1)
Como auditor quiero roles de mínimo privilegio y un registro inmutable de accesos, cambios sensibles y pagos.

## Functional Requirements
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
- **FR-011**: MUST auditar autenticación, usuarios, permisos, pagos y reembolsos.
- **FR-012**: MUST ocultar secretos y datos personales en respuestas y logs.
- **FR-013**: MUST distinguir claramente el adaptador sandbox de un proveedor real.
- **FR-014**: MUST incluir cabeceras HTTP defensivas.

## Success Criteria
- Ninguna colección contiene PAN o CVV.
- Repetir una confirmación con la misma clave devuelve el mismo pago sin duplicarlo.
- Un usuario sin permiso recibe 403 fuera del entorno de desarrollo.
- Cinco intentos fallidos bloquean temporalmente la cuenta.
- Toda operación sensible produce un evento de auditoría.

## Assumptions
- El adaptador incluido es sandbox local; producción requiere credenciales de un adquirente certificado.
- HTTPS termina en el proxy de despliegue; la aplicación aplica cabeceras compatibles.
