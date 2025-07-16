from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_brand_id = fields.Many2one(
        comodel_name="product.brand",
        string="Brand",
        related="product_template_id.product_brand_id",
        store=True,
        readonly=True,
    )

    delivery_time = fields.Char(string='Plazo de entrega (días)')