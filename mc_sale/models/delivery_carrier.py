# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    route_id = fields.Many2one('stock.location.route', string='Route', ondelete='restrict', check_company=True, company_dependent=True)