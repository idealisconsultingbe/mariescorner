# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, exceptions, models, _
from odoo.tools.misc import get_lang


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    carrier_id = fields.Many2one('delivery.carrier', compute='_compute_carrier_id', store=True, help='Automatically filled with the first shipping method available for current delivery address.')
    comment = fields.Html(string='Comment')
    delivery_comment = fields.Html(string='Delivery Comment')
    allowed_invoice_address_ids = fields.Many2many('res.partner', 'sale_order_allowed_invoice_address_rel', 'order_id', 'partner_id', string='Allowed Invoice Addresses', compute='_compute_allowed_addresses')
    allowed_shipping_address_ids = fields.Many2many('res.partner', 'sale_order_allowed_shipping_address_rel', 'order_id', 'partner_id', string='Allowed Shipping Addresses', compute='_compute_allowed_addresses')
    down_payment_paid = fields.Boolean(string='Down Payment Paid', default=False)
    date_order = fields.Datetime(states={'draft': [('readonly', False)], 'sent': [('readonly', False),], 'sale': [('readonly', False),]}, tracking=True) # modify standard parameters

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

    def action_cancel(self):
        """
        Cancel the PO linked.
        """
        for rec in self:
            po_id = rec._get_purchase_order()
            if po_id:
                po_id.button_cancel()
        res = super(SaleOrder, self).action_cancel()
        return res

    def action_compute_pricelist_discount(self):
        """
        Compute pricelist discounts on current sale order
        This action is only possible in draft state to prevent side effects
        """
        self.ensure_one()
        if self.state in ['draft', 'sent']:
            # Remove delivery products from the sales order because prices may have changed
            self._remove_delivery_line()
            for line in self.order_line:
                if self.pricelist_id.discount_policy == 'with_discount':
                    line.discount = 0.0
                product = line.product_id.with_context(
                    lang=get_lang(self.env, line.order_id.partner_id.lang).code,
                    partner=line.order_id.partner_id,
                    quantity=line.product_uom_qty,
                    date=line.order_id.date_order,
                    pricelist=line.order_id.pricelist_id.id,
                    uom=line.product_uom.id
                )
                if line.order_id.pricelist_id and line.order_id.partner_id:
                    line.price_unit = self.env['account.tax']._fix_tax_included_price_company(line._get_display_price(product), product.taxes_id, line.tax_id, line.company_id)
                line._onchange_discount()
