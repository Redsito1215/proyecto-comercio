# Research: Precios y márgenes

- **Decisión**: margen porcentual sobre venta: `(precio-costo)/precio*100`; evita ambigüedad con markup.
- **Decisión**: Decimal/Decimal128 y redondeo HALF_UP a dos decimales para dinero.
- **Decisión**: historial append-only en `price_changes`; el producto mantiene solo el valor vigente.
- **Decisión**: observaciones de mercado son evidencia fechada, nunca automatizan cambios.
- **Alternativa descartada**: usar `float`, por errores de representación monetaria.
