from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    internal_notes = fields.Html(string='Notas Internas')