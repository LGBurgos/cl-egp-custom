from odoo import models, fields, api, _

from odoo.tools.misc import formatLang

import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    price_dolar = fields.Float(string="Dólar hoy", tracking=True)

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


    def _l10n_ar_get_invoice_custom_tax_summary_for_report(self):
        """ Get a new tax details for RG 5614/2024 to show ARCA VAT and Other National Internal Taxes. """
        if self.l10n_latam_document_type_id.code not in ('6', '7', '8'):
            return []

        base_lines, _tax_lines = self._get_rounded_base_and_tax_lines()

        def grouping_function(base_line, tax_data):
            tax_group = tax_data['tax'].tax_group_id
            skip = False
            name = None
            if self._l10n_ar_is_tax_group_other_national_ind_tax(tax_group):
                if 'es_' in self.partner_id.lang:
                    name = _("Otros impuestos nacionales internos %s") % base_line['currency_id'].symbol
                else:
                # name = _("Other National Ind. Taxes %s", base_line['currency_id'].symbol)
                    name = _("Other National Ind. Taxes %s") % base_line['currency_id'].symbol
            elif self._l10n_ar_is_tax_group_vat(tax_group):
                if 'es_' in self.partner_id.lang:
                # name = _("VAT Content %s", base_line['currency_id'].symbol)
                    name = _("IVA Contenido %s") % base_line['currency_id'].symbol
                else:
                    name = _("VAT Content %s") % base_line['currency_id'].symbol
            else:
                skip = True
            return {
                'name': name,
                'skip': skip,
            }

        AccountTax = self.env['account.tax']
        base_lines_aggregated_values = AccountTax._aggregate_base_lines_tax_details(base_lines, grouping_function)
        values_per_grouping_key = AccountTax._aggregate_base_lines_aggregated_values(base_lines_aggregated_values)
        results = []
        for grouping_key, values in values_per_grouping_key.items():
            if (
                    grouping_key
                    and not grouping_key['skip']
                    and not self.currency_id.is_zero(values['tax_amount_currency'])
            ):
                results.append({
                    'name': grouping_key['name'],
                    'tax_amount_currency': values['tax_amount_currency'],
                    'formatted_tax_amount_currency': formatLang(self.env, values['tax_amount_currency']),
                })
        return results



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    custom_description = fields.Text(string="Descripción adicional")
