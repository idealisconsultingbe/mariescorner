# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    carrier_id = fields.Many2one('delivery.carrier', compute='_compute_carrier_id', store=True, help='Automatically filled with the first shipping method available for current delivery address.')
    comment = fields.Html(string="Comment")

    @api.depends('partner_shipping_id')
    def _compute_carrier_id(self):
        """ Compute shipping method according to delivery address """
        for order in self:
            carriers = self.env['delivery.carrier'].search(['|', ('company_id', '=', False), ('company_id', '=', order.company_id.id)])
            available_carriers = carriers.available_carriers(order.partner_shipping_id) if order.partner_shipping_id else carriers
            order.carrier_id = available_carriers[0] if available_carriers else False
