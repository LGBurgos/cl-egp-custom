from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    team_id = fields.Many2one('crm.team', compute='_compute_team_from_user', inverse='_inverse_team_from_user', store=True, string="Equipo de ventas")

    @api.depends('user_ids.sale_team_id')
    def _compute_team_from_user(self):
        """Calcular equipo de ventas basado en el usuario asociado"""
        for partner in self:
            if partner.user_ids:
                user_with_team = partner.user_ids.filtered('sale_team_id')
                partner.team_id = user_with_team[0].sale_team_id if user_with_team else False
            else:
                partner.team_id = False

    def _inverse_team_from_user(self):
        """Actualizar equipo de ventas en usuarios asociados"""
        for partner in self:
            if partner.user_ids and partner.team_id:
                partner.user_ids.write({'sale_team_id': partner.team_id.id})