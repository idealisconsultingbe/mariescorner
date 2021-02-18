# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_invoices_synchronization = fields.Boolean(string='Invoices/Bills Synchronization', implied_group='mc_account.group_invoices_synchronization', help='If set, invoices are synchronized between companies.')
    invoices_sync_origin_type = fields.Selection([('out_invoice', 'Customer Invoices'), ('in_invoice', 'Vendor Bills')], string='Invoices Synchronization Origin Type', default='out_invoice', config_parameter='mc_account.invoices_sync_origin_type', help='Determines inter-company invoices synchronization direction')
    invoices_sync_origin_company_id = fields.Many2one('res.company', string='Invoices Synchronization Origin', config_parameter='mc_account.invoices_sync_origin')
    invoices_sync_destination_company_id = fields.Many2one('res.company', string='Invoices Synchronization Destination', config_parameter='mc_account.invoices_sync_destination')
    invoices_sync_destination_type = fields.Selection([('out_invoice', 'Customer Invoices'), ('in_invoice', 'Vendor Bills')], string='Invoices Synchronization Destination Type', compute='_compute_invoices_sync_destination_type', help='Determines inter-company invoices synchronization direction')
    intercompany_invoice_synchronization_message = fields.Char(string='Invoices Synchronization Message')

    @api.depends('invoices_sync_origin_type')
    def _compute_invoices_sync_destination_type(self):
        """
        Compute type of invoices to be synchronized in multi-company transactions. Invoices are synchronized in only one direction.
        User has to choose synchronization origin. Synchronization destination is computed in order to prevent user from
        modifying it. Vendor bills are synchronized with customer invoices and customer invoices are synchronized with vendor bills
        """
        for config in self:
            config.invoices_sync_destination_type = 'out_invoice' if config.invoices_sync_origin_type == 'in_invoice' else 'in_invoice'

    @api.onchange('group_invoices_synchronization', 'invoices_sync_origin_type')
    def _onchange_intercompany_invoice_synchronization_message(self):
        """ Compute informative tooltip about synchronization direction """
        if self.group_invoices_synchronization and self.invoices_sync_origin_type == 'out_invoice':
            self.intercompany_invoice_synchronization_message = _('In case of inter-company transaction, purchase order invoices will be synchronized with sales order invoices : confirmation of a customer invoice will generate a synchronized vendor bill if all quantities have not been invoiced yet.')
        if self.group_invoices_synchronization and self.invoices_sync_origin_type == 'in_invoice':
            self.intercompany_invoice_synchronization_message = _('In case of inter-company transaction, sales order invoices will be synchronized with purchase order invoices : confirmation of a vendor bill will generate a synchronized customer invoice if all quantities have not been invoiced yet.')

    @api.onchange('rule_type')
    def _onchange_group_invoices_synchronization(self):
        """ Uncheck group_invoices_synchronization if rule type is not sales and purchase orders synchronization """
        if self.rule_type != 'so_and_po':
            self.group_invoices_synchronization = False

    @api.constrains('invoices_sync_origin_company_id', 'invoices_sync_destination_company_id')
    def _check_invoices_synchronization(self):
        """ Check if synchronized companies are different """
        for config in self:
            if config.invoices_sync_destination_company_id == config.invoices_sync_origin_company_id:
                raise ValidationError(_('Invoices synchronization is only for inter-company transactions'))
