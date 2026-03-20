from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange("l10n_ar_withholding_line_ids")
    def _onchange_withholding_line_ids_calculate_amount(self):
        """
        OVERRIDE: Calcula el monto de retención automáticamente, 
        pero respeta los montos marcados como manuales.
        """
        for rec in self:
            if rec.l10n_ar_withholding_line_ids and rec.partner_type == 'customer':
                for line in rec.l10n_ar_withholding_line_ids:
                    # NUEVO: Verificar si el monto está marcado como manual
                    if line.manual_amount:
                        _logger.info(
                            f"Retención {line.tax_id.name}: monto manual, "
                            f"NO se recalcula (monto actual: {line.amount})"
                        )
                        continue  # No recalcular si es manual
                    
                    # Verificar si el impuesto es de tipo customer
                    if line.tax_id and line.tax_id.l10n_ar_type_tax_use == 'customer':
                        # Calcular el monto basado en el porcentaje del impuesto
                        tax_percentage = line.tax_id.amount
                        base_amount = rec.original_amount or rec.amount
                        
                        if base_amount and tax_percentage:
                            calculated_amount = base_amount * tax_percentage / 100
                            # Usar contexto para indicar que es cálculo automático
                            line.with_context(
                                auto_calculate_withholding=True
                            ).amount = calculated_amount
                            _logger.info(
                                f"Retención calculada: {base_amount} * {tax_percentage}% "
                                f"= {calculated_amount}"
                            )
