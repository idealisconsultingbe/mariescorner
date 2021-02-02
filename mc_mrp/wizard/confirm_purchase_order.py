# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ConfirmPurchaseOrder(models.TransientModel):
    _name = 'confirm.purchase.order'
    _description = 'Confirm Purchase Order(s) Linked to the same Sale Order'

    @api.model
    def default_get(self, fields):
        res = super(ConfirmPurchaseOrder, self).default_get(fields)
        if 'purchase_order_ids' in fields and not res.get('purchase_order_ids') and res.get('sale_order_id'):
            sale_order = self.env['sale.order'].browse(res.get('sale_order_id'))
            res['purchase_order_ids'] = [(6, 0, sale_order._get_purchase_order().ids)]
        return res

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    company_id = fields.Many2one('res.company', string='Company', related='sale_order_id.company_id')
    purchase_order_ids = fields.Many2many('purchase.order', 'wiz_purchase_order_to_confirm_rel', 'wiz_id', 'order_id', string='Purchase Orders')
    show_confirmation_button = fields.Boolean(string='Confirmation Button Visibility', compute='_compute_show_confirmation_button')

    @api.depends('purchase_order_ids.to_be_confirmed')
    def _compute_show_confirmation_button(self):
        for wiz in self:
            wiz.show_confirmation_button = False
            if wiz.purchase_order_ids.filtered(lambda o: o.state in ['draft', 'sent'] and o.to_be_confirmed):
                wiz.show_confirmation_button = True

    def action_confirm(self):
        self.ensure_one()
        for order in self.purchase_order_ids.filtered(lambda o: o.state in ['draft', 'sent'] and o.to_be_confirmed):
            order.button_confirm()
