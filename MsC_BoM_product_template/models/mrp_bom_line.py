# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_id = fields.Many2one('product.product', required=False)
    # should be stored to prevent unwanted related=True behavior
    product_tmpl_id = fields.Many2one('product.template', store=True)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        """ Clear product field when product_tmpl changes """
        if self.product_id and self.product_tmpl_id and (self.product_tmpl_id != self.product_id.product_tmpl_id):
            temp = self.product_tmpl_id
            self.product_id = False
            self.update({'product_tmpl_id': temp})
