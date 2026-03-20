{
    "name": "Account Payment Pro - Pay Now Fix",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Fix para el método pay_now() que crea pagos con monto $0",
    "description": """
Account Payment Pro - Pay Now Fix
=================================

Problema que resuelve
---------------------
Al confirmar facturas con "Diario de pago directo" configurado, el pago 
automático se creaba con monto $0 y la factura quedaba como "No pagada".

Causa raíz
----------
El método pay_now() original usa payment_difference para calcular el monto.
Este campo computado no se evalúa correctamente por lazy evaluation del ORM
cuando el pago recién se crea, resultando en monto = 0.

Solución
--------
Override del método pay_now() que calcula el monto directamente desde las 
líneas abiertas (open_move_line_ids.amount_residual), evitando la dependencia 
de campos computados que pueden dar valores incorrectos.

Impacto
-------
- Solo afecta el método pay_now() de account.move
- No modifica el comportamiento de pagos manuales
- No afecta otras funcionalidades del módulo account_payment_pro

Autor: Hitofusion
Fecha: 2026-03-19
    """,
    "author": "Hitofusion",
    "website": "https://www.hitofusion.com",
    "license": "LGPL-3",
    "depends": ["account_payment_pro"],
    "data": [],
    "installable": True,
    "auto_install": False,
}
