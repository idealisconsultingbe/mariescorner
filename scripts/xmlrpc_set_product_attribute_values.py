# -*- coding: utf-8 -*-
"""
Configure attributes-values for every product belonging to a specific category.
"""

import argparse
import xmlrpc.client


product_attributes_domain = {
    '[Seats] Primary Fabric Type': {'normal': [('name', 'not in', ['To Be Defined'])], 'tcl': [('name', 'in', ['None', 'TCL', 'TISSU À DEFINIR GRADE A', 'TISSU À DEFINIR GRADE B', 'TISSU À DEFINIR GRADE C', 'TISSU À DEFINIR GRADE D', 'TISSU À DEFINIR GRADE E', 'TISSU À DEFINIR GRADE F'])]},
    '[Seats] Color of primary fabric': {'normal': [('name', 'not in', ['To Be Defined'])], 'tcl': [('name', '=', 'None')]},
    '[Seats] Secondary Fabric Type': {'normal': [('name', 'not in', ['To Be Defined'])], 'tcl': [('name', 'in', ['None', 'TCL', 'TISSU À DEFINIR GRADE A', 'TISSU À DEFINIR GRADE B', 'TISSU À DEFINIR GRADE C', 'TISSU À DEFINIR GRADE D', 'TISSU À DEFINIR GRADE E', 'TISSU À DEFINIR GRADE F'])]},
    '[Seats] Color of secondary fabric': {'normal': [('name', 'not in', ['To Be Defined'])], 'tcl': [('name', '=', 'None')]},
    '[Seats] Foot Type': {'standard': [('name', '=', 'STANDARD')],
                          'archer': [('name', '=', 'ARCHER')],
                          'burton': [('name', '=', 'BURTON')],
                          'daly': [('name', '=', 'DALY')],
                          'hunter': [('name', '=', 'HUNTER')],
                          'mitchell': [('name', '=', 'MITCHELL')],
                          'murray': [('name', '=', 'MURRAY')],
                          'victoria': [('name', '=', 'VICTORIA')]},
    '[Seats] Color of the foots': {'beech': ['|', '|', ('name', '=like', 'BEECH%'), ('name', '=', 'None'), ('name', '=', 'To Be Defined')],
                                    'metal': ['|', '|', ('name', '=like', 'METAL%'), ('name', '=', 'None'), ('name', '=', 'To Be Defined')],
                                    'oak': ['|', '|', ('name', '=like', 'OAK%'), ('name', '=', 'None'), ('name', '=', 'To Be Defined')],
                                    'walnut': ['|', '|', ('name', '=like', 'WALNUT%'), ('name', '=', 'None'), ('name', '=', 'To Be Defined')],
                                    'beech_9': ['|', '|', ('name', '=', 'BEECH EBONY (9)'), ('name', '=', 'None'), ('name', '=', 'To Be Defined')],
                                    'walnut_specific': ['|', '|', ('name', 'in', ['WALNUT (5)', 'WALNUT WAXED (6)', 'WALNUT EBONY (9)', 'WALNUT SMOKE (14)']), ('name', '=', 'None'), ('name', '=', 'To Be Defined')],},
    '[Seats] Mc Care': {'normal': []},
    '[Seats] Leather covering': {'normal': []},
    '[Seats] Fireproof treatment': {'normal': []},
    '[Seats] Contrast Piping': {'normal': []},
    '[Seats] Contrast fabrics': {'normal': []},
    '[Seats] Contrast pillow': {'normal': []},
    '[Seats] Cushion configuration': {'normal': []},
    '[Seats] Color of the nails': {'normal': [('name', '=', 'None')], 'nails': []},
    '[Seats] Base in RAL Finish': {'normal': []},
    '[Seats] Lacquered finish base': {'normal': []},
    '[Seats] Customer wood color': {'normal': []},
    '[Seats] Feet upholstered': {'normal': []},
    '[Seats] Feet and basement upholstered': {'normal': []},
    '[Seats] One size modification': {'normal': []},
    '[Seats] Fabrics with a repeat pattern': {'normal': []},
    '[Seats] Fabrics width < 140 cm': {'normal': []},
    '[Seats] Customer Own Material (COM) fabrics with a repeat pattern': {'normal': []},
    '[Seats] Artificial & Real leathers': {'normal': []},
    '[Seats] Stain Treatment': {'normal': []},
}

def get_product_type(product):
    fabric_type = 'normal'
    foot_type = 'standard'
    foot_color_type = 'beech'
    nails_type = 'normal'
    if 'c.o.m.' in product['name'].lower() or 'com' in product['name'].lower() or (product['default_code'] and 'tcl' in product['default_code'].lower()):
        fabric_type = 'tcl'
    if 'pieds archer' in product['name'].lower():
        foot_type = 'archer'
    elif 'pieds burton' in product['name'].lower():
        foot_type = 'burton'
    elif 'pieds daly' in product['name'].lower():
        foot_type = 'daly'
    elif 'pieds hunter' in product['name'].lower():
        foot_type = 'hunter'
    elif 'pieds mitchell' in product['name'].lower():
        foot_type = 'mitchell'
    elif 'pieds murray' in product['name'].lower():
        foot_type = 'murray'
    elif 'pieds victoria' in product['name'].lower():
        foot_type = 'victoria'
    if 'alvin' in product['name'].lower():
        foot_color_type = 'beech_9'
    elif 'pouf carmel' in product['name'].lower():
        foot_color_type = 'oak'
    elif 'collin' in product['name'].lower() and 'metal' in product['name'].lower():
        foot_color_type = 'metal'
    elif 'collin' in product['name'].lower():
        foot_color_type = 'beech_9'
    elif 'hamlet' in product['name'].lower() or 'fillmore' in product['name'].lower() or 'foley' in product['name'].lower() or 'rockland' in product['name'].lower() or 'garland' in product['name'].lower():
        foot_color_type = 'oak'
    elif 'ashton' in product['name'].lower() and 'walnut' in product['name'].lower():
        foot_color_type = 'walnut_specific'
    elif 'baldwin' in product['name'].lower() or 'sonoma lounge' in product['name'].lower():
        foot_color_type = 'walnut'
    elif 'brentwood' in product['name'].lower() or 'carmel' in product['name'].lower() or 'pierson' in product['name'].lower():
        foot_color_type = 'oak'
    elif 'virginia' in product['name'].lower():
        foot_color_type = 'metal'
    if 'pierson' in product['name'].lower():
        nails_type = 'nails'
    return fabric_type, foot_type, foot_color_type, nails_type


def get_attribute_values_domain(attribute, fabric_type, foot_type, foot_color_type, nails_type):
    domain = []
    if attribute['name'] in ('[Seats] Primary Fabric Type', '[Seats] Color of primary fabric', '[Seats] Secondary Fabric Type', '[Seats] Color of secondary fabric'):
        domain_candidates = product_attributes_domain[attribute['name']]
        if fabric_type in domain_candidates:
            domain = domain_candidates[fabric_type].copy()
    elif attribute['name'] == '[Seats] Foot Type':
        domain_candidates = product_attributes_domain[attribute['name']]
        if foot_type in domain_candidates:
            domain = domain_candidates[foot_type].copy()
    elif attribute['name'] == '[Seats] Color of the foots':
        domain_candidates = product_attributes_domain[attribute['name']]
        if foot_color_type in domain_candidates:
            domain = domain_candidates[foot_color_type].copy()
    elif attribute['name'] == '[Seats] Color of the nails':
        domain_candidates = product_attributes_domain[attribute['name']]
        if nails_type in domain_candidates:
            domain = domain_candidates[nails_type].copy()
    else:
        if attribute['name'] in product_attributes_domain:
            domain_candidates = product_attributes_domain[attribute['name']]
            domain = domain_candidates['normal'].copy()
        else:
            print('%s attribute not found' % attribute['name'])
    return domain


def get_dict_records(records_list):
    records = {}
    for record_list in records_list:
        records[record_list['id']] = record_list
    return records


parser = argparse.ArgumentParser(description="")
parser.add_argument('url')
parser.add_argument('database')
parser.add_argument('user')
parser.add_argument('password')
parser.add_argument('product_category_id')
parser.add_argument('product_attribute_ids')
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

product_attribute_ids = [int(id) for id in args.product_attribute_ids.split(',')]
print('Load product attributes.')
attributes_info = models.execute_kw(db, uid, password, 'product.attribute', 'search_read', [[('id', 'in', product_attribute_ids)]], {'fields': ['name']})
print('%s Product attributes loaded.' % len(attributes_info))

attribute_values_to_create = []
print('Start configuring attribute values.')
i = 0
for product in products_tmpl_info:
    i += 1
    # if product.default_code == 'VIRGINIA 200':
    #     print('test')
    for attribute in attributes_info:
        product_template_attributes_candidate_info = models.execute_kw(db, uid, password, 'product.template.attribute.line', 'search_read', [[('id', 'in', product['attribute_line_ids']), ('attribute_id', '=', attribute['id'])]], {'fields': ['value_ids']})
        ptac_records = get_dict_records(product_template_attributes_candidate_info)
        product_template_attributes_candidate_ids = [ptac['id'] for ptac in product_template_attributes_candidate_info]
        if len(product_template_attributes_candidate_ids) > 1:
            product_template_attributes_to_delete_ids = product_template_attributes_candidate_ids[0:len(product_template_attributes_candidate_ids) - 1]
            product_template_attributes_candidate_ids = product_template_attributes_candidate_ids[-1]
            models.execute_kw(db, uid, password, 'product.template.attribute.line', 'unlink', [product_template_attributes_to_delete_ids])
        product_template_attributes_candidate_id = product_template_attributes_candidate_ids[0]
        fabric_type, foot_type, foot_color_type, nails_type = get_product_type(product)
        domain = get_attribute_values_domain(attribute, fabric_type, foot_type, foot_color_type, nails_type)
        domain.append(('attribute_id', '=', attribute['id']))
        pav_ids = models.execute_kw(db, uid, password, 'product.attribute.value', 'search', [domain])
        if pav_ids:
            if product_template_attributes_candidate_id:
                value_ids = ptac_records[product_template_attributes_candidate_id]['value_ids']
                value_to_add = [pav_id for pav_id in pav_ids if pav_id not in value_ids]
                if value_to_add:
                    models.execute_kw(db, uid, password, 'product.template.attribute.line', 'write', [product_template_attributes_candidate_id,
                                                                                                      {'value_ids': [(4, v_id) for v_id in value_to_add]}])
                value_to_delete = [pav_id for pav_id in value_ids if pav_id not in pav_ids]
                if value_to_delete:
                    models.execute_kw(db, uid, password, 'product.template.attribute.line', 'write', [product_template_attributes_candidate_id,
                                                                                                      {'value_ids': [(3, v_id) for v_id in value_to_delete]}])
            else:
                attribute_values_to_create.append({'product_tmpl_id': product['id'], 'attribute_id': attribute['id'], 'value_ids': [(6, 0, pav_ids)]})
    if i % 100 == 0:
        print('%s product templates configured' % i)
print('%s product templates configured' % i)

print('%s missing product template attribute lines to create.' % len(attribute_values_to_create))
batch_of_values = []
i = 0
for attribute_value in attribute_values_to_create:
    batch_of_values.append(attribute_value)
    i+=1
    if i % 1000 == 0:
        models.execute_kw(db, uid, password, 'product.template.attribute.line', 'create', [batch_of_values])
        batch_of_values = []
        print('%s product template attribute lines created' % i)
models.execute_kw(db, uid, password, 'product.template.attribute.line', 'create', [batch_of_values])
print('%s product template attribute lines created' % i)

print('Done')

