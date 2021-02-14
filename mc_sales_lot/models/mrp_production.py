# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mandatory_date = fields.Date(string='Mandatory Date', related='sales_lot_id.mandatory_date', help='Mandatory date coming from original sale order')
    inter_company_origin = fields.Text(string='Inter Company Source', compute='_compute_inter_company_origin', store=True)
    sales_lot_id = fields.Many2one('stock.production.sales.lot', compute='_compute_sales_lot_id', string='Manufacturing Number', store=True)
    log_assigned_done = fields.Boolean(string='Log Assigned', default=False, help='Boolean indicating that a msg for the assignation has already been logged on the production number.')

    @api.depends('move_dest_ids.sales_lot_id')
    def _compute_sales_lot_id(self):
        """
        Compute M2o relation to Stock Production Manufacturing Number from destination moves
        """
        for production in self:
            if len(production.move_dest_ids.mapped('sales_lot_id')) == 1 and all(
                    move.sales_lot_id for move in production.move_dest_ids):
                production.sales_lot_id = production.move_dest_ids[0].sales_lot_id
            else:
                production.sales_lot_id = False

    @api.depends('sales_lot_id.sale_order_ids')
    def _compute_inter_company_origin(self):
        """
        Display the inter company source.
        """
        for production in self:
            if production.sales_lot_id and production.sales_lot_id.sale_order_ids:
                so_inter_company = production.sales_lot_id.sale_order_ids.filtered(lambda so: so.company_id != production.company_id)
                production.inter_company_origin = ','.join(so_inter_company.mapped('name'))
            else:
                production.inter_company_origin = ''

    def action_confirm(self):
        """
        Overridden method
        If MO is confirmed, then an entry log is created
        """
        res = super(MrpProduction, self).action_confirm()
        for production in self.filtered(lambda p: p.sales_lot_id):
            if production.state == 'confirmed':
                name = {
                    'no_lang': _('{} Confirmed').format(production.name),
                    'en_US': '{} Confirmed'.format(production.name),
                    'fr_BE': '{} Confirmé'.format(production.name)
                }
                msg = {
                    'no_lang': _('All the necessary information have been received by {} for manufacturing order {}, the planned date is {}').format(production.company_id.name, production.name, production.date_planned_start),
                    'en_US': 'All the necessary information have been received by {} for manufacturing order {}, the planned date is {}'.format(production.company_id.name, production.name, production.date_planned_start),
                    'fr_BE': 'Toutes les informations nécessaires à {} pour l\'ordre de production {} ont été reçues, la date plannifiées est {}'.format(production.company_id.name, production.name, production.date_planned_start),
                }
                production._create_log(name, msg)
        return res

    def action_assign(self):
        """
        Overridden method
        If all materials are correctly reserved, then an entry log is created
        """
        res = super(MrpProduction, self).action_assign()
        for production in self.filtered(lambda p: p.sales_lot_id):
            if not production.log_assigned_done and all(state == 'assigned' for state in production.move_raw_ids.mapped('state')):
                production.log_assigned_done = True
                name = {
                    'no_lang': _('{} Ready').format(production.name),
                    'en_US': '{} Ready'.format(production.name),
                    'fr_BE': '{} Prêt'.format(production.name)
                }
                msg = {
                    'no_lang': _('All raw materials have been received by {} for manufacturing order {}').format(production.company_id.name, production.name),
                    'en_US': 'All raw materials have been received by {} for manufacturing order {}'.format(production.company_id.name, production.name),
                    'fr_BE': _('Tous les matériaux ont été réceptionnés par {} pour l\'ordre de production {}').format(production.company_id.name, production.name),
                }
                production._create_log(name, msg)
        return res

    def _create_log(self, name, msg):
        """
        Create an entry log in manufacturing number
        """
        self.ensure_one()
        model = self.env['ir.model'].search([('model', '=', self._name)])
        self.sales_lot_id.create_log(name, msg, user=self.env.user, model=model, record=self.id)
