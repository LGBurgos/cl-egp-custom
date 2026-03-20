# L10n AR Withholding Manual Amount

## Problema

En pagos de clientes, cuando se agrega una retención (ej: Retención Ganancias 2%), el sistema calcula automáticamente el monto basado en el porcentaje del impuesto. Sin embargo, el usuario necesita poder **editar manualmente** este monto en ciertos casos.

El módulo `l10n_ar_tax_fix` tiene un `@api.onchange` que recalcula el monto cada vez que hay cambios, sobrescribiendo cualquier edición manual del usuario.

## Solución

Este módulo agrega:

1. **Campo "Monto Manual"** (boolean) en las líneas de retención
2. **Lógica en el onchange** que respeta los montos marcados como manuales
3. **Botón "↺"** para volver al cálculo automático si se desea

## Cómo funciona

1. El usuario carga un pago y agrega una retención
2. El sistema calcula automáticamente el monto (ej: 2% de la base)
3. Si el usuario edita el monto manualmente → se marca "Manual = ✓"
4. El onchange ya NO sobrescribe ese monto
5. Si quiere volver al automático → click en botón "↺"

## Instalación

1. Copiar el módulo a `/home/odoo/src/user/`
2. Reiniciar Odoo
3. Actualizar lista de aplicaciones
4. Instalar "L10n AR Withholding Manual Amount"

## Dependencias

- `l10n_ar_tax_fix` (módulo de Hitofusion)

## Autor

Hitofusion - https://www.hitofusion.com

## Ticket relacionado

EGP - Impuesto ID 185 - Retención editable
