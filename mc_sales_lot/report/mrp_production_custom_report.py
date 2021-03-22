# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _


class SalesLotReportLabels(models.Model):
    _name = 'report.mc_sales_lot.report_mrp_saleslot_label'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('mc_sales_lot.report_mrp_saleslot_label')
        productions = self.env[report.model].browse(docids)
        serial_numbers = {}
        for production in productions:
            serial_numbers[production.sales_lot_id.id] = []
            if production.sales_lot_id:
                for i in range(1, int(production.product_qty) + 1):
                    serial_numbers[production.sales_lot_id.id].append("{}{}".format(production.sales_lot_id.name, f"{i:02d}"))
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': productions,
            'data': data,
            'serial_numbers': serial_numbers,
        }
