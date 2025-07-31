from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    price_dolar = fields.Float(string="Dolar hoy", compute="compute_dolar_price")

    @api.onchange('invoice_date')
    def _onchange_compute_dolar_price(self):
        usd_currency = self.env['res.currency'].sudo().search([('name', '=', 'USD')], limit=1)
        for rec in self:
            rec.price_dolar = 1.0  # Valor por defecto
            if rec.invoice_date and usd_currency:
                rate = self.env['res.currency.rate'].sudo().search([
                    ('currency_id', '=', usd_currency.id),
                    ('name', '<=', rec.invoice_date)
                ], order="name desc", limit=1)
                if rate:
                    rec.price_dolar = rate.inverse_company_rate



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    custom_description = fields.Text(string="Descripción adicional")
