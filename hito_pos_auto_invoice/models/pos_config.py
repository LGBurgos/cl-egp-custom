from odoo import fields, models, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    invoice_auto_check = fields.Boolean()
