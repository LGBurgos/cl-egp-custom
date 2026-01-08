from odoo import models, fields
from odoo.tools.misc import formatLang, format_date
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class AccountFollowupReport(models.AbstractModel):
    _inherit = 'account.followup.report'

    def _get_followup_report_lines(self, options):
        """
        Override para excluir facturas pagadas del reporte de seguimiento.
        Filtra en el origen los apuntes contables de facturas que están pagadas.
        """
        _logger.info(f"[FOLLOWUP_REPORT] Generando líneas del reporte")
        
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []

        lang_code = partner.lang
        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        
        # FILTRO CLAVE: Solo obtener apuntes de facturas que NO estén pagadas
        for l in partner.unreconciled_aml_ids.sorted().filtered(lambda aml: not aml.currency_id.is_zero(aml.amount_residual_currency)):
            # FILTRO: Excluir si la factura padre está pagada
            if l.move_id.payment_state in ['paid', 'in_payment']:
                _logger.info(f"[FOLLOWUP_REPORT] SALTAR {l.move_id.name} - payment_state: {l.move_id.payment_state}")
                continue
            
            _logger.info(f"[FOLLOWUP_REPORT] INCLUIR {l.move_id.name} - payment_state: {l.move_id.payment_state}")
            
            if l.company_id in self.env.company.search([('id', 'child_of', self.env.context.get('allowed_company_ids', self.env.company.id))]):
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        
        # Rest of the original logic (same as parent)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            for aml in aml_recs:
                amount = aml.amount_residual_currency if aml.currency_id else aml.amount_residual
                invoice_date = {
                    'name': format_date(self.env, aml.move_id.invoice_date or aml.date, lang_code=lang_code),
                    'class': 'date',
                    'style': 'white-space:nowrap;text-align:left;',
                    'template': 'account_followup.line_template',
                }
                date_due = format_date(self.env, aml.date_maturity or aml.move_id.invoice_date or aml.date, lang_code=lang_code)
                total += amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += amount or 0
                date_due = {
                    'name': date_due, 'class': 'date',
                    'style': 'white-space:nowrap;text-align:left;',
                    'template': 'account_followup.line_template',
                }
                if is_overdue:
                    date_due['style'] += 'color: red;'
                if is_payment:
                    date_due = ''
                move_line_name = {
                    'name': self._followup_report_format_aml_name(aml.name, aml.move_id.ref),
                    'style': 'text-align:left; white-space:normal;',
                    'template': 'account_followup.line_template',
                }
                amount = {
                    'name': formatLang(self.env, amount, currency_obj=currency),
                    'style': 'text-align:right; white-space:normal;',
                    'template': 'account_followup.line_template',
                }
                line_num += 1
                invoice_origin = aml.move_id.invoice_origin or ''
                if len(invoice_origin) > 43:
                    invoice_origin = invoice_origin[:40] + '...'
                invoice_origin = {
                    'name': invoice_origin,
                    'style': 'text-align:center; white-space:normal;',
                    'template': 'account_followup.line_template',
                }
                columns = [
                    invoice_date,
                    date_due,
                    invoice_origin,
                    move_line_name,
                    amount,
                ]
                lines.append({
                    'id': aml.id,
                    'account_move': aml.move_id,
                    'name': aml.move_id.name,
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'columns': [isinstance(v, dict) and v or {'name': v, 'template': 'account_followup.line_template'} for v in columns],
                })
            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1

            cols = \
                [{
                    'name': v,
                    'template': 'account_followup.line_template',
                } for v in [''] * 3] + \
                [{
                    'name': v,
                    'style': 'text-align:right; white-space:normal; font-weight: bold;',
                    'template': 'account_followup.line_template',
                } for v in [total >= 0 and _('Total Due') or '', total_due]]

            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'style': 'border-top-style: double',
                'unfoldable': False,
                'level': 3,
                'columns': cols,
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                line_num += 1

                cols = \
                    [{
                        'name': v,
                        'template': 'account_followup.line_template',
                    } for v in [''] * 3] + \
                    [{
                        'name': v,
                        'style': 'text-align:right; white-space:normal; font-weight: bold;',
                        'template': 'account_followup.line_template',
                    } for v in [_('Total Overdue'), total_issued]]

                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 3,
                    'columns': cols,
                })

        return lines
