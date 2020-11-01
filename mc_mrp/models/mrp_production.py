# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_description = fields.Text(string='Product Description', compute='_compute_sale_information')
    show_sale_description = fields.Boolean(string='Is Description Visible', compute='_compute_sale_information')
    sale_comment = fields.Text(string='Comment', compute='_compute_sale_information')
    show_sale_comment = fields.Boolean(string='Is Comment Visible', compute='_compute_sale_information')

    def action_confirm(self):
        """ Overridden method
            If sale order confirmation creates a MO, then this MO is not automatically confirmed
        """
        if self.env.context.get('skip_mo_confirmation'):
            return False
        return super(MrpProduction, self).action_confirm()

    def _compute_sale_information(self):
        """ retrieve sale description at production creation """
        for production in self:
            production.sale_description = ""
            production.sale_comment = False
            production.show_sale_comment = False
            production.show_sale_description = False
            sale_line_id = production.move_dest_ids[0]._get_sale_line() if production.move_dest_ids else False
            if sale_line_id:
                if sale_line_id.name:
                    production.sale_description = sale_line_id.name
                    production.show_sale_description = True
                if sale_line_id.comment:
                    production.sale_comment = sale_line_id.comment
                    production.show_sale_comment = True

    def _get_moves_raw_values(self):
        """
        Overwritten standard method
        Add product_tmpl to condition in case of product missing and filter moves to prevent creation of empty moves
        """
        moves = []
        for production in self:
            factor = production.product_uom_id._compute_quantity(production.product_qty,
                                                                 production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor,
                                                    picking_type=production.bom_id.picking_type_id)
            for bom_line, line_data in lines:
                # changes here
                if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom' or \
                        (bom_line.product_id.type or bom_line.product_tmpl_id.type) not in ['product', 'consu']:
                    continue
                moves.append(production._get_move_raw_values(bom_line, line_data))
        # changes here
        # filter moves in order to ignore empty moves
        moves = [move for move in moves if move]
        return moves

    def _get_move_raw_values(self, bom_line, line_data):
        """
        Overridden method
        Add logic to generate move values for bom lines without product.
        If move values are generated from a sale order line, try to find a product matching product configuration
        If there are attributes values flagged as 'none values', preparation of move values is aborted to prevent creation
        of an unnecessary stock move
        """
        res = super(MrpProduction, self)._get_move_raw_values(bom_line, line_data)
        if not bom_line.product_id and bom_line.product_tmpl_id:
            sale_line_id = self.move_dest_ids[0]._get_sale_line() if self.move_dest_ids else False
            if sale_line_id:
                bom_line_attributes = bom_line.product_attribute_ids
                sale_line_attributes = sale_line_id.product_no_variant_attribute_value_ids.mapped('attribute_id')
                shared_attributes = bom_line_attributes & sale_line_attributes
                custom_attribute_values = sale_line_id.product_custom_attribute_value_ids
                # The goal is to make sure that current bom line attributes are present in sale line configuration
                if shared_attributes == bom_line_attributes:
                    # filter product attribute values (product.attribute.value) from sale line
                    # in order to keep only those which attribute (product.attribute) is present in bom line attributes
                    attribute_values = sale_line_id.product_no_variant_attribute_value_ids.mapped('product_attribute_value_id').filtered(lambda pav: pav.attribute_id in bom_line_attributes)
                    # if there is a none value in attribute values, move creation should be skipped
                    if attribute_values.filtered(lambda values: values.is_none_value):
                        return {}
                    # search for product template attribute values (product.template.attribute.value)
                    # with product attribute value (product.attribute.value) included in product attribute values related to previous result
                    # and same product template as the one on bom line
                    product_template_attribute_values = self.env['product.template.attribute.value'].search([('product_attribute_value_id', 'in', attribute_values.mapped('product_attribute_value_id').ids), ('product_tmpl_id', '=', bom_line.product_tmpl_id.id)])
                    # Search for variants corresponding to this product.template.attribute.value combinaition if not found creates it (only if allow dynamic attributes)
                    products = bom_line.product_tmpl_id._create_product_variant(product_template_attribute_values)
                    # if there is one and one product matching domain, add product to move values else raise an error
                    if products and len(products) == 1:
                        res['product_id'] = products.id
                        # if a product is found, check if there is a custom value for this particular attribute value.
                        # if so, try to convert it to a float or do nothing if it is not possible
                        pcav = custom_attribute_values.filtered(lambda v: v.custom_product_template_attribute_value_id.attribute_id in shared_attributes)
                        if len(pcav) == 1:
                            try:
                                res['product_uom_qty'] = float(pcav.custom_value)
                            except ValueError:
                                pass
                    else:
                        raise ValidationError(_('Cannot produce {}, there is no or several product variant related to this configuration: {}')
                                              .format(sale_line_id.product_template_id.name, product_template_attribute_values.mapped(lambda ptav: ptav.name_get()[0][1])))
                else:
                    res['product_tmpl_id'] = bom_line.product_tmpl_id.id
            else:
                res['product_tmpl_id'] = bom_line.product_tmpl_id.id
        return res
