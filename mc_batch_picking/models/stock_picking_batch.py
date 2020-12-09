# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    # delivery batch picking
    inter_company_batch_picking_id = fields.Many2one('stock.picking.batch', string='InterCompany Batch Picking', readonly=True)
    # receipt batch pickings
    inter_company_batch_picking_ids = fields.One2many('stock.picking.batch', 'inter_company_batch_picking_id', string='InterCompany Batch Pickings', readonly=True)

    # used to filter pickings
    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Method', check_company=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', string='Partner', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type', check_company=True, domain=[('code', 'in', ('incoming', 'outgoing'))], states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    move_ids = fields.Many2many('stock.move', 'batch_picking_stock_move_rel', 'batch_id', 'move_id', string='Stock Moves', compute='_compute_moves', readonly=False)
    move_line_ids = fields.Many2many('stock.move.line', 'batch_picking_stock_move_line_rel', 'batch_id', 'move_line_id', string='Operations', compute='_compute_moves', readonly=False)

    # compatibility fields used by pickings, moves and move lines in UI
    show_lots_text = fields.Boolean(compute='_compute_show_lots_text', help='Used in UI')
    immediate_transfer = fields.Boolean(default=False, help='Used in UI')
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_type_id.code', help='Used in UI')

    @api.depends('picking_ids')
    def _compute_moves(self):
        """ Compute moves and move lines used in batch """
        for batch in self:
            batch.update({
                    'move_ids': [(6, 0, batch.picking_ids.mapped('move_lines').ids)],
                    'move_line_ids': [(6, 0, batch.picking_ids.mapped('move_line_ids').ids)],
                })

    @api.depends('move_line_ids', 'picking_type_id.use_create_lots', 'picking_type_id.use_existing_lots', 'state')
    def _compute_show_lots_text(self):
        """ Compute visibility of lot_id and lot_name in move_line_ids tree view on batch form """
        group_production_lot_enabled = self.user_has_groups('stock.group_production_lot')
        for batch in self:
            if not batch.move_line_ids:
                batch.show_lots_text = False
            elif group_production_lot_enabled and batch.picking_type_id.use_create_lots \
                    and not batch.picking_type_id.use_existing_lots and batch.state != 'done':
                batch.show_lots_text = True
            else:
                batch.show_lots_text = False

    def button_load_picking(self):
        """ Load all pickings with the same picking type/operation type, delivery method (optional), and partner (optional) """
        self.ensure_one()
        if self.picking_type_id:
            pickings = self.env['stock.picking'].search([('state', 'in', ('waiting', 'confirmed')), ('picking_type_id', '=', self.picking_type_id.id)])
            pickings.action_assign()
            domain = [('company_id', '=', self.company_id.id), ('state', '=', 'assigned'), ('picking_type_id', '=', self.picking_type_id.id)]
            if self.delivery_carrier_id:
                domain.extend([('carrier_id', '=', self.delivery_carrier_id.id)])
            if self.partner_id:
                domain.extend([('partner_id', '=', self.partner_id.id)])
            pickings = self.env['stock.picking'].search(domain)
            self.update({
                'picking_ids': [(6, 0, pickings.ids)],
            })
        else:
            raise UserError(_('An operation type is required before loading available pickings'))

    def done(self):
        """
        Overridden method
        When validating a batch:
         - filter out all pickings with no quantities done
         - apply standard behaviour
         - create an inter company batch for all inter company pickings
         """
        self._check_company()
        self = self.sudo()
        pickings_without_qty_done = self.mapped('picking_ids').filtered(lambda picking: all([ml.qty_done == 0.0 for ml in picking.move_line_ids]))
        pickings_without_qty_done.update({'batch_id': False})
        if not self.picking_ids:
            raise UserError(_('Nothing to check the availability for. Please update at least one quantity done.'))
        res = super(StockPickingBatch, self).done()


        if self.picking_type_code == 'outgoing' and not self.inter_company_batch_picking_id :
            company_partners = self.env['res.company'].search([]).mapped('partner_id')
            company_partners |= self.env['res.partner'].search([('parent_id', 'in', company_partners.ids)])
            company_pickings = self.mapped('picking_ids').filtered(lambda pick: pick.partner_id in company_partners)

            company_picking_dict = {partner: [pick for pick in company_pickings if pick.partner_id == partner] for partner in company_pickings.mapped('partner_id')}
            for partner, picks in company_picking_dict.items():
                pickings = self.env['stock.picking']
                partner = partner.parent_id if partner.parent_id else partner
                for pick in picks:
                    if pick.sale_id:
                        purchase_line_ids = pick.sale_id.mapped('order_line.inter_company_po_line_id')
                        if purchase_line_ids:
                            pickings |= purchase_line_ids.mapped('move_ids').filtered(lambda m: m.state in ['waiting', 'confirmed', 'draft', 'partially_available', 'assigned']).mapped('picking_id')
                if pickings:
                    inter_company_batch = self.env['stock.picking.batch'].create({
                        'company_id': self.env['res.company'].search([('partner_id', '=', partner.id)]).id or False,
                        'picking_ids': [(6, 0, pickings.ids)],
                        'partner_id': self.company_id.partner_id.id,
                        'picking_type_id': self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1).id or False,
                        'inter_company_batch_picking_id': self.id
                    })
                    inter_company_batch.confirm_picking()
        return res
