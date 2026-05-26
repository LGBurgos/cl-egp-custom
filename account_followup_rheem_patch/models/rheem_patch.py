from odoo import models
import logging

_logger = logging.getLogger(__name__)


class AccountReportPatch(models.AbstractModel):
    """
    Filtro para reportes - Excluye facturas pagadas a nivel de query
    Aplicado a TODOS los clientes (20/05/2026 FINAL v3)
    Filtra SIEMPRE, no solo cuando unreconciled=True
    """
    _inherit = 'account.report'

    def _get_report_query(self, options, date_scope, domain=None):
        """
        Override para agregar filtro de facturas pagadas
        Filtra en reportes de seguimiento/partner ledger/customer statement
        """
        # Verificar si es un reporte relacionado con partners
        report_name = self.name if hasattr(self, 'name') else ''
        is_partner_report = any(x in report_name.lower() for x in ['followup', 'partner ledger', 'customer statement'])
        
        # CAMBIO: Filtrar SIEMPRE en reportes de partners, no solo cuando unreconciled=True
        if is_partner_report:
            _logger.info(f"[FOLLOWUP_FILTER] Aplicando filtro en reporte: {report_name}")
            
            # Agregar dominio para excluir facturas pagadas
            if domain is None:
                domain = []
            
            domain += [
                '|',
                    ('move_id.payment_state', 'not in', ['paid', 'in_payment']),
                    ('move_id.payment_state', '=', False)
            ]
            
            _logger.info(f"[FOLLOWUP_FILTER] Dominio modificado")
        
        return super()._get_report_query(options, date_scope, domain=domain)
