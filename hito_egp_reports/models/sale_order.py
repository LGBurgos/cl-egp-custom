from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    internal_notes = fields.Html(string='Notas Internas')