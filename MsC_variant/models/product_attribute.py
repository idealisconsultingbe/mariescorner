# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    is_fabric_attribute = fields.Boolean(string='Is a Fabric Attribute')
    product_attribute_id = fields.Many2one('product.attribute', string='Related Attribute', compute='_compute_product_attribute_id', inverse='_inverse_product_attribute_id', store=True, help='Changing this relationship will erase all links between values on this record and related ones.')
    product_attribute_ids = fields.One2many('product.attribute', 'product_attribute_id', readonly=True, help='Utility field, not used in UI')

    @api.depends('product_attribute_ids')
    def _compute_product_attribute_id(self):
        for attribute in self:
            if len(attribute.product_attribute_ids) > 0:
                attribute.product_attribute_id = attribute.product_attribute_ids[0]
            else:
                attribute.product_attribute_id = False

    def _inverse_product_attribute_id(self):
        for attribute in self:
            attribute.product_attribute_ids = [(6, 0, [attribute.product_attribute_id.id])]
            attribute.value_ids.write({'product_attribute_value_id': False})

    @api.onchange('product_attribute_id')
    def _onchange_product_attribute_id(self):
        if self.product_attribute_id:
            return {'warning': {'title': _('Warning'), 'message': _(
                'Changing this relationship will erase all links between values on this record and related ones. Discard changes if you are not sure of what you are doing.')}}

    def write(self, vals):
        if self.product_attribute_id and not self.env.context.get('is_synchronized', False):
            res = [list for list in vals.get('value_ids', []) if list[0] == 0]
            self.with_context(is_synchronized=True).product_attribute_id.write({'value_ids': res})
        return super(ProductAttribute, self).write(vals)
