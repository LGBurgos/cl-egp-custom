from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    price_dolar = fields.Float(string="Dolar hoy", compute="compute_dolar_price")

    @api.depends('invoice_date')
    def compute_dolar_price(self):
        for rec in self:
            currency_id = self.env['res.currency'].sudo().search([('name', '=', 'USD')])
            initial_rate = currency_id.rate_ids.sudo().search([('name', '<=', rec.invoice_date)], limit=1)
            if initial_rate:
                rec.price_dolar = initial_rate.inverse_company_rate
            else:
                rec.price_dolar = 1
