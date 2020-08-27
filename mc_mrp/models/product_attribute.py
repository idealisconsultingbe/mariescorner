# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    product_attribute_id = fields.Many2one('product.attribute', string='Related Attribute')
    product_attribute_ids = fields.One2many('product.attribute', 'product_attribute_id', string='Related Attributes')
    relationship_type = fields.Selection([('o2m', 'One to Many'), ('m2o', 'Many to One'), ('none', 'None')], string='Relationship Type', compute='_compute_relationship_type', help='Utility field used in UI.')

    @api.depends('product_attribute_ids', 'product_attribute_id')
    def _compute_relationship_type(self):
        """ Compute relationship type in order to hide unwanted fields
            - if relationship_type = o2m, then m2o field should be hidden
            - if relationship_type = m2o, then o2m field should be hidden
            - else both fields should be visible
        """
        for attribute in self:
            if attribute.product_attribute_id:
                attribute.relationship_type = 'm2o'
            elif attribute.product_attribute_ids:
                attribute.relationship_type = 'o2m'
            else:
                attribute.relationship_type = 'none'

    @api.onchange('product_attribute_id', 'product_attribute_ids')
    def _onchange_product_attribute_id(self):
        """ Advise user to don't save changes if he doesn't want to lose all links between attribute values """
        # FIXME : if we change display_type, all relationships are erased too
        return {'warning': {'title': _('Warning'), 'message': _(
                'Changing this relationship will erase all links between values on this record and related ones. Discard changes if you are not sure of what you are doing.')}}

    @api.constrains('product_attribute_id', 'product_attribute_ids')
    def _check_product_attributes(self):
        """ Prevent user to use both product attribute relationships """
        for attribute in self:
            if attribute.product_attribute_id and attribute.product_attribute_ids:
                raise UserError(_('There is already a relationship set on this attribute ({}).').format(attribute.display_name))

    def write(self, vals):
        """ Overridden standard method
        Handle synchronization between related fields """
        # retrieve all attributes related to current one
        if self.product_attribute_id:
            # if current product attribute has a parent, then this parent and its children (minus current attribute) must be updated
            related_product_attributes = self.product_attribute_id + self.product_attribute_id.product_attribute_ids - self
        elif self.product_attribute_ids:
            # if current product attribute has children, then its children must be updated
            related_product_attributes = self.product_attribute_ids
        else:
            related_product_attributes = []

        # if relationship to other attribute(s) changes, then erase all relationships between attribute values
        if 'product_attribute_id' in vals or 'product_attribute_ids' in vals:
            self.value_ids.update({'product_attribute_value_id': False, 'product_attribute_value_ids': [(5, 0, 0)]})

        # if new values are added to current attribute, create copy of them in related attributes before establishing relationships
        # if values are deleted, delete them as well in related attributes before doing it on current attribute
        if related_product_attributes and not self.env.context.get('is_synchronized', False):
            # retrieve new values
            attribute_values = [list for list in vals.get('value_ids', []) if list[0] == 0] # list[0] = 0 is for new records -> (0, 0, values)
            for product_attribute in related_product_attributes:
                # write new values in related attributes and use a flag to prevent loops
                product_attribute.with_context(is_synchronized=True).write({'value_ids': attribute_values})
            # delete values
            attribute_values = [list for list in vals.get('value_ids', []) if list[0] == 2] # list[0] = 2 is for deleted records -> (2, id, 0)
            for value in attribute_values:
                v = self.env['product.attribute.value'].browse(value[1])
                for related_product_attribute in related_product_attributes:
                    pav_to_delete = self.env['product.attribute.value'].search(
                        [('attribute_id', '=', related_product_attribute.id), ('name', '=', v.name)])
                    related_product_attribute.with_context(is_synchronized=True).update(
                        {'value_ids': [(2, pav_to_delete.id or False)]})

        res = super(ProductAttribute, self).write(vals)

        # synchronization
        if not self.env.context.get('is_synchronized', False):

            # attributes synchronization
            for product_attribute in related_product_attributes:
                # condition does not work with get() if 'has_linear_price' is explicitly False
                # if 'has_linear_price' in vals:
                #     product_attribute.with_context(is_synchronized=True).update({'has_linear_price': vals.get('has_linear_price')})
                if vals.get('display_type'):
                    product_attribute.with_context(is_synchronized=True).update({'display_type': vals.get('display_type')})

            #attribute values synchronization
            for value in vals.get('value_ids', []):
                # create synchronization (product attribute level)
                if value[0] == 0:  # value[0] = 0 is for new records -> (0, 0, values)
                    # name is unique inside values of an attribute so it works as an identifier
                    name = value[2]['name']

                    if self.product_attribute_id:
                        # if current product attribute has a parent, update its children relationships
                        # there is no need to update parent relationship since changes on children will be reflected on parent
                        for product_attribute in self.product_attribute_id.product_attribute_ids:
                            product_attribute.value_ids.filtered(lambda v: v.name == name).update({'product_attribute_value_id': self.product_attribute_id.value_ids.filtered(lambda v: v.name == name).id})
                    if self.product_attribute_ids:
                        # if current product attribute has children, update children relationships
                        for product_attribute in self.product_attribute_ids:
                            product_attribute.value_ids.filtered(lambda v: v.name == name).update({'product_attribute_value_id': self.value_ids.filtered(lambda v: v.name == name).id})

                # update synchronization (product attribute value level)
                if value[0] == 1:  # value[0] = 1 is for updates -> (1, id, values)
                    # retrieve record to update
                    v = self.env['product.attribute.value'].browse(value[1])
                    # retrieve updated values
                    update_vals = {key: value for (key, value) in value[2].items() if key in ('name', 'is_none_value')}
                    # update_vals = {key: value for (key, value) in value[2].items() if key in ('name', 'is_custom', 'is_none_value')}
                    if v.product_attribute_value_id:
                        # if record has a parent, update parent values before updating children values
                        v.product_attribute_value_id.update(update_vals)
                        for pav in v.product_attribute_value_id.product_attribute_value_ids:
                            pav.update(update_vals)
                    if v.product_attribute_value_ids:
                        # if record has children, update children values
                        for pav in v.product_attribute_value_ids:
                            pav.update(update_vals)
        return res

