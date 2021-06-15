# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _default_volume_uom_name(self):
        return self.env['product.template']._get_volume_uom_name_from_ir_config_parameter()

    def _default_weight_uom_name(self):
        return self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    def _default_length_uom_name(self):
        uom = self.env.ref('uom.product_uom_cm', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.uom_categ_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'smaller')], limit=1)
        return uom.name

    product_weight = fields.Float(string='Product Weight', compute='_compute_product_info', store=True, readonly=False)
    weight_uom_name = fields.Char(string='Weight UoM Label', readonly=True, default=_default_weight_uom_name)

    product_volume = fields.Float(string='Product Volume', compute='_compute_product_info', store=True, readonly=False)
    volume_uom_name = fields.Char(string='Volume UoM Label', readonly=True, default=_default_volume_uom_name)

    length_uom_name = fields.Char(string='Length UoM Label', readonly=True, default=_default_length_uom_name)
    product_height = fields.Float(string='Product Height', compute='_compute_product_info', store=True, readonly=False)
    product_width = fields.Float(string='Product Width', compute='_compute_product_info', store=True, readonly=False)
    product_depth = fields.Float(string='Product Depth', compute='_compute_product_info', store=True, readonly=False)

    @api.depends('product_id.height', 'product_id.width', 'product_id.depth', 'product_id.volume', 'product_id.weight', 'product_uom_qty', 'state')
    def _compute_product_info(self):
        for move in self:
            if move.state == 'done':
                qty = move.quantity_done
            else:
                qty = move.product_uom_qty
            move.update({
                'product_height': move.product_id.height,
                'product_width': move.product_id.width,
                'product_depth': move.product_id.depth,
                'product_volume': move.product_id.volume * qty,
                'product_weight': move.product_id.weight * qty,
            })
