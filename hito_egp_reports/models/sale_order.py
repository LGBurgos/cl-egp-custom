from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    internal_notes = fields.Html(string='Notas Internas')


    def action_confirm(self):
        res = super().action_confirm()

        for order in self:
            for picking in order.picking_ids:
                for move in picking.move_ids_without_package:
                    sale_line = move.sale_line_id
                    if sale_line and sale_line.custom_description:
                        move.description_picking = sale_line.custom_description

        return res

    @api.model
    def link_invoices_and_pickings(self):
        sales = self.search([])
        for sale in sales:
            pickings = sale.picking_ids.filtered(lambda p: p.sale_id)
            if not pickings:
                continue

            invoices = sale.invoice_ids.filtered(lambda m: m.move_type in ['out_invoice', 'out_refund'])
            if not invoices:
                continue

            for picking in pickings:
                for inv in invoices:
                    if inv.id not in picking.invoice_ids.ids:
                        picking.write({'invoice_ids': [(4, inv.id)]})

            for inv in invoices:
                for picking in pickings:
                    if picking.id not in inv.picking_ids.ids:
                        inv.write({'picking_ids': [(4, picking.id)]})




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    custom_description = fields.Text(string="Descripción adicional")




class SaleAdvancePaymentInvWizard(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        res = super().create_invoices()

        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for order in sale_orders:
            for invoice in order.invoice_ids:
                for inv_line in invoice.invoice_line_ids:
                    so_line = inv_line.sale_line_ids and inv_line.sale_line_ids[0] or False
                    if so_line and hasattr(so_line, 'custom_description') and hasattr(inv_line, 'custom_description'):
                        inv_line.custom_description = so_line.custom_description

        return res