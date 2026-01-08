import logging
from odoo import models

_logger = logging.getLogger(__name__)


class AccountFollowupReport(models.AbstractModel):
    _inherit = "account.followup.report"

    def _get_partner_move_lines(self, partner):
        _logger.info(
            "[FOLLOWUP PATCH] Processing partner %s (ID %s)",
            partner.display_name,
            partner.id,
        )

        lines = super()._get_partner_move_lines(partner)

        _logger.info(
            "[FOLLOWUP PATCH] Initial move lines count: %s",
            len(lines),
        )

        filtered_lines = self.env["account.move.line"]

        for line in lines:
            move = line.move_id

            _logger.debug(
                "[FOLLOWUP PATCH] Checking AML %s | Move %s | Type %s | "
                "Payment state %s | Residual %s %s",
                line.id,
                move.name,
                move.move_type,
                move.payment_state,
                line.amount_residual,
                line.company_currency_id.name,
            )

            # Excluir facturas pagadas
            if (
                move.move_type in ("out_invoice", "out_refund")
                and move.payment_state == "paid"
            ):
                _logger.warning(
                    "[FOLLOWUP PATCH] EXCLUDED paid invoice | "
                    "AML %s | Invoice %s | Residual %s %s",
                    line.id,
                    move.name,
                    line.amount_residual,
                    line.company_currency_id.name,
                )
                continue

            filtered_lines |= line

        _logger.info(
            "[FOLLOWUP PATCH] Final move lines count: %s",
            len(filtered_lines),
        )

        return filtered_lines
