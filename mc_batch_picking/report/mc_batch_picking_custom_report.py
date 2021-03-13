# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _


class BatchPickingReceiptReport(models.Model):
    _name = 'report.mc_batch_picking.receipt_batch_packing_lst_report'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_batch_picking.receipt_batch_packing_lst_report')
        batch_pickings = self.env[report.model].browse(docids)
        batch_pickings_by_carrier = {}
        for batch in batch_pickings:
            pickings_by_carrier = batch.picking_ids.get_picking_by_carrier()
            batch_pickings_by_carrier[batch.id] = pickings_by_carrier
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': batch_pickings,
            'data': data,
            'batch_pickings_by_carrier': batch_pickings_by_carrier,
        }

class PickingReceiptReport(models.Model):
    _name = 'report.mc_batch_picking.receipt_batch_packing_lst_document'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_batch_picking.receipt_batch_packing_lst_document')
        pickings = self.env[report.model].browse(docids)
        pickings_by_carrier = pickings.get_picking_by_carrier()
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': pickings,
            'data': data,
            'pickings_by_carrier': pickings_by_carrier,
        }

class PlannedBatchPickingReport(models.Model):
    _name = 'report.mc_batch_picking.planned_batch_packing_lst_report'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_batch_picking.planned_batch_packing_lst_report')
        batch_pickings = self.env[report.model].browse(docids)
        batch_pickings_by_carrier = {}
        for batch in batch_pickings:
            pickings_by_carrier = batch.picking_ids.get_picking_by_carrier()
            batch_pickings_by_carrier[batch.id] = pickings_by_carrier
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': batch_pickings,
            'data': data,
            'batch_pickings_by_carrier': batch_pickings_by_carrier,
        }

class PlannedPickingShipmentReport(models.Model):
    _name = 'report.mc_batch_picking.planned_batch_packing_lst_document'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_batch_picking.planned_batch_packing_lst_document')
        pickings = self.env[report.model].browse(docids)
        pickings_by_carrier = pickings.get_picking_by_carrier()
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': pickings,
            'data': data,
            'pickings_by_carrier': pickings_by_carrier,
        }


class BatchPickingReport(models.Model):
    _name = 'report.mc_batch_picking.batch_packing_list_report_template'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_batch_picking.batch_packing_list_report_template')
        batch_pickings = self.env[report.model].browse(docids)
        batch_pickings_by_carrier = {}
        for batch in batch_pickings:
            pickings_by_carrier = batch.picking_ids.get_picking_by_carrier()
            batch_pickings_by_carrier[batch.id] = pickings_by_carrier
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': batch_pickings,
            'data': data,
            'batch_pickings_by_carrier': batch_pickings_by_carrier,
        }


class PickingShipmentReport(models.Model):
    _name = 'report.mc_batch_picking.batch_packing_list_document'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_batch_picking.batch_packing_list_document')
        pickings = self.env[report.model].browse(docids)
        pickings_by_carrier = pickings.get_picking_by_carrier()
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': pickings,
            'data': data,
            'pickings_by_carrier': pickings_by_carrier,
        }