# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrderMerge(models.TransientModel):
    _name = "sale.order.merge"
    _description = 'Merge Sale Orders'
                               
    merge_quatation = fields.Selection([
        ('merge_into_new_and_cancel', 'Create New Order and Cancel Selected Order.'),
    ], default='merge_into_new_and_cancel', string="Merge Type")
    
    order_ids = fields.Many2one('sale.order', string="Orders", domain="[('id', 'in', selected_sale_order_ids)]")

    selected_sale_order_ids = fields.Many2many(
        'sale.order', 
        compute='_compute_selected_sale_orders',
        string="Selected Sale Orders",
    )
    customer_id = fields.Many2one('res.partner', string='Cliente')



    @api.depends('merge_quatation')
    def _compute_selected_sale_orders(self):
        for record in self:
            sale_order_ids = self.env['sale.order'].browse(self._context.get('active_ids', []))
            record.selected_sale_order_ids = sale_order_ids.filtered(
                lambda order: order.state in ['draft', 'sent']
            )

    def merge_order(self):
        sale_order_ids = self.env['sale.order'].browse(self._context.get('active_ids'))

        if self.merge_quatation == 'merge_into_new_and_cancel':
            new_order_id = sale_order_ids[0].copy()
            new_order_id.write({'state': 'draft', 'partner_id': self.customer_id})
            order_id = self.env['sale.order'].search([('id', '=', sale_order_ids[0].id)])
            order_id.write({'state': 'cancel'})
            for order_id in sale_order_ids[1:]:
                for line in order_id.order_line:
                    line.copy(default={'order_id': new_order_id.id})
                del_order_id = self.env['sale.order'].search([('id', '=', order_id.id)])
                del_order_id.write({'state': 'cancel'})
