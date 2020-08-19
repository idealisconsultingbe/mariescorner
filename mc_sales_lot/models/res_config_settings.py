# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    extra_serial_digits = fields.Integer(String='S/N Extra Digits', help='Number digits to add to compose S/N', required=True,
                                              default=2, config_parameter='mc_sales_lot.additional_serial_number')
    group_automatic_lot_creation = fields.Boolean(string='Automatic Sales Lot Creation', implied_group='mc_sales_lot.group_automatic_sales_lot',
                                            help='If set, sales lots are automatically created. Else, user has to do it manually')

    @api.constrains('group_automatic_lot_creation', 'group_stock_production_lot')
    def _check_group_automatic_lot_creation(self):
        """ Prevent user to check Automatic Sales Lot Creation if system does not handle lots and serial numbers """
        for settings in self:
            if settings.group_automatic_lot_creation and not settings.group_stock_production_lot:
                raise UserError(_('Configuration conflict: Automatic Sales Lot Creation cannot be checked while Lots and Serial Numbers is not'))

    @api.onchange('group_stock_production_lot')
    def _onchange_group_stock_production_lot(self):
        """ Overridden method
            If user unchecks Lots and Serial Numbers parameter then uncheck Automatic Sales Lot Creation too """
        super(ResConfigSettings, self)._onchange_group_stock_production_lot()
        if not self.group_stock_production_lot:
            self.group_automatic_lot_creation = False
