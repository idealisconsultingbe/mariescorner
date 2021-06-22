# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.misc import get_lang


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fabrics_meterage_needed = fields.Float(string='Meterage of fabrics', related='product_id.linear_length')
    product_sale_price = fields.Float(related='product_template_id.list_price', string='Standard Sale Price')
    comment = fields.Text(string='Comment')
    short_name = fields.Text(string='Short Description')
    price_unit = fields.Float(string='Your Price')
    route_id = fields.Many2one('stock.location.route', compute='_compute_route_id', store=True, readonly=False)

    @api.depends('order_id.carrier_id.route_id', 'product_id')
    def _compute_route_id(self):
        for line in self:
            line.route_id = line.order_id.carrier_id.route_id if line.order_id.carrier_id else False

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_info(self):
        """
        Update short description with product attributes flagged accordingly and description lines on product.template related
        """
        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty or 1.0,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        short_name = ''
        if self.product_id:
            short_name = self.product_id.product_tmpl_id.get_product_configurable_description(
                self.product_custom_attribute_value_ids, self.product_no_variant_attribute_value_ids,
                self.order_id.partner_id, product_qty=self.product_uom_qty, product_variant=self.product_id,
                display_custom=True)

            # Retrieve extra description from delta between original short name and short name computed with original quantity
            short_name_with_origin_qty = self.product_id.product_tmpl_id.get_product_configurable_description(
                self.product_custom_attribute_value_ids, self.product_no_variant_attribute_value_ids,
                self.order_id.partner_id, product_qty=self._origin.product_uom_qty, product_variant=self.product_id,
                display_custom=True)
            if self._origin.short_name:
                extra_desc = '\n'.join([desc for desc in self._origin.short_name.split('\n') if desc not in short_name_with_origin_qty.split('\n')])
                if extra_desc:
                    short_name = short_name + "\n" + extra_desc

        self.update({'short_name': short_name,
                     'list_price': product.list_price,})

    def _prepare_invoice_line(self):
        """
        Overridden method
        Add short description to invoice line
        """
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.short_name:
            res['short_name'] = self.short_name
        return res

