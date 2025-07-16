from odoo import fields, models, api, _

from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def open_unify_quote_wizard(self):
        sale_order_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
        if any(order_ids for order_ids in sale_order_ids if order_ids.state not in ['draft', 'sent']):
            raise UserError(('Seleccione sólo los pedidos en etapa de cotización/cotización envíada para unificar.'))
        partner_list = set([order_id.partner_id.name for order_id in sale_order_ids])
        if len(partner_list) > 1:
            raise UserError(('Por favor seleccione cotizaciones de un mismo cliente para unificar.'))

        return {
            'name': 'Unificar cotiazciones',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.merge',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_customer_id': sale_order_ids[0].partner_id.id},
        }
