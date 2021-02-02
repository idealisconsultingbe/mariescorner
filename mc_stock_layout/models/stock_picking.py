# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_default_volume_uom(self):
        return self.env['product.template']._get_volume_uom_name_from_ir_config_parameter()

    volume_uom_name = fields.Char(string='Volume unit of measure label', readonly=True, default=_get_default_volume_uom)
