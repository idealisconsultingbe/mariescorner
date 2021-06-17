# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from math import ceil
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    destination_usage = fields.Selection(related='picking_type_id.default_location_dest_id.usage', string='Destination Location Type', help="Technical field used in view", readonly=True)

    number_of_packages = fields.Integer(string='Number of Packages', compute='_compute_number_of_packages', store=True)
    manual_number_of_packages = fields.Integer(string='Manual Number of Packages')
    is_package_number_user_defined = fields.Boolean(string='User Defined Package Number', default=False)

    # changes to existing fields
    carrier_id = fields.Many2one('delivery.carrier', tracking=True)
    carrier_tracking_ref = fields.Char(tracking=True)
    scheduled_date = fields.Datetime(states={'cancel': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', states={'cancel': [('readonly', True)]}, tracking=True)

    @api.depends('is_package_number_user_defined',
                 'manual_number_of_packages',
                 'move_lines',
                 'move_lines.quantity_done',
                 'move_lines.product_uom',
                 'move_lines.product_id')
    def _compute_number_of_packages(self):
        for pick in self:
            if pick.is_package_number_user_defined:
                pick.number_of_packages = pick.manual_number_of_packages
            else:
                nb_packages = 0
                for line in pick.move_lines.filtered(
                        lambda line: line.product_id.categ_id.is_packed if line.product_id else False):
                    if line.product_uom.packaging_ratio == 0 or not line.product_uom.packaging_ratio:
                        continue
                    elif line.product_uom.packaging_ratio < 0:
                        nb_packages += 1
                    else:
                        nb_packages += ceil(line.quantity_done / line.product_uom.packaging_ratio)
                pick.number_of_packages = nb_packages

    def _set_scheduled_date(self):
        return super(StockPicking, self.filtered(lambda record: record.state != 'done'))._set_scheduled_date()
