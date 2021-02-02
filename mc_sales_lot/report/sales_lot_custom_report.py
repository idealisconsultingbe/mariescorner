# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _


class SalesLotReport(models.Model):
    _name = 'report.mc_sales_lot.report_saleslot'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_sales_lot.report_saleslot')
        sales_lot = self.env[report.model].browse(docids)
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': sales_lot,
            'data': data,
            'fabrics_lots': False,
        }


class SalesLotReportLabels(models.Model):
    _name = 'report.mc_sales_lot.report_saleslot_labels'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_sales_lot.report_saleslot_labels')
        sales_lot = self.env[report.model].browse(docids)
        serial_numbers = {}
        for sale_lot in sales_lot:
            serial_numbers[sale_lot.id] = []
            for i in range(1, int(sale_lot.product_qty) + 1):
                serial_numbers[sale_lot.id].append("{}{}".format(sale_lot.name, f"{i:02d}"))
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': sales_lot,
            'data': data,
            'serial_numbers': serial_numbers,
        }
