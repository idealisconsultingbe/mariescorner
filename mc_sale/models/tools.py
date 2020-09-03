# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

def to_float(string_value):
    try:
        string_value = string_value.replace(',', '.')
        return float(string_value)
    except ValueError:
        return 0.0
    except AttributeError:
        return 0.0

def is_float(string_value):
    try:
        float(string_value)
        return True
    except ValueError:
        return False
