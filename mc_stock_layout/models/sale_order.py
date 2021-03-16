# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_default_volume_uom(self):
        return self.env['product.template']._get_volume_uom_name_from_ir_config_parameter()

    def _get_default_weight_uom(self):
        return self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    weight_uom_name = fields.Char(string='Weight unit of measure label', compute='_compute_weight_uom_name', readonly=True, default=_get_default_weight_uom)
    volume_uom_name = fields.Char(string='Volume unit of measure label', readonly=True, default=_get_default_volume_uom)

    def _compute_weight_uom_name(self):
        for package in self:
            package.weight_uom_name = self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()
