# -*- coding: utf-8 -*-

from odoo import models


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
            sale_line_id = self._get_sale_line(self.move_dest_ids[0])
            if sale_line_id:
                # filter product template attribute values (product.template.attribute.value) from sale line
                # in order to keed only those which attribute value (product.attribute.value) is related to
                # one of product template attribute values (product.attribute.value)
                attribute_values = sale_line_id.product_no_variant_attribute_value_ids.filtered(
                    lambda value: value.product_attribute_value_id.product_attribute_value_id in bom_line.product_tmpl_id.attribute_line_ids.mapped('value_ids'))
                # retrieve product attribute values (product.attribute.value) from previous result
                related_attribute_values = attribute_values.mapped('product_attribute_value_id.product_attribute_value_id')
                # search for product template attribute values (product.template.attribute.value)
                # with product attribute value (product.attribute.value) included in previous result
                # and same product template as the one on bom line
                product_template_attribute_values = self.env['product.template.attribute.value'].search([('product_attribute_value_id', 'in', related_attribute_values.ids), ('product_tmpl_id', '=', bom_line.product_tmpl_id.id)])
                # compute a domain to find products with those product template attribute values (product.template.attribute.value)
                domain = []
                for ptav in product_template_attribute_values:
                    domain.append(('product_template_attribute_value_ids', '=', ptav.id))
                products = self.env['product.product'].search(domain)
                # if there is one and one product matching domain, add product to move values else add product template instead
                if len(products) == 1:
                    res['product_id'] = products.id
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
        if move.sale_line_id:
            return move.sale_line_id
        else:
            raw_production = move.raw_material_production_id
            if raw_production and len(raw_production.move_dest_ids) == 1:
                return self._get_sale_line(raw_production.move_dest_ids)
            if raw_production and len(raw_production.move_finished_ids) == 1:
                return self._get_sale_line(raw_production.move_finished_ids)
            return False

