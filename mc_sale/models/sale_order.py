# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, exceptions, models, _
from odoo.tools.misc import get_lang
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    carrier_id = fields.Many2one('delivery.carrier', compute='_compute_carrier_id', store=True, help='Automatically filled with the first shipping method available for current delivery address.')
    comment = fields.Html(string='Comment')
    delivery_comment = fields.Html(string='Delivery Comment')
    allowed_invoice_address_ids = fields.Many2many('res.partner', 'sale_order_allowed_invoice_address_rel', 'order_id', 'partner_id', string='Allowed Invoice Addresses', compute='_compute_allowed_addresses')
    allowed_shipping_address_ids = fields.Many2many('res.partner', 'sale_order_allowed_shipping_address_rel', 'order_id', 'partner_id', string='Allowed Shipping Addresses', compute='_compute_allowed_addresses')
    down_payment_paid = fields.Boolean(string='Down Payment Paid', default=False)
    date_order = fields.Datetime(states={'draft': [('readonly', False)], 'sent': [('readonly', False),], 'sale': [('readonly', False),]}, tracking=True) # modify standard parameters
    registered_date_order = fields.Datetime(string='Registered Order Date', readonly=True, copy=False, help="Date of the very first confirmation of current sale order.")

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
            carriers = self.env['delivery.carrier'].search(
                ['|', ('company_id', '=', False), ('company_id', '=', order.company_id.id)])
            available_carriers = carriers.available_carriers(
                order.partner_shipping_id) if order.partner_shipping_id else carriers
            order.carrier_id = available_carriers[0] if available_carriers else False

    @api.onchange('order_line', 'partner_id', 'partner_invoice_id', 'partner_shipping_id', 'payment_term_id', 'pricelist_id')
    def _onchange_date_order(self):
        """ order date of draft orders is updated when partner, order lines, payment terms of pricelist change """
        if self.state in ['draft', 'sent']:
            self.date_order = fields.Datetime.now()

    # Todo: date_order is updated with registered_date_order everytime or only at confirmation ?
    # def write(self, values):
    #     if 'date_order' in values and self.registered_date_order:
    #         values['date_order'] = self.registered_date_order
    #     return super(SaleOrder, self).write(values)

    @api.returns('self', lambda value: value.id)
    def copy(self, defaults=None):
        """ Copy registered date order and date order in case of revision (see module sale_revision_history)"""
        if not defaults:
            defaults = {}
        if self.env.context.get('sale_revision_history'):
            defaults.update({
                'registered_date_order': self.registered_date_order,
                'date_order': self.registered_date_order if self.registered_date_order else self.date_order})
        return super(SaleOrder, self).copy(defaults)

    def _action_confirm(self):
        """ When order is confirmed for the first time, register confirmation date.
        If the same order is confirmed another time (because of a revision or a cancellation & draft),
        then use the registered confirmation date as the new date order.
        """
        for order in self:
            # Send mail if order contains products that belongs to specific category.
            if len([x for x in order.order_line if x.product_id.categ_id.send_mail_order_confirmation]) > 0:
                template = self.env.ref('mc_sale.mail_template_send_mail_confirmation_order', raise_if_not_found=True)
                order.message_post_with_template(template.id)
            if not order.registered_date_order:
                order.registered_date_order = fields.Datetime.now()
            else:
                order.date_order = order.registered_date_order
        return super(SaleOrder, self)._action_confirm()

    def action_cancel(self):
        """
        Overridden method
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
