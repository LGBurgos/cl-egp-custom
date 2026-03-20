# Account Payment Pro - Pay Now Fix

## Descripción

Este módulo corrige un bug en el método `pay_now()` del módulo `account_payment_pro` que causaba que los pagos automáticos se crearan con monto $0.

## Problema

Al confirmar facturas con el campo "Diario de pago directo" configurado:
- El pago automático se creaba con monto $0
- La factura quedaba en estado "No pagada"
- El cliente debía crear el pago manualmente

## Causa Raíz

El método `pay_now()` original usa `payment.payment_difference` para calcular el monto del pago. Este campo computado depende de otros campos computados que no se evalúan correctamente por *lazy evaluation* del ORM cuando el pago recién se crea.

```python
# Código problemático original
difference = payment.payment_difference  # Devuelve 0 por lazy evaluation
payment.amount = abs(difference)         # Monto queda en 0
```

## Solución

El fix calcula el monto directamente desde `open_move_line_ids.amount_residual` **antes** de crear el pago:

```python
# Código corregido
open_lines = rec.open_move_line_ids
amount_residual = sum(open_lines.mapped('amount_residual'))
difference = amount_residual * (-1.0 if partner_type == "supplier" else 1.0)
# ... crear pago ...
payment.amount = abs(difference)  # Monto correcto
```

## Instalación

1. Copiar el módulo a la carpeta de addons
2. Actualizar la lista de aplicaciones
3. Instalar "Account Payment Pro - Pay Now Fix"

## Dependencias

- `account_payment_pro`

## Impacto

- ✅ Solo afecta facturas con "Diario de pago directo" configurado
- ✅ No modifica el comportamiento de pagos manuales
- ✅ No afecta otras funcionalidades
- ✅ Compatible con la funcionalidad existente

## Autor

Hitofusion - 2026-03-19
