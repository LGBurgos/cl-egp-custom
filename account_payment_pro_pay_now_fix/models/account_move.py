# © 2026 Hitofusion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, Command


class AccountMove(models.Model):
    _inherit = "account.move"

    def pay_now(self):
        """
        Override del método pay_now() para corregir el cálculo del monto.
        
        PROBLEMA ORIGINAL:
        El método original usa payment_difference para calcular el monto:
            payment.amount = abs(payment.payment_difference)
        
        Pero payment_difference depende de campos computados que no se evalúan
        correctamente por lazy evaluation cuando el pago recién se crea,
        resultando en monto = 0.
        
        SOLUCIÓN:
        Calcular el monto directamente desde las líneas abiertas
        (open_move_line_ids.amount_residual) en vez de usar payment_difference.
        
        Fix por Hitofusion - 2026-03-19
        """
        for rec in self.filtered(
            lambda x: x.pay_now_journal_id 
            and x.state == "posted" 
            and x.payment_state in ("not_paid", "partial")
        ):
            pay_journal = rec.pay_now_journal_id
            
            if rec.move_type in ["in_invoice", "in_refund"]:
                partner_type = "supplier"
            else:
                partner_type = "customer"

            payment_type = "inbound"
            payment_method = pay_journal._get_manual_payment_method_id(payment_type)

            # FIX: Forzar recomputo y obtener líneas directamente
            rec.invalidate_recordset(['open_move_line_ids'])
            open_lines = rec.open_move_line_ids
            
            # Si open_lines está vacío (puede pasar por timing), buscar directamente
            if not open_lines:
                open_lines = rec.line_ids.filtered(
                    lambda r: not r.reconciled
                    and r.account_id.account_type in self.env["account.payment"]._get_valid_payment_account_types()
                )
            
            # FIX: Calcular monto directamente en vez de usar payment_difference
            amount_residual = sum(open_lines.mapped('amount_residual'))
            difference = amount_residual * (-1.0 if partner_type == "supplier" else 1.0)

            # Si no hay monto a pagar, no crear pago
            if abs(difference) <= 0:
                continue

            # Crear el pago con el monto calculado directamente
            payment = (
                rec.env["account.payment"]
                .with_context(pay_now=True)
                .create(
                    {
                        "date": rec.invoice_date,
                        "partner_id": rec.commercial_partner_id.id,
                        "partner_type": partner_type,
                        "payment_type": payment_type,
                        "company_id": rec.company_id.id,
                        "journal_id": pay_journal.id,
                        "payment_method_id": payment_method.id,
                        "to_pay_move_line_ids": [Command.set(open_lines.ids)],
                        "memo": rec.payment_reference,
                    }
                )
            )

            # Ajustar tipo de pago según el signo del monto
            # - Factura proveedor o NC cliente → outbound (pagamos)
            # - Factura cliente o NC proveedor → inbound (cobramos)
            if partner_type == "supplier" and difference >= 0.0 or partner_type == "customer" and difference < 0.0:
                payment.payment_type = "outbound"
                payment.payment_method_id = pay_journal._get_manual_payment_method_id(payment_type).id

            # Setear el monto calculado
            payment.amount = abs(difference)
            
            # Confirmar el pago
            payment.action_post()
            
            # Vincular el pago a la factura
            rec.write({"matched_payment_ids": [(4, payment.id)]})
