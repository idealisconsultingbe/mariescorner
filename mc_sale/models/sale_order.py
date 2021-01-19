# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    carrier_id = fields.Many2one('delivery.carrier', compute='_compute_carrier_id', store=True, help='Automatically filled with the first shipping method available for current delivery address.')
    comment = fields.Html(string="Comment")
    po_state = fields.Selection([
        ('none', 'None'),
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Purchase Order Status', compute='_compute_po_state')

    @api.depends('partner_shipping_id')
    def _compute_carrier_id(self):
        """ Compute shipping method according to delivery address """
        for order in self:
            carriers = self.env['delivery.carrier'].search(['|', ('company_id', '=', False), ('company_id', '=', order.company_id.id)])
            available_carriers = carriers.available_carriers(order.partner_shipping_id) if order.partner_shipping_id else carriers
            order.carrier_id = available_carriers[0] if available_carriers else False

    def _compute_po_state(self):
        """ Retrieve Purchase Order Status from related purchase order """
        for order in self:
            purchase_order = self._get_purchase_order()
            if not purchase_order or len(purchase_order) > 1:
                order.po_state = 'none'
            else:
                order.po_state = purchase_order.state

    def action_confirm_purchase_order(self):
        """ Ensure that there is only one purchase order related to this sale order and confirm it """
        self.ensure_one()
        purchase_order_id = self._get_purchase_order()
        if not purchase_order_id:
            raise UserError(_("There is no purchase order to confirm for this sale."))
        elif len(purchase_order_id) > 1:
            raise UserError(_('There is more than one purchase order to confirm for this sale.'))
        else:
            purchase_order_id.button_confirm()

    def _get_purchase_order(self):
        """ Retrieve purchase order(s) if there is a MTO product with buy route """
        self.ensure_one()
        purchase_order_ids = self.env['purchase.order']
        for line in self.order_line:
            purchase_order_lines = self.env['purchase.order.line'].search([('sale_line_id', '=', line.id)])
            if purchase_order_lines:
                purchase_order_ids = purchase_order_lines.mapped('order_id')
            if line.move_ids:
                move = line.move_ids[0]
                purchase_order_line = move._get_purchase_line_id()
                if purchase_order_line:
                    purchase_order_ids |= purchase_order_line.order_id
        return purchase_order_ids
