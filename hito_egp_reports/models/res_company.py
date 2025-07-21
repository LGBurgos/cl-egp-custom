from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"


    fondo_remito = fields.Binary(string='Marca de agua Remito')
    