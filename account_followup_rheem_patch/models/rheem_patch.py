from odoo import models
import logging

_logger = logging.getLogger(__name__)


class AccountFollowupReportRheemPatch(models.AbstractModel):
    """
    Parche para RHEEM S.A. ÚNICAMENTE
    Excluye facturas con payment_state = 'paid' o 'in_payment'
    """
    _inherit = 'account.followup.report'

    def _get_followup_report_lines(self, options):
        """
        Excluir facturas pagadas de RHEEM S.A. del reporte de seguimiento
        """
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return super()._get_followup_report_lines(options)
        
        # SOLO para RHEEM S.A.
        if partner.vat != '30612958528':
            return super()._get_followup_report_lines(options)
        
        _logger.info(f"[RHEEM_PATCH] Aplicando filtro a {partner.name}")
        
        lines = super()._get_followup_report_lines(options)
        
        if not lines:
            return lines
        
        _logger.info(f"[RHEEM_PATCH] Total líneas antes: {len(lines)}")
        
        # Filtrar: excluir facturas pagadas
        filtered_lines = []
        for line in lines:
            # Mantener líneas de totales y pagos
            if line.get('class') == 'total' or line.get('type') == 'payment':
                filtered_lines.append(line)
                continue
            
            # Filtrar por payment_state
            if 'move_id' in line and line['move_id']:
                move = self.env['account.move'].browse(line['move_id'])
                if move.payment_state not in ['paid', 'in_payment']:
                    _logger.info(f"[RHEEM_PATCH] INCLUIR {move.name} ({move.payment_state})")
                    filtered_lines.append(line)
                else:
                    _logger.info(f"[RHEEM_PATCH] EXCLUIR {move.name} ({move.payment_state})")
            else:
                filtered_lines.append(line)
        
        _logger.info(f"[RHEEM_PATCH] Total líneas después: {len(filtered_lines)}")
        return filtered_lines
