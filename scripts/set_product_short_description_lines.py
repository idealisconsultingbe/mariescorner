# -*- coding: utf-8 -*-
"""

"""

import argparse
import logging

primary_fabric = {
    'en': 'Primary fabric:',
    'fr_BE': 'Tissu primaire:',
}

secondary_fabric = {
    'en': 'Secondary fabric:',
    'fr_BE': 'Tissu secondaire:',
}

color = {
    'en': '/ Color:',
    'fr_BE': '/ Couleur:',
}

foot = {
    'en': 'Foot types:',
    'fr_BE': 'Type de pieds:',
}

def prepare_description_values(description_line, fabric_sequence, attribute_id=False, attribute_color_id=False):
    if fabric_sequence == 1:
        label = primary_fabric
    elif fabric_sequence == 2:
        label = secondary_fabric
    else:
        label = foot
    return [
        {'type': 'text',
        'text': label['en'],
        'description_line_id': description_line.id,
         },
        {'type': 'attribute' if attribute_id else 'text',
        'attribute_id': attribute_id if attribute_id else False,
         'text': 'None' if not attribute_id else False,
        'description_line_id': description_line.id,
         },
        {'type': 'text',
         'text': color['en'],
         'description_line_id': description_line.id,
         },
        {'type': 'attribute' if attribute_color_id else 'text',
         'attribute_id': attribute_color_id if attribute_color_id else False,
         'text': 'None' if not attribute_color_id else False,
         'description_line_id': description_line.id,
         },
    ]

def translate_values(values, lang):
    for value in values:
        for label in [primary_fabric, secondary_fabric, color, foot]:
            if value.text == label['en']:
                value.with_context(lang=lang).write({'text': label[lang]})

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
logging.info('Product templates loaded %s.' % products.ids)

logging.info('Delete existing description lines.')
description_lines = session.env['product.configurator.description.line'].search([])
description_line_values = session.env['product.configurator.description.line.value'].search([])
description_lines.unlink()
description_line_values.unlink()

product_not_updated_description_ids = []
for product in products:
    attributes = product.attribute_line_ids.mapped('attribute_id')
    if not product.description_line_ids:
        first_line = session.env['product.configurator.description.line'].create({'product_tmpl_id': product.id, 'sequence': 1})
        second_line = session.env['product.configurator.description.line'].create({'product_tmpl_id': product.id, 'sequence': 2})
        third_line = session.env['product.configurator.description.line'].create({'product_tmpl_id': product.id, 'sequence': 3})
        if int(args.primary_fabric_id) in attributes.ids:
            values = session.env['product.configurator.description.line.value'].create(prepare_description_values(first_line, 1, int(args.primary_fabric_id), int(args.primary_fabric_color_id)))
            translate_values(values, 'fr_BE')
        else:
            session.env['product.configurator.description.line.value'].create(prepare_description_values(first_line, 1))
        if int(args.secondary_fabric_id) in attributes.ids:
            values = session.env['product.configurator.description.line.value'].create(prepare_description_values(second_line, 2, int(args.secondary_fabric_id), int(args.secondary_fabric_color_id)))
            translate_values(values, 'fr_BE')
        else:
            session.env['product.configurator.description.line.value'].create(prepare_description_values(second_line, 2))
        if int(args.foot_id) in attributes.ids:
            values = session.env['product.configurator.description.line.value'].create(prepare_description_values(third_line, 3, int(args.foot_id), int(args.foot_color_id)))
            translate_values(values, 'fr_BE')
        else:
            session.env['product.configurator.description.line.value'].create(prepare_description_values(third_line, 3))
    else:
        product_not_updated_description_ids.append(product.id)

logging.info('No description created for %s.' % product_not_updated_description_ids)
session.cr.commit()
session.close()
logging.info('Done')

