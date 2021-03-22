# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
{
    'name': 'MsC Batch Picking',
    'version': '13.0.0.1',
    'category': 'Operations/Inventory',
    'description': """
    -   Keep a link between intercompany po lines and so lines through a new field.
    -   Keep a link between intercompany stock.production.lot.
    -   Keep a link between intercompany stock.move.line.
    -   By pass the reservation for transit location.
    -   When delivering from one company A to another company B, create stock move line for the reception in B with the values of the 
        delivery stock move line of the company A. This way if the tracking is activated we can pre-filled the lot.
    -   Add a button on the batch picking that allow to load every assigned picking.
    -   When validating a delivery batch picking (in company A) automatically create a batch picking for the reception (in company B) (multi company process).
    -   Add custom report for the batch picking.
    """,
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['stock_picking_batch', 'delivery', 'mc_sale', 'mc_sales_lot'],
    'data': [
        'views/stock_picking_batch_views.xml',
        'report/mc_batch_picking_report_templates.xml',
        'report/mc_batch_picking_reports.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}

