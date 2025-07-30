from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    internal_notes = fields.Html(string='Notas Internas')


    def button_confirm(self):
        res = super().button_confirm()

        for order in self:
            for picking in order.picking_ids:
                for move in picking.move_ids_without_package:
                    purchase_line = move.purchase_line_id
                    if purchase_line and purchase_line.custom_description:
                        move.description_picking = purchase_line.custom_description

        return res


    def action_create_invoice(self):
        res = super().action_create_invoice()

        for order in self:
            for invoice in order.invoice_ids:
                for inv_line in invoice.invoice_line_ids:
                    po_line = inv_line.purchase_line_id
                    if po_line and hasattr(po_line, 'custom_description') and hasattr(inv_line, 'custom_description'):
                        inv_line.custom_description = po_line.custom_description

        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    custom_description = fields.Text(string="Descripción adicional")