# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from .tools import to_float
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round
from odoo.tools.misc import get_lang


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fabrics_meterage_needed = fields.Float(string='Meterage of fabrics', related='product_id.linear_length')
    product_sale_price = fields.Float(related='product_template_id.list_price', string='Standard Sale Price')
    comment = fields.Text(string='Comment')
    short_name = fields.Text(string='Short Description')
    price_unit = fields.Float(string='Customer Price')

    @api.onchange('product_id', 'product_uom_qty')
    def product_id_change(self):
        """
        Overridden method
        Update short description with product attributes flagged accordingly and description lines on product.template related
        """
        res = super(SaleOrderLine, self).product_id_change()

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        short_name = ''
        if self.product_id:
            short_name = self.product_id.product_tmpl_id.get_product_configurable_description(self.product_custom_attribute_value_ids, self.product_no_variant_attribute_value_ids, self.order_id.partner_id, product_qty=self.product_uom_qty, product_variant=self.product_id, display_custom=True)

        self.update({'short_name': short_name,
                     'list_price': product.list_price,})
        return res

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

