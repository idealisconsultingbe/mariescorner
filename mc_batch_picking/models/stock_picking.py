# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_picking_by_carrier(self):
        """
        Group picking by carrier
        :return: {carrier_record: recordset_of_pickings}
        """
        pickings_by_carrier = {}
        carrier_model = self.env['delivery.carrier']
        for picking in self:
            if picking.carrier_id and picking.carrier_id in pickings_by_carrier:
                pickings_by_carrier[picking.carrier_id] |= picking
            elif picking.carrier_id:
                pickings_by_carrier[picking.carrier_id] = picking
            else:
                if carrier_model not in pickings_by_carrier:
                    pickings_by_carrier[carrier_model] = self.env['stock.picking']
                pickings_by_carrier[carrier_model] |= picking
        return pickings_by_carrier
