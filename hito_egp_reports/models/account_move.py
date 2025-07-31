from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    price_dolar = fields.Float(string="Dólar hoy")

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        invoice_date = defaults.get('invoice_date', fields.Date.context_today(self))
        usd_currency = self.env['res.currency'].sudo().search([('name', '=', 'USD')], limit=1)
        price_dolar = 1.0

        if invoice_date and usd_currency:
            rate = self.env['res.currency.rate'].sudo().search([
                ('currency_id', '=', usd_currency.id),
                ('name', '<=', invoice_date)
            ], order="name desc", limit=1)
            if rate:
                price_dolar = rate.inverse_company_rate

        defaults['price_dolar'] = price_dolar

        _logger.info(f"[DEFAULT_GET] Factura nueva con fecha {invoice_date} — Dólar aplicado: {price_dolar}")
        return defaults


    @api.onchange('invoice_date')
    def onchange_compute_dolar_price(self):
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
