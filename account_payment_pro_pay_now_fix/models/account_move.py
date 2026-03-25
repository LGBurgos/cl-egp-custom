# © 2026 Hitofusion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, Command
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def pay_now(self):
        """
        Override del método pay_now() para corregir el cálculo del monto.
        FIX: No usar ._origin, calcular monto directamente.
        """
        _logger.info("[PAY_NOW_FIX] Método pay_now() OVERRIDE ejecutándose")
        
        for rec in self.filtered(
            lambda x: x.pay_now_journal_id 
            and x.state == "posted" 
            and x.payment_state in ("not_paid", "partial")
        ):
            _logger.info(f"[PAY_NOW_FIX] Procesando factura {rec.name} con journal {rec.pay_now_journal_id.name}")
            
            pay_journal = rec.pay_now_journal_id
            
            if rec.move_type in ["in_invoice", "in_refund"]:
                partner_type = "supplier"
            else:
                partner_type = "customer"

            payment_type = "inbound"
            payment_method = pay_journal._get_manual_payment_method_id(payment_type)

            # FIX: Obtener líneas directamente de la BD, NO usar ._origin
            open_lines = self.env['account.move.line'].search([
                ('move_id', '=', rec.id),
                ('account_type', 'in', ['asset_receivable', 'liability_payable']),
                ('reconciled', '=', False),
                ('amount_residual', '!=', 0)
            ])
            
            _logger.info(f"[PAY_NOW_FIX] Líneas encontradas: {open_lines.ids}")
            
            if not open_lines:
                _logger.warning(f"[PAY_NOW_FIX] No se encontraron líneas abiertas para {rec.name}")
                continue
            
            # FIX: Calcular monto directamente
            amount_residual = sum(open_lines.mapped('amount_residual'))
            difference = amount_residual * (-1.0 if partner_type == "supplier" else 1.0)
            
            _logger.info(f"[PAY_NOW_FIX] Monto calculado: {abs(difference)}")

            if abs(difference) <= 0:
                _logger.warning(f"[PAY_NOW_FIX] Monto es 0, no se crea pago")
                continue

            # Crear el pago con el monto correcto desde el inicio
            payment_vals = {
                "date": rec.invoice_date,
                "partner_id": rec.commercial_partner_id.id,
                "partner_type": partner_type,
                "payment_type": payment_type,
                "company_id": rec.company_id.id,
                "journal_id": pay_journal.id,
                "payment_method_id": payment_method.id,
                "to_pay_move_line_ids": [Command.set(open_lines.ids)],
                "memo": rec.payment_reference,
                "amount": abs(difference),  # FIX: Setear monto directamente en create
            }
            
            # Ajustar tipo de pago
            if partner_type == "supplier" and difference >= 0.0 or partner_type == "customer" and difference < 0.0:
                payment_vals["payment_type"] = "outbound"
                payment_vals["payment_method_id"] = pay_journal._get_manual_payment_method_id("outbound").id
            
            _logger.info(f"[PAY_NOW_FIX] Creando pago con vals: amount={payment_vals['amount']}")
            
            payment = rec.env["account.payment"].with_context(pay_now=True).create(payment_vals)
            
            _logger.info(f"[PAY_NOW_FIX] Pago creado: {payment.id}, amount: {payment.amount}")
            
            # Confirmar el pago
            payment.action_post()
            
            # Vincular el pago a la factura
            rec.write({"matched_payment_ids": [(4, payment.id)]})
            
            _logger.info(f"[PAY_NOW_FIX] Pago confirmado y vinculado a {rec.name}")
