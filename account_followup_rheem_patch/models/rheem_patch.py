from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class AccountReportPatch(models.AbstractModel):
    """
    Filtro para reportes de seguimiento/partner ledger/customer statement.
    - Excluye facturas pagadas (payment_state in paid/in_payment).
    - Usa 'reconciled=False' como criterio de pendiente en lugar de
      'full_reconcile_id=False', alineando el reporte con el Mayor de Clientes.
      Esto evita que líneas reconciliadas sin full_reconcile_id (causadas por
      el bug de secuencia de account_full_reconcile) aparezcan incorrectamente.
    """
    _inherit = 'account.report'

    def _get_report_query(self, options, date_scope, domain=None):
        """
        Filtra facturas pagadas en reportes de seguimiento/partner ledger.
        """
        report_name = self.name if hasattr(self, 'name') else ''
        is_partner_report = any(x in report_name.lower() for x in ['followup', 'partner ledger', 'customer statement'])

        if is_partner_report:
            _logger.info(f"[FOLLOWUP_FILTER] Aplicando filtro payment_state en reporte: {report_name}")
            if domain is None:
                domain = []
            domain += [
                '|',
                    ('move_id.payment_state', 'not in', ['paid', 'in_payment']),
                    ('move_id.payment_state', '=', False)
            ]

        return super()._get_report_query(options, date_scope, domain=domain)

    @api.model
    def _get_options_unreconciled_domain(self, options):
        """
        Corrige el criterio de "pendiente" del reporte de seguimiento combinando
        AMBAS condiciones: reconciled=False AND full_reconcile_id=False.

        El filtro nativo usa solo:
            full_reconcile_id=False AND balance!=0
        Esto incluye líneas con reconciled=True pero full_reconcile_id=NULL
        (bug de secuencia: el INSERT de full_reconcile falló pero reconciled quedó True).

        El filtro anterior (solo reconciled=False) resolvía ese caso pero causaba
        otro: líneas con reconciled=False pero full_reconcile_id asignado
        (bug inverso: el full_reconcile quedó asignado pero reconciled no se actualizó
        al deshacerse la conciliación via reversión de VARIO/CAMBI).
        Esas líneas aparecen en el reporte al importe total de la factura sin los pagos
        que las compensan, inflando el saldo del reporte.

        La combinación de ambos criterios excluye los dos tipos de inconsistencia:
        - reconciled=True  + full_reconcile_id=NULL  → excluido (reconciled=True)
        - reconciled=False + full_reconcile_id=5140  → excluido (full_reconcile_id!=False)
        - reconciled=False + full_reconcile_id=NULL  → incluido (genuinamente abierto)
        """
        if options.get('unreconciled'):
            return [
                ('reconciled', '=', False),
                ('full_reconcile_id', '=', False),
                ('balance', '!=', '0'),
            ]
        return []
