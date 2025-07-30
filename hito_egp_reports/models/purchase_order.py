from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    internal_notes = fields.Html(string='Notas Internas')


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    custom_description = fields.Text(string="Descripción adicional")