# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    carrier_id = fields.Many2one('delivery.carrier', compute='_compute_carrier_id', store=True, help='Automatically filled with the first shipping method available for current delivery address.')
    comment = fields.Html(string='Comment')
    allowed_invoice_address_ids = fields.Many2many('res.partner', 'sale_order_allowed_invoice_address_rel', 'order_id', 'partner_id', string='Allowed Invoice Addresses', compute='_compute_allowed_addresses')
    allowed_shipping_address_ids = fields.Many2many('res.partner', 'sale_order_allowed_shipping_address_rel', 'order_id', 'partner_id', string='Allowed Shipping Addresses', compute='_compute_allowed_addresses')

    @api.depends('partner_id')
    def _compute_allowed_addresses(self):
        """ Compute allowed shipping and invoice addresses according to partner information """
        for order in self:
            order.allowed_invoice_address_ids = False
            order.allowed_shipping_address_ids = False
            if order.partner_id:
                commercial_partner = order.partner_id.commercial_partner_id
                order.allowed_shipping_address_ids = self.env['res.partner'].search([('type', '=', 'delivery'), ('parent_id', '=', commercial_partner.id)])
                order.allowed_invoice_address_ids = self.env['res.partner'].search([('type', '=', 'invoice'), ('parent_id', '=', commercial_partner.id)])

    @api.depends('partner_shipping_id')
    def _compute_carrier_id(self):
        """ Compute shipping method according to delivery address """
        for order in self:
            carriers = self.env['delivery.carrier'].search(['|', ('company_id', '=', False), ('company_id', '=', order.company_id.id)])
            available_carriers = carriers.available_carriers(order.partner_shipping_id) if order.partner_shipping_id else carriers
            order.carrier_id = available_carriers[0] if available_carriers else False
