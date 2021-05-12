# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_planned = fields.Datetime(tracking=True)

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
