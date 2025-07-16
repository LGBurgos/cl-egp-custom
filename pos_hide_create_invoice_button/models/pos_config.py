from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    invoice_visibility = fields.Boolean(default=False)
