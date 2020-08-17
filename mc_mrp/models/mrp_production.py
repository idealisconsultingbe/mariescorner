# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_moves_raw_values(self):
        """
        Overwritten standard method
        Add product_tmpl to condition in case of product missing
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
        return moves

    def _get_move_raw_values(self, bom_line, line_data):
        """
        Overridden method
        Add logic to generate move values for bom lines without product.
        If move values are generated from a sale order line, try to find a product matching product configuration
        """
        res = super(MrpProduction, self)._get_move_raw_values(bom_line, line_data)
        if not bom_line.product_id and bom_line.product_tmpl_id:
            sale_line_id = self._get_sale_line(self.move_dest_ids[0] if self.move_dest_ids else False)
            if sale_line_id:
                bom_line_attributes = bom_line.product_attribute_ids
                sale_line_attributes = sale_line_id.product_no_variant_attribute_value_ids.mapped('attribute_id')
                # The goal is to make sure that current bom line attributes are present in sale line configuration
                if (bom_line_attributes & sale_line_attributes) == bom_line_attributes:
                    # filter product attribute values (product.attribute.value) from sale line
                    # in order to keep only those which attribute (product.attribute) is present in bom line attributes
                    attribute_values = sale_line_id.product_no_variant_attribute_value_ids.mapped('product_attribute_value_id').filtered(lambda pav: pav.attribute_id in bom_line_attributes)
                    # search for product template attribute values (product.template.attribute.value)
                    # with product attribute value (product.attribute.value) included in product attribute values related to previous result
                    # and same product template as the one on bom line
                    product_template_attribute_values = self.env['product.template.attribute.value'].search([('product_attribute_value_id', 'in', attribute_values.mapped('product_attribute_value_id').ids), ('product_tmpl_id', '=', bom_line.product_tmpl_id.id)])
                    # compute a domain to find products with those product template attribute values (product.template.attribute.value)
                    domain = []
                    for ptav in product_template_attribute_values:
                        domain.append(('product_template_attribute_value_ids', '=', ptav.id))
                    products = self.env['product.product'].search(domain)
                    # if there is one and one product matching domain, add product to move values else add product template instead
                    if len(products) == 1:
                        res['product_id'] = products.id
                    else:
                        raise ValidationError(_('Cannot produce {}, there is no BoM fabric related to this configuration: {}')
                                              .format(sale_line_id.product_template_id.name,
                                                      ', '.join(sale_line_id.product_no_variant_attribute_value_ids
                                                                .filtered(lambda pnvav: pnvav.attribute_id.has_linear_price).mapped('name'))))
                else:
                    res['product_tmpl_id'] = bom_line.product_tmpl_id.id
            else:
                res['product_tmpl_id'] = bom_line.product_tmpl_id.id
        return res

    def _get_sale_line(self, move):
        """
        Retrieve sale line from a move
        """
        self.ensure_one()
        if move and move.sale_line_id:
            if move.sale_line_id.product_no_variant_attribute_value_ids:
                return move.sale_line_id
            elif move.sale_line_id.order_id:
                try:
                    order_line = move.sale_line_id.order_id.auto_purchase_order_id.order_line
                except Exception:
                    return False
                if order_line.move_dest_ids and len(order_line.move_dest_ids) == 1:
                    return self._get_sale_line(order_line.move_dest_ids[0])
        if move.move_dest_ids and len(move.move_dest_ids) == 1:
            return self._get_sale_line(move.move_dest_ids[0])
        return False
