# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict')
    route_id = fields.Many2one('stock.location.route', string='Route', ondelete='restrict', check_company=True, company_dependent=True)