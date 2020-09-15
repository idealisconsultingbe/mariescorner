# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', compute='_compute_sales_lot_id', string='Sales Lot',
                                   store=True)

    @api.depends('move_dest_ids.sales_lot_id')
    def _compute_sales_lot_id(self):
        """ Compute M2o relation to Stock Production Sales Lot from destination moves
        """
        for production in self:
            if len(production.move_dest_ids.mapped('sales_lot_id')) == 1 and all(
                    move.sales_lot_id for move in production.move_dest_ids):
                production.sales_lot_id = production.move_dest_ids[0].sales_lot_id
            else:
                production.sales_lot_id = False

    def action_confirm(self):
        """
        Overridden method
        If MO is confirmed, then an entry log is created
        """
        res = super(MrpProduction, self).action_confirm()
        for production in self.filtered(lambda p: p.sales_lot_id):
            if production.state == 'confirmed':
                msg = _('All the necessary information have been received by {} for manufacturing order {}').format(production.company_id.name, production.name)
                production._create_log(msg)
        return res

    def action_assign(self):
        """
        Overridden method
        If all materials are correctly reserved, then an entry log is created
        """
        res = super(MrpProduction, self).action_assign()
        for production in self.filtered(lambda p: p.sales_lot_id):
            if not production.env.context.get('skip_sales_lot_log') and not any(state == 'partially_available' for state in production.move_raw_ids.mapped('state')):
                msg = _('All raw materials have been received by {} for manufacturing order {}').format(production.company_id.name, production.name)
                production._create_log(msg)
        return res

    def button_mark_done(self):
        """
        Overridden method
        Add context info in order to prevent creation of an entry log when MO is ready for production
        """
        self = self.with_context(skip_sales_lot_log=True)
        return super(MrpProduction, self).button_mark_done()

    def _create_log(self, msg):
        """
        Create an entry log in sales lot
        """
        self.ensure_one()
        params = self.env.context.get('params', defaultdict(lambda: False))
        model = self.env['ir.model'].search([('model', '=', params['model'])])
        self.sales_lot_id.create_log(msg, user=self.env.user, model=model, record=params['id'])
