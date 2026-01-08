from odoo import models, api, fields
from datetime import datetime, timedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _is_overdue(self):
        """
        Validar si una factura está realmente vencida (no pagada)
        """
        self.ensure_one()
        
        # Excluir facturas pagadas
        if self.payment_state == 'paid':
            return False
        
        # Excluir facturas en estado borrador o canceladas
        if self.state not in ['posted']:
            return False
        
        # Verificar que sea una factura de cliente
        if self.move_type != 'out_invoice':
            return False
        
        return True


class AccountFollowupFollowupLine(models.Model):
    _inherit = 'account_followup.followup.line'

    def _get_overdue_invoices(self, partner, company_id):
        """
        Override para excluir facturas pagadas del seguimiento de vencidas
        """
        # Obtener las facturas vencidas base
        overdue_invoices = super()._get_overdue_invoices(partner, company_id)
        
        # Filtrar solo facturas no pagadas
        # Usar payment_state para estar 100% seguro
        overdue_invoices = overdue_invoices.filtered(
            lambda inv: inv.payment_state not in ['paid', 'in_payment']
        )
        
        return overdue_invoices


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_overdue_invoices(self, company_id):
        """
        Obtener facturas vencidas excluyendo las pagadas
        """
        # Llamar al método del módulo base
        overdue = super()._get_overdue_invoices(company_id) if hasattr(super(), '_get_overdue_invoices') else self.env['account.move']
        
        if not overdue:
            # Si el método base no existe, obtener facturas manualmente
            overdue = self.env['account.move'].search([
                ('partner_id', '=', self.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('company_id', '=', company_id.id),
            ])
        
        # Excluir facturas pagadas
        overdue = overdue.filtered(lambda inv: inv.payment_state not in ['paid', 'in_payment'])
        
        return overdue


class AccountFollowupManualReminder(models.Model):
    _inherit = 'account_followup.manual_reminder'

    def _get_invoices_data(self):
        """
        Override para asegurar que solo se incluyen facturas no pagadas
        """
        result = super()._get_invoices_data() if hasattr(super(), '_get_invoices_data') else {}
        
        # Filtrar líneas para excluir facturas pagadas
        if hasattr(self, 'line_ids') and self.line_ids:
            self.line_ids = self.line_ids.filtered(
                lambda line: line.move_id and line.move_id.payment_state not in ['paid', 'in_payment']
            )
        
        return result

    def process_followup(self):
        """
        Override para asegurar que solo se procesan facturas no pagadas
        """
        # Limpiar cualquier factura pagada antes de procesar
        if self.line_ids:
            paid_lines = self.line_ids.filtered(
                lambda line: line.move_id and line.move_id.payment_state in ['paid', 'in_payment']
            )
            if paid_lines:
                # Remover facturas pagadas del recordatorio
                paid_lines.unlink()
        
        return super().process_followup()
