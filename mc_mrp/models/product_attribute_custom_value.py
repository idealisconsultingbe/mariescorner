# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductAttributeCustomValue(models.Model):
    _inherit = 'product.attribute.custom.value'

    sale_order_line_id = fields.Many2one('sale.order.line', copy=False) # Add copy False to standard field

    def unlink(self):
        """
        Allow to delete custom value link to a purchase order line
        """
        po_lines = self.env['purchase.order.line'].search([('product_custom_attribute_value_ids', 'in', self.ids)])
        po_lines.write({'product_custom_attribute_value_ids': [(3, pacv.id) for pacv in self]})
        return super(ProductAttributeCustomValue, self).unlink()
