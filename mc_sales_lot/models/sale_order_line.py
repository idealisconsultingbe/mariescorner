# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Manufacturing Number', copy=False)
    sales_lot_id_required = fields.Boolean(string='Manufacturing Number Required', compute='_compute_sales_lot_id_required')
    has_tracking = fields.Selection(related='product_id.tracking', string='Product with Tracking')

    @api.depends('product_id', 'has_tracking')
    def _compute_sales_lot_id_required(self):
        """ According to this field, "Manufacturing Number" readonly and required field attributes will be set True
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
        """ Prevent user to force an order line without a Manufacturing Number """
        for line in self:
            if line.sales_lot_id_required and not line.sales_lot_id:
                raise ValidationError(_('Manufacturing Number is mandatory ({} product).').format(line.product_id.name))

    def _prepare_sales_lot_id(self):
        """
        Prepare a dictionary for the creation of one sales lot.
        """
        self.ensure_one()
        name = self.env['ir.sequence'].next_by_code('stock.production.sales.lot')
        values = {
            'name': name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'partner_id': self.order_id.partner_id.id,
            'partner_shipping_id': self.order_id.partner_shipping_id.id,
            'origin_sale_order_id': self.order_id.id,
            'product_qty': self.product_uom_qty,
        }
        return values

    def _prepare_invoice_line(self):
        """
        Overridden method
        Add manufactuing number information to invoice line
        """
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.sales_lot_id:
            res['sales_lot_ids'] = [(4, self.sales_lot_id.id)]
        return res

    def _prepare_procurement_values(self, group_id=False):
        """
        Override standard method -> add the manufacturing number into the procurement.
        :return:
        """
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.product_id.sales_lot_activated:
            values['sales_lot_id'] = self.sales_lot_id
        return values
