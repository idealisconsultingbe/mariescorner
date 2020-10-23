# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models

class StockLocation(models.Model):
    _inherit = 'stock.location'

    def should_bypass_reservation(self):
        """
        Override standard method
        By pass the reservation also for transit locations
        """
        return super(StockLocation, self).should_bypass_reservation() or self.usage == 'transit'
