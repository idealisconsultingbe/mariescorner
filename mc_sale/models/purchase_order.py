# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_planned = fields.Datetime(tracking=True)

    @api.model
    def _prepare_picking(self):
        """
        In case of drop shipping set as partner id of the picking the delivery address
        """
        res = super(PurchaseOrder, self)._prepare_picking()
        if self.picking_type_id.default_location_dest_id.usage == 'customer' and self.dest_address_id:
            res['partner_id'] = self.dest_address_id.id
        return res

    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        """
            Overridden Method
            Generate the Sales Order values from the PO
            Add origin to sale order values
            :param name : the origin client reference
            :rtype name : string
            :param partner : the partner reprenseting the company
            :rtype partner : res.partner record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param direct_delivery_address : the address of the SO
            :rtype direct_delivery_address : res.partner record
        """
        res = super(PurchaseOrder, self)._prepare_sale_order_data(name, partner, company, direct_delivery_address)
        carriers = self.order_line.mapped('sales_lot_id.carrier_id')
        if carriers:
            res['carrier_id'] = carriers[0].id
        res['origin'] = self.origin
        return res

    @api.model
    def _prepare_sale_order_line_data(self, line, company, sale_id):
        """ Overridden Method

            Generate the Sales Order Line values from the PO line.
            Add short description to SO Line values.
            :param line : the origin Purchase Order Line
            :rtype line : purchase.order.line record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param sale_id : the id of the SO
        """
        res = super(PurchaseOrder, self)._prepare_sale_order_line_data(line, company, sale_id)
        res['short_name'] = line.short_name or ''
        return res
