# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    is_fabric_attribute = fields.Boolean(string='Is a Fabric Attribute')
    # one2one relationship
    product_attribute_id = fields.Many2one('product.attribute', string='Related Attribute', compute='_compute_product_attribute_id', inverse='_inverse_product_attribute_id', store=True, help='Changing this relationship will erase all links between values on this record and related ones.')
    product_attribute_ids = fields.One2many('product.attribute', 'product_attribute_id', readonly=True, help='Utility field, not used in UI')

    @api.depends('product_attribute_ids')
    def _compute_product_attribute_id(self):
        """ inverse method changes one2many field which triggers computation of 'pseudo' one2one field product_attribute_id """
        for attribute in self:
            if len(attribute.product_attribute_ids) > 0:
                attribute.product_attribute_id = attribute.product_attribute_ids[0]
            else:
                attribute.product_attribute_id = False

    def _inverse_product_attribute_id(self):
        """ changing one2one relationship erase all links between attribute values """
        for attribute in self:
            attribute.product_attribute_ids = [(6, 0, [attribute.product_attribute_id.id])]
            attribute.value_ids.write({'product_attribute_value_id': False})

    @api.onchange('product_attribute_id')
    def _onchange_product_attribute_id(self):
        """ Advise user to don't save changes if he doesn't want to lose all links between attribute values """
        # FIXME : if we change display_type, all relationships are erased too
        if self.product_attribute_id:
            return {'warning': {'title': _('Warning'), 'message': _(
                'Changing this relationship will erase all links between values on this record and related ones. Discard changes if you are not sure of what you are doing.')}}

    def write(self, vals):
        """ Overridden standard method
        Handle synchronization between related fields """
        # if new values are added to current attribute, create copy of them in related attribute
        if self.product_attribute_id and not self.env.context.get('is_synchronized', False):
            attribute_values = [list for list in vals.get('value_ids', []) if list[0] == 0]
            self.with_context(is_synchronized=True).product_attribute_id.write({'value_ids': attribute_values})
        res = super(ProductAttribute, self).write(vals)
        # synchronization
        if not self.env.context.get('is_synchronized', False):
            # attributes synchronization
            if self.product_attribute_id:
                # condition does not work with get() if 'is_fabric_attribute' is explicitly False
                if 'is_fabric_attribute' in vals:
                    self.with_context(is_synchronized=True).product_attribute_id.update({'is_fabric_attribute': vals.get('is_fabric_attribute')})
                if vals.get('display_type'):
                    self.with_context(is_synchronized=True).product_attribute_id.update({'display_type': vals.get('display_type')})
            # attribute values synchronization
            for value in vals.get('value_ids', []):
                # create synchronization
                if value[0] == 0:
                    name = value[2]['name']
                    # name is unique inside values of an attribute so it works as an identifier
                    self.value_ids.filtered(lambda v: v.name == name).update({'product_attribute_value_id': self.product_attribute_id.value_ids.filtered(lambda v: v.name == name).id})
                # update synchronization
                if value[0] == 1:
                    v = self.env['product.attribute.value'].browse(value[1])
                    if v.product_attribute_value_id:
                        update_vals = {key:value for (key,value) in value[2].items() if key in ('name', 'is_custom')}
                        v.product_attribute_value_id.update(update_vals)
        return res

