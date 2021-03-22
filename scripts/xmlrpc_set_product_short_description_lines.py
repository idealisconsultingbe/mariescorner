# -*- coding: utf-8 -*-
"""
Configure the short description for every product belonging to a specific category.
"""

import argparse
import xmlrpc.client

labels = {
    1: {
        'en': '',
        'fr_BE': '',
    },
    2: {
        'en': '',
        'fr_BE': '',
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

def prepare_description_values(description_line_values, attribute_id=False, attribute_color_id=False):
    need_color = True
    if description_line_values['sequence'] not in [1, 2]:
        need_color = False
    color = labels['color']
    label = labels[description_line_values['sequence']]
    values = [(0, 0,
               {
                   'type': 'attribute' if attribute_id else 'text',
                   'attribute_id': attribute_id if attribute_id else False,
                   'text': label['en'],
               })
              ]
    if need_color:
        values.append((0, 0, {
            'type': 'attribute' if attribute_color_id else 'text',
            'attribute_id': attribute_color_id if attribute_color_id else False,
            'text': color['en'],
        }))
    return values

def translate_values(values, lang):
    for value in values:
        for label_key in labels:
            if value.text == labels[label_key]['en']:
                value.with_context(lang=lang).write({'text': labels[label_key][lang]})

parser = argparse.ArgumentParser(description="")
parser.add_argument('url')
parser.add_argument('database')
parser.add_argument('user')
parser.add_argument('password')
parser.add_argument('product_category_id')
parser.add_argument('primary_fabric_id')
parser.add_argument('primary_fabric_color_id')
parser.add_argument('secondary_fabric_id')
parser.add_argument('secondary_fabric_color_id')
parser.add_argument('foot_color_id')
args = parser.parse_args()

db =args.database
password = args.password

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(args.url))
uid = common.authenticate(db, args.user, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(args.url))

print('Load product category.')
product_category_ids = models.execute_kw(db, uid, password, 'product.category', 'search', [[('id', 'child_of', int(args.product_category_id))]])
print('%s Product category loaded.' % len(product_category_ids))

print('Load product templates.')
products_tmpl_info = models.execute_kw(db, uid, password, 'product.template', 'search_read', [[('categ_id', 'in', product_category_ids)]], {'fields': ['name', 'default_code', 'attribute_line_ids']})
print('%s Product templates loaded.' % len(products_tmpl_info))

print('Delete existing description lines.')
description_line_ids = models.execute_kw(db, uid, password, 'product.configurator.description.line', 'search', [[]])
models.execute_kw(db, uid, password, 'product.configurator.description.line', 'unlink', [description_line_ids])

print('Start Creating Short Description Lines.')
product_not_updated_description_ids = []
for product in products_tmpl_info:
    lines_values = []
    for i in range(1, 23):
        lines_values.append({'product_tmpl_id': product['id'], 'sequence': i})
    for line_values in lines_values:
        if line_values['sequence'] == 1:
            line_values.update({'value_ids': prepare_description_values(line_values, int(args.primary_fabric_id), int(args.primary_fabric_color_id))})
            # translate_values(values, 'fr_BE')
        elif line_values['sequence'] == 2:
            line_values.update({'value_ids': prepare_description_values(line_values, int(args.secondary_fabric_id), int(args.secondary_fabric_color_id))})
            # translate_values(values, 'fr_BE')
        elif line_values['sequence'] == 3:
            line_values.update({'value_ids': prepare_description_values(line_values, int(args.foot_color_id))})
            # translate_values(values, 'fr_BE')
        else:
            line_values.update({'value_ids': prepare_description_values(line_values, attribute_ids[line_values['sequence']])})
            # translate_values(values, 'fr_BE')
    models.execute_kw(db, uid, password, 'product.configurator.description.line', 'create', [lines_values])


print('No description created for %s.' % product_not_updated_description_ids)
print('Done')

