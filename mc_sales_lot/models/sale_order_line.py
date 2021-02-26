# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _default_allow_set_sales_lot(self):
        """
        :return: True if the sales lot should be set by the user manually.
        """
        automatic_lot_enabled = self.user_has_groups('mc_sales_lot.group_automatic_sales_lot')
        production_lot_enabled = self.user_has_groups('stock.group_production_lot')
        return (production_lot_enabled and not automatic_lot_enabled)

    manufacturing_state = fields.Selection(String='Manufacturing State', related='sales_lot_id.manufacturing_state')
    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Manufacturing Number', copy=False)
    sales_lot_id_required = fields.Boolean(string='Manufacturing Number Required', compute='_compute_sales_lot_id_required')
    sales_lot_id_needed = fields.Boolean(string='Manufacturing Number Needed', compute='_compute_sales_lot_id_required')
    allow_set_sales_lot_id = fields.Boolean(string='Manual Manufacturing Number', default=_default_allow_set_sales_lot)
    has_tracking = fields.Selection(related='product_id.tracking', string='Product with Tracking')
    fabric_purchase_order_ids = fields.One2many('purchase.order', compute='_get_fabric_purchase_orders', string="Fabric Order(s)")

    def _get_fabric_purchase_orders(self):
        for line in self:
            line.fabric_purchase_order_ids = line.sales_lot_id.fabric_purchase_order_ids.filtered(lambda po: po.company_id == line.company_id)

    @api.depends('product_id', 'has_tracking', 'allow_set_sales_lot_id')
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
                line.sales_lot_id_needed = False
            else:
                line.sales_lot_id_required = sales_lot_id_required and line.has_tracking != 'none' and line.product_id.sales_lot_activated
                line.sales_lot_id_needed = line.allow_set_sales_lot_id and line.has_tracking != 'none' and line.product_id.sales_lot_activated

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
            'carrier_id': self.order_id.carrier_id.id,
            'origin_sale_order_line_id': self.id,
            'product_qty': self.product_uom_qty,
        }
        return values

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overridden method
        Create automatically a new sales lot for each lines in sale order state with tracking and sales lot activated on product
        only if there is no sales lot already and automatic creation of sales lot is set
        """
        if self.user_has_groups('mc_sales_lot.group_automatic_sales_lot'):
            for val in vals_list:
                order = self.env['sale.order'].browse(val['order_id']) if val.get('order_id', False) else False
                product = self.env['product.product'].browse(val['product_id']) if val.get('product_id') else False
                if order and order.state in ['sale', 'done'] and product:
                    if product.tracking and not val.get('sales_lot_id', False) and product.sales_lot_activated:
                        sales_lot = self.env['stock.production.sales.lot'].create({'name': '/', 'product_id': product.id, 'partner_id': order.partner_shipping_id.id})
                        val.update({'sales_lot_id': sales_lot.id})
        lines = super(SaleOrderLine, self).create(vals_list)
        if self.user_has_groups('mc_sales_lot.group_automatic_sales_lot'):
            for line in lines.filtered(lambda l: l.sales_lot_id and l.sales_lot_id.name == '/'):
                values = line._prepare_sales_lot_id()
                line.sales_lot_id.write(values)
        return lines

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
        if self.product_id.sales_lot_activated and self.sales_lot_id:
            values['sales_lot_id'] = self.sales_lot_id.id
        return values
