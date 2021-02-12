# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_picking_by_carrier(self):
        """
        Group picking by carrier
        :return: {carrier_name: recordset_of_pickings}
        """
        pickings_by_carrier = {}
        for picking in self:
            if picking.carrier_id and picking.carrier_id.name in pickings_by_carrier:
                pickings_by_carrier[picking.carrier_id.name] |= picking
            elif picking.carrier_id:
                pickings_by_carrier[picking.carrier_id.name] = picking
            else:
                if 'Undefined' not in pickings_by_carrier:
                    pickings_by_carrier['Undefined'] = self.env['stock.picking']
                pickings_by_carrier['Undefined'] |= picking
        return pickings_by_carrier
