# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductionSalesLot(models.Model):
    _name = 'stock.production.sales.lot'
    _description = 'Manufacturing Number'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'name desc'
    _sql_constraints = [
        ('product_name_unique', 'UNIQUE(product_id, name)', _('You are about to use a lot number that already exists (product and manufacturing number combination must be unique).')),
    ]

    name = fields.Char(string='Manufacturing Number', required=True)
    manufacturing_state = fields.Selection([('to_produce', 'To Produce'), ('in_manufacturing', 'In Manufacturing'), ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')], String='State', compute='_compute_manufacturing_state', tracking=True, store=True)
    external_state = fields.Selection([('to_produce', 'To Produce'), ('in_manufacturing', 'Demand received by the supplier'), ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')], String='External State', default='to_produce', help='Manufacturing state of subcontracted products')
    supplier_type = fields.Selection([('internal', 'Internal Company'), ('external', 'External Company')], string='Supplier Type', compute='_compute_supplier_type', store=True)
    manufacturing_date = fields.Date(string='Manufacturing Date')
    shipped_date = fields.Date(string='Shipped Date')
    ext_delivery_date = fields.Date(string='Subcontractor Delivery Date', help='Estimated delivery date provided by subcontractor')
    product_qty = fields.Float(string='Product Quantity', compute='_compute_product_qty', help='Quantity ordered by customer')

    # Relational fields
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_ids = fields.Many2many('res.partner', 'sales_lot_partner_rel', 'sales_lot_id', 'partner_id', string='Sellers', compute='_compute_supplier_type', store=True)
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('type', 'in', ['product', 'consu']), ('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True, ondelete='restrict', check_company=True)

    production_ids = fields.One2many('mrp.production', 'sales_lot_id', string='Manufacturing Orders')
    stock_move_ids = fields.One2many('stock.move', 'sales_lot_id', string='Stock Moves')
    stock_move_line_ids = fields.One2many('stock.move.line', 'sales_lot_id', string='Stock Move Lines')
    sale_order_line_ids = fields.One2many('sale.order.line', 'sales_lot_id', string='Sale Order Lines')
    sale_order_ids = fields.Many2many('sale.order', 'sales_lot_so_rel', 'sales_lot_id', 'so_id', string='Sale Orders', compute='_compute_sale_orders', store=True)
    purchase_order_line_ids = fields.One2many('purchase.order.line', 'sales_lot_id', string='Purchase Order Lines')
    purchase_order_ids = fields.Many2many('purchase.order', 'sales_lot_po_rel', 'sales_lot_id', 'po_id', string='Purchase Orders', compute='_compute_purchase_orders', store=True)
    lot_ids = fields.Many2many('stock.production.lot', 'sales_lot_stock_lot_rel', 'sales_lot_id', 'stock_lot_id', string='Lot/Serial', compute='_compute_get_lots', store=True)
    picking_ids = fields.Many2many('stock.picking', 'sales_lot_picking_rel', 'sales_lot_id', 'picking_id', string='Transfers', compute='_compute_pickings', store=True)

    log_sales_lot_status_ids = fields.One2many('log.sales.lot.status', 'sales_lot_id', string='Status')

    @api.depends('production_ids.state', 'supplier_type', 'external_state')
    def _compute_manufacturing_state(self):
        """
        Compute manufacturing state of each manufacturing number
        if supplier type is internal:
            Manuf State = To Produce: No Manufacturing Orders have been created for this Manufacturing Number.
            Manuf State = In Manufacturing: At least one MO exists.
            Manuf State = Confirmed: All Manufacturing Orders are Confirmed or Done.
            Manuf State = Done: All Manufacturing Orders are Done.
            Manuf State = Cancel: At least one MO is cancelled.
        else:
            Manuf state = external state set by external company
        """
        # Manually track "state" since tracking doesn't work with computed fields.
        # Retrieve initial values
        tracking = not self._context.get("mail_notrack") and not self._context.get("tracking_disable")
        initial_values = {}
        if tracking:
            initial_values = dict(
                (sale_lot.id, {"manufacturing_state": sale_lot.manufacturing_state})
                for sale_lot in self
            )
        for sale_lot in self:
            if sale_lot.supplier_type == 'external':
                state = sale_lot.external_state
            else:
                if not sale_lot.production_ids:
                    state = 'to_produce'
                else:
                    state = 'in_manufacturing'
                    if all([x == 'done' for x in sale_lot.production_ids.mapped('state')]):
                        state = 'done'
                    elif all([x not in ['cancel', 'draft'] for x in sale_lot.production_ids.mapped('state')]):
                        state = 'confirmed'
                    elif any([x == 'cancel' for x in sale_lot.production_ids.mapped('state')]):
                        state = 'cancel'
            sale_lot.manufacturing_state = state
        # track changing state
        if initial_values:
            self.message_track(self.fields_get(["manufacturing_state"]), initial_values)

    @api.depends('purchase_order_ids.partner_id', 'purchase_order_ids.partner_id.child_ids', 'purchase_order_ids.partner_id.parent_id', 'purchase_order_ids.partner_id.parent_id.child_ids')
    def _compute_supplier_type(self):
        """
        Compute supplier type and partners (sellers) of each manufacturing number.
        """
        for sale_lot in self:
            seller_ids = sale_lot.purchase_order_ids.mapped('partner_id')
            sale_lot.partner_ids = seller_ids or self.env['res.partner']
            for seller in seller_ids:
                if seller.parent_id:
                    seller = seller.parent_id
                sale_lot.partner_ids |= self.env['res.partner'].search([('id', 'child_of', seller.id)])
            company_partners = self.env['res.company'].search([]).mapped('partner_id')
            if sale_lot.partner_ids.mapped('commercial_partner_id') in company_partners:
                sale_lot.supplier_type = 'internal'
            else:
                sale_lot.supplier_type = 'external'

    @api.depends('sale_order_line_ids.order_id')
    def _compute_sale_orders(self):
        """ Compute sale orders linked to each manufacturing number """
        for sale_lot in self:
            sale_lot.sale_order_ids = sale_lot.sale_order_line_ids.mapped('order_id')

    @api.depends('purchase_order_line_ids.order_id')
    def _compute_purchase_orders(self):
        """ Compute purchase orders linked to each manufacturing number """
        for sale_lot in self:
            sale_lot.purchase_order_ids = False
            if sale_lot.purchase_order_line_ids:
                sale_lot.purchase_order_ids = sale_lot.purchase_order_line_ids.mapped('order_id')

    @api.depends('stock_move_line_ids.lot_id')
    def _compute_get_lots(self):
        """ Compute S/N linked to each manufacturing """
        for sale_lot in self:
            sale_lot.lot_ids = sale_lot.stock_move_line_ids.mapped('lot_id')

    @api.depends('stock_move_ids.picking_id')
    def _compute_pickings(self):
        """ Compute pickings linked to each manufacturing number """
        for sale_lot in self:
            sale_lot.picking_ids = sale_lot.stock_move_ids.mapped('picking_id')

    @api.depends('sale_order_line_ids.product_uom_qty')
    def _compute_product_qty(self):
        """ Compute sum of all ordered quantities for each manufacturing number """
        for sale_lot in self:
            sale_lot.product_qty = sum(sale_lot.sale_order_line_ids.mapped('product_uom_qty'))

    def create_log(self, name, msg, user=None, model=None, record=None, datetime=None):
        """
        Create an entry log in order to track manufacturing number actions. In case of empty message,
        an error is thrown.
        :param name: name of the log (in different languages)
        :param msg: message recorded (in different languages)
        :param user: user who made the action
        :param model: ir.model where occurred the action
        :param record: the source record id of the action
        :param datetime: the date and time when occurred the action
        :return: an entry log
        """
        self.ensure_one()
        if msg:
            vals = {
                'name': name['no_lang'],
                'description': msg['no_lang'],
                'sales_lot_id': self.id,
                'user_id': user.id or self.env.user.id,
                'model_id': model.id or False,
                'res_id': record or False,
                'date': datetime or fields.Datetime.now(),
            }
            log = self.env['log.sales.lot.status'].create(vals)
            log.with_context(lang='fr_BE').update({'name': name['fr_BE'], 'description': msg['fr_BE']})
            log.with_context(lang='en_US').update({'name': name['en_US'], 'description': msg['en_US']})
            return log
        else:
            msg = _('You cannot create an empty log')
            if model and record:
                msg = '{} {}'.format(msg, _('(model={}, record={})').format(model.model, record))
            raise ValidationError(msg)

