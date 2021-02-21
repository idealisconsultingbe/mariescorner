# -*- coding: utf-8 -*-
"""
Configure the short description for every product belonging to a specific category.
"""

import argparse
import logging

labels = {
    1: {
        'en': 'Primary fabric:',
        'fr_BE': 'Tissu primaire:',
    },
    2: {
        'en': 'Secondary fabric:',
        'fr_BE': 'Tissu secondaire:',
    },
    'color': {
        'en': '/ Color:',
        'fr_BE': '/ Couleur:',
    },
    3: {
        'en': '',
        'fr_BE': '',
    },
    4: {
        'en': 'Mc Care:',
        'fr_BE': 'Mc Care:',
    },
    5: {
        'en': ' Leather covering:',
        'fr_BE': ' Leather covering:',
    },
    6: {
        'en': 'Fireproof treatment:',
        'fr_BE': 'Fireproof treatment:',
    },
    7: {
        'en': 'Contrast Piping:',
        'fr_BE': 'Contrast Piping:',
    },
    8: {
        'en': 'Contrast fabrics:',
        'fr_BE': 'Contrast fabrics:',
    },
    9: {
        'en': 'Contrast pillow:',
        'fr_BE': 'Contrast pillow:',
    },
    10: {
        'en': 'Cushion configuration:',
        'fr_BE': 'Cushion configuration:',
    },
    11: {
        'en': 'Color of the nails:',
        'fr_BE': 'Color of the nails:',
    },
    12: {
        'en': 'Base in RAL Finish:',
        'fr_BE': 'Base in RAL Finish:',
    },
    13: {
        'en': 'Lacquered finish base:',
        'fr_BE': 'Lacquered finish base:',
    },
    14: {
        'en': 'Customer wood color:',
        'fr_BE': 'Customer wood color:',
    },
    15: {
        'en': 'Feet upholstered:',
        'fr_BE': 'Feet upholstered:',
    },
    16: {
        'en': ' Feet and basement upholstered:',
        'fr_BE': 'Feet and basement upholstered:',
    },
    17: {
        'en': 'One size modification:',
        'fr_BE': 'One size modification:',
    },
    18: {
        'en': 'Fabrics with a repeat pattern:',
        'fr_BE': 'Fabrics with a repeat pattern:',
    },
    19: {
        'en': 'Fabrics width < 140 cm:',
        'fr_BE': 'Fabrics width < 140 cm:',
    },
    20: {
        'en': 'COM fabrics with a repeat pattern:',
        'fr_BE': 'COM fabrics with a repeat pattern:',
    },
    21: {
        'en': 'Artificial & Real leathers:',
        'fr_BE': 'Artificial & Real leathers:',
    },
    22: {
        'en': 'Stain Treatment:',
        'fr_BE': 'Stain Treatment:',
    },
}

attribute_ids = {4: 71, 5: 72, 6: 75, 7: 76, 8: 77, 9: 78, 10: 79, 11: 80,
                 12: 81, 13: 82, 14: 83, 15: 84, 16: 85, 17: 86, 18: 87, 19: 88, 20: 89, 21: 90, 22: 91,}

def prepare_description_values(description_line, fabric_sequence, attribute_id=False, attribute_color_id=False):
    need_color = True
    if fabric_sequence not in [1, 2, 3]:
        need_color = False
    color = labels['color']
    label = labels[fabric_sequence]
    values = [
        {
            'type': 'attribute' if attribute_id else 'text',
            'attribute_id': attribute_id if attribute_id else False,
            'text': label['en'],
            'description_line_id': description_line.id,
        }
    ]
    if need_color:
        values.append({
            'type': 'attribute' if attribute_color_id else 'text',
            'attribute_id': attribute_color_id if attribute_color_id else False,
            'text': color['en'],
            'description_line_id': description_line.id,
        })
    return values

def translate_values(values, lang):
    for value in values:
        for label_key in labels:
            if value.text == labels[label_key]['en']:
                value.with_context(lang=lang).write({'text': labels[label_key][lang]})

parser = argparse.ArgumentParser(description="")
parser.add_argument('database')
parser.add_argument('product_category')
parser.add_argument('primary_fabric_id')
parser.add_argument('primary_fabric_color_id')
parser.add_argument('secondary_fabric_id')
parser.add_argument('secondary_fabric_color_id')
parser.add_argument('foot_id')
parser.add_argument('foot_color_id')
args = parser.parse_args()

session.open(db=args.database)

logging.info('Load product category.')
product_category = session.env['product.category'].search([('id', 'child_of', int(args.product_category))])
logging.info('Product category loaded %s.' % product_category.mapped('name'))

logging.info('Load product templates.')
products = session.env['product.template'].search([('categ_id', 'in', product_category.ids)])
logging.info(' %s Product templates loaded.' % len(products.ids))

logging.info('Delete existing description lines.')
description_lines = session.env['product.configurator.description.line'].search([])
description_lines.unlink()

logging.info('Start Creating Short Description Lines.')
product_not_updated_description_ids = []
for product in products:
    if not product.description_line_ids:
        lines = session.env['product.configurator.description.line']
        for i in range(1, 23):
            lines |= session.env['product.configurator.description.line'].create({'product_tmpl_id': product.id, 'sequence': i})
        for line in lines:
            if line.sequence == 1:
                values = session.env['product.configurator.description.line.value'].create(prepare_description_values(line, line.sequence, int(args.primary_fabric_id), int(args.primary_fabric_color_id)))
                translate_values(values, 'fr_BE')
            elif line.sequence == 2:
                values = session.env['product.configurator.description.line.value'].create(prepare_description_values(line, line.sequence, int(args.secondary_fabric_id), int(args.secondary_fabric_color_id)))
                translate_values(values, 'fr_BE')
            elif line.sequence == 3:
                values = session.env['product.configurator.description.line.value'].create(prepare_description_values(line, line.sequence, int(args.foot_id), int(args.foot_color_id)))
                translate_values(values, 'fr_BE')
            else:
                values = session.env['product.configurator.description.line.value'].create(prepare_description_values(line, line.sequence, attribute_ids[line.sequence]))
                translate_values(values, 'fr_BE')
    else:
        product_not_updated_description_ids.append(product.id)

logging.info('No description created for %s.' % product_not_updated_description_ids)
session.cr.commit()
session.close()
logging.info('Done')

