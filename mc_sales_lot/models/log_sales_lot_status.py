# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class LogSalesLotStatus(models.Model):
    _name = 'log.sales.lot.status'
    _description = 'Model used for logging the status of the sales lot, allow to follow its progression.'
    _order = 'date asc'

    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user.id)
    date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now())
    name = fields.Text(string='Name', required=True)
    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Sales Lot', required=True)
    model_id = fields.Many2one('ir.model', string="Model")
    res_id = fields.Integer(string='Record ID')
