#!/usr/bin/env bash

database=${1}

echo "Running Fabric automation for db:${database}"

echo "========= Adding product attribute values ============="
#../../../../bin/python_odoo ./set_product_attribute_values.py ${database} 170 65,66,67,68,69,70,71,72,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91

echo "========= Configuring Primary Fabric ============="
../../../../bin/python_odoo ./configure_attributes_combinaison.py ${database} 170 65 66 /home/fish/Documents/Idealis_work/Maries_Corner/Import/Odoo/mc_fabrics_attribute_combinaison.xlsx

echo "========= Configuring Secondary Fabric ============="
../../../../bin/python_odoo ./configure_attributes_combinaison.py ${database} 170 67 68 /home/fish/Documents/Idealis_work/Maries_Corner/Import/Odoo/mc_fabrics_attribute_combinaison.xlsx

echo "========= Configuring Fabric Variants ============="
../../../../bin/python_odoo ./configure_attributes_combinaison.py ${database} 108 92 93 /home/fish/Documents/Idealis_work/Maries_Corner/Import/Odoo/mc_fabrics_attribute_combinaison.xlsx

echo "========= Create Fabric Variants ============="
../../../../bin/python_odoo ./create_variants.py ${database} 14721 92 93 /home/fish/Documents/Idealis_work/Maries_Corner/Import/Odoo/mc_fabrics_attribute_combinaison.xlsx

echo "Actions Done !!!"
