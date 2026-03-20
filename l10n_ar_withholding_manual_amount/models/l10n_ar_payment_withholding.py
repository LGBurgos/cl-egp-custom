from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class L10nArPaymentWithholding(models.Model):
    _inherit = "l10n_ar.payment.withholding"

    manual_amount = fields.Boolean(
        string="Monto Manual",
        default=False,
        help="Si está marcado, el monto no se recalculará automáticamente. "
             "Se activa automáticamente cuando el usuario edita el monto manualmente."
    )

    @api.onchange("amount")
    def _onchange_amount_set_manual(self):
        """
        Cuando el usuario edita manualmente el monto, marcamos el flag.
        Esto evita que el onchange del pago lo sobrescriba.
        """
        # Solo marcar como manual si ya existe el registro (no es creación inicial)
        # y si el contexto no indica que es un cálculo automático
        if not self.env.context.get("auto_calculate_withholding"):
            for rec in self:
                if rec.amount and not rec.manual_amount:
                    # Verificamos si el monto difiere del calculado
                    if rec.tax_id and rec.base_amount:
                        calculated = rec.base_amount * rec.tax_id.amount / 100
                        # Si difiere más de 0.01, es edición manual
                        if abs(rec.amount - calculated) > 0.01:
                            rec.manual_amount = True
                            _logger.info(
                                f"Retención {rec.tax_id.name}: monto marcado como manual "
                                f"(ingresado: {rec.amount}, calculado: {calculated})"
                            )

    def action_reset_to_automatic(self):
        """
        Botón para volver al cálculo automático.
        Resetea el flag y recalcula el monto.
        """
        for rec in self:
            rec.manual_amount = False
            if rec.tax_id and rec.base_amount:
                rec.with_context(auto_calculate_withholding=True).amount = (
                    rec.base_amount * rec.tax_id.amount / 100
                )
                _logger.info(
                    f"Retención {rec.tax_id.name}: volvió a cálculo automático, "
                    f"nuevo monto: {rec.amount}"
                )
