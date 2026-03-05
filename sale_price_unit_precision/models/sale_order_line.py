from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit = fields.Float(
        string='Precio unitario',
        required=True,
        digits='Product Price',  # Respeta dinámicamente la precisión decimal configurada en Ajustes
        default=0.0,
    )
