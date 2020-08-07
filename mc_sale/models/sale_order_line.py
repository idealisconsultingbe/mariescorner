# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Sales Lot')
    sales_lot_number_visible = fields.Boolean(string='Sales Lot Number Visible', compute='_compute_sales_lot_number_visible')
    sales_lot_number = fields.Char(string='Sales Lot Number')
    has_tracking = fields.Selection(related='product_id.tracking', string='Product with Tracking')

    @api.depends('product_id', 'has_tracking')
    def _compute_sales_lot_number_visible(self):
        """ According to this field, the field "Sales Lot Number" will be displayed
        on a sale order line from its order form view, or not.
        """
        automatic_lot_enabled = self.user_has_groups('mc_sale.group_automatic_sales_lot')
        production_lot_enabled = self.user_has_groups('stock.group_production_lot')
        sales_lot_number_visible = (production_lot_enabled and not automatic_lot_enabled)
        for line in self:
            if not line.product_id or line.sales_lot_id:
                line.sales_lot_number_visible = False
            else:
                line.sales_lot_number_visible = sales_lot_number_visible and line.has_tracking != 'none'

    @api.constrains('sales_lot_number')
    def _check_sales_lot_number(self):
        for line in self:
            if line.sales_lot_number_visible and not line.sales_lot_number:
                raise ValidationError(_('Sales Lot Number is mandatory ({} product).').format(line.product_id.name))

    # @api.constrains('product_uom_qty')
    # def _check_product_uom_qty(self):
    #     for line in self:
    #         if line.has_tracking == 'serial' and line.product_uom_qty > 1:
    #             raise ValidationError(_('Please restrain yourself to one UoM quantity per line with a product tracked by S/N ({} product).').format(line.product_id.name))
    #
