# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Sales Lot', copy=False)
    sales_lot_id_required = fields.Boolean(string='Sales Lot Required', compute='_compute_sales_lot_id_required')
    # sales_lot_number = fields.Char(string='Sales Lot Number')
    has_tracking = fields.Selection(related='product_id.tracking', string='Product with Tracking')

    @api.depends('product_id', 'has_tracking')
    def _compute_sales_lot_id_required(self):
        """ According to this field, "Sales Lot" readonly and required field attributes will be set True
        on a sale order line from its order form view, or not.
        """
        automatic_lot_enabled = self.user_has_groups('mc_sales_lot.group_automatic_sales_lot')
        production_lot_enabled = self.user_has_groups('stock.group_production_lot')
        sales_lot_id_required = (production_lot_enabled and not automatic_lot_enabled)
        for line in self:
            if not line.product_id:
                line.sales_lot_id_required = False
            else:
                line.sales_lot_id_required = sales_lot_id_required and line.has_tracking != 'none' and line.product_id.sales_lot_activated

    @api.constrains('sales_lot_id')
    def _check_sales_lot_id(self):
        """ Prevent user to force an order line without a Sales Lot """
        for line in self:
            if line.sales_lot_id_required and not line.sales_lot_id:
                raise ValidationError(_('Sales Lot Number is mandatory ({} product).').format(line.product_id.name))
