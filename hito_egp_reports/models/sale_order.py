from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    internal_notes = fields.Html(string='Notas Internas')




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    custom_description = fields.Text(string="Descripción adicional")
