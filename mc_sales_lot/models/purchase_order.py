# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sales_lot_ids = fields.Many2many('stock.production.sales.lot', 'sales_lot_purchase_order_rel', 'po_id', 'sales_lot_id', string="Manufacturing Numbers")

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if vals.get('date_planned'):
            self.order_line.filtered(lambda line: not line.display_type).date_msc_planned = vals['date_planned']
        return res

    @api.model
    def _prepare_sale_order_line_data(self, line, company, sale_id):
        """ Overridden Method

            Generate the Sales Order Line values from the PO line.
            Add Stock Production Manufacturing Number to SO Line values.
            :param line : the origin Purchase Order Line
            :rtype line : purchase.order.line record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param sale_id : the id of the SO
        """
        res = super(PurchaseOrder, self)._prepare_sale_order_line_data(line, company, sale_id)
        # if all stock moves have the same Manufacturing Number then add it to values
        sales_lot = self.env['stock.production.sales.lot']
        sale_line = self.env['sale.order.line']
        if line.sale_line_id:
            sale_line = line.sale_line_id
        else:
            move_dest_ids = line.move_dest_ids
            if move_dest_ids:
                sale_line = move_dest_ids[0]._get_sale_line()
        if sale_line and sale_line.sales_lot_id:
            sales_lot = sale_line.sales_lot_id
        if not sales_lot:
            sales_lot = line.sales_lot_id
        if sales_lot:
            res['sales_lot_id'] = sales_lot.id
        return res

    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        """
        Overridden method

        Generate the Sales Order values from the PO
        Add sale order mandatory date to values
        """
        res = super(PurchaseOrder, self)._prepare_sale_order_data(name, partner, company, direct_delivery_address)
        if self.order_line:
            move_dest_ids = self.order_line.move_dest_ids
            if move_dest_ids:
                sale_line = move_dest_ids[0]._get_sale_line()
                if sale_line:
                    res['mandatory_date'] = sale_line.order_id.mandatory_date
        return res

    def button_confirm(self):
        """ Set automatically sales lot external state to 'To Produce' of each purchase order line at purchase order confirmation """
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            sales_lots = order.order_line.mapped('sales_lot_id').filtered(lambda lot: lot.supplier_type == 'external' and lot.external_state == 'to_produce')
            sales_lots.write({'external_state': 'in_manufacturing'})
        return res
