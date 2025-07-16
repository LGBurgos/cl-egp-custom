from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductNameLimitSettings(models.TransientModel):
    _name = 'product.name.limit.settings'
    _inherit = 'res.config.settings'

    product_name_char_limit = fields.Integer(
        string='Límite de caracteres para nombre del producto',
        config_parameter='product_name_limit.char_limit',
        default=30
    )

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('name')
    def _check_name_length(self):
        char_limit = int(self.env['ir.config_parameter'].sudo().get_param('product_name_limit.char_limit', default=30))
        for record in self:
            if record.name and len(record.name) > char_limit:
                raise ValidationError(f'El nombre del producto no puede tener más de {char_limit} caracteres.')