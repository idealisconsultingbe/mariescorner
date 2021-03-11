# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_show_details(self):
        """
        Add context in the wizard for the automation of lot creation
        """
        action = super(StockMove, self).action_show_details()
        action['context'].update({
            'operations_create_lot': True,
        })
        return action
