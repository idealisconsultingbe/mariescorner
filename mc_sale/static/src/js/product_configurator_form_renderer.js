odoo.define('mc_sale.ProductConfiguratorFormRenderer', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var FormRenderer = require('sale_product_configurator.ProductConfiguratorFormRenderer');
    // var VariantMixin = require('sale.VariantMixin');


    var ProductConfiguratorFormRenderer = FormRenderer.include({

        /**
         * @override
         */
        _onChangeColorAttribute: function (ev) {
            this._super.apply(this, arguments);
            var $parent = $(ev.target).closest('.js_product');
            $parent.find('.css_attribute_color')
                .removeClass("active")
                .filter(':has(input:checked)')
                .addClass("active");
        },

        /**
         * @overwrite
         */
        _getCombinationInfo: function (ev) {
            var self = this;

            var $parent = $(ev.target).closest('.js_product');
            var qty = $parent.find('input[name="add_qty"]').val();
            var combination = this.getSelectedVariantValues($parent);
            var parentCombination = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;
            var productTemplateId = parseInt($parent.find('.product_template_id').val());
            // Custom changes
            var customValues = this.getCustomVariantValues($parent);
            // End custom changes

            self._checkExclusions($parent, combination);

            return ajax.jsonRpc(this._getUri('/sale/get_combination_info'), 'call', {
                'product_template_id': productTemplateId,
                'product_id': this._getProductId($parent),
                'combination': combination,
                'add_qty': parseInt(qty),
                'pricelist_id': this.pricelistId || false,
                'parent_combination': parentCombination,
                // Custom changes
                'custom_values': customValues,
                // End custom changes
            }).then(function (combinationData) {
                self._onChangeCombination(ev, $parent, combinationData);
            });
        },

        /**
         * @overwrite
         */
        handleCustomValues: function ($target) {
            var $variantContainer;
            var $customInput = false;
            if ($target.is('input[type=radio]') && $target.is(':checked')) {
                $variantContainer = $target.closest('ul').closest('li');
                $customInput = $target;
            } else if ($target.is('select')) {
                $variantContainer = $target.closest('li');
                $customInput = $target
                    .find('option[value="' + $target.val() + '"]');
            }

            if ($variantContainer) {
                if ($customInput && $customInput.data('is_custom') === 'True') {
                    var attributeValueId = $customInput.data('value_id');
                    var attributeValueName = $customInput.data('value_name');
                    var has_linear_price = $customInput.data('has_linear_price');
                    var linear_length = $customInput.data('linear_length');

                    if ($variantContainer.find('.variant_custom_value').length === 0
                        || $variantContainer
                            .find('.variant_custom_value')
                            .data('custom_product_template_attribute_value_id') !== parseInt(attributeValueId)) {
                        $variantContainer.find('.variant_custom_value').remove();

                        var $input = $('<input>', {
                            type: 'text',
                            'data-custom_product_template_attribute_value_id': attributeValueId,
                            'data-attribute_value_name': attributeValueName,
                            class: 'variant_custom_value form-control'
                        });

                        var isRadioInput = $target.is('input[type=radio]') &&
                            $target.closest('label.css_attribute_color').length === 0;

                        if (isRadioInput && $customInput.data('is_single_and_custom') !== 'True') {
                            $input.addClass('custom_value_radio');
                            $target.closest('div').after($input);
                        } else {
                            $input.attr('placeholder', attributeValueName);
                            $input.addClass('custom_value_own_line');
                            $variantContainer.append($input);
                        }
                        // Custom changes start here
                        if (has_linear_price) {
                            $input.attr('placeholder', 'Meterage in meter (E.g. 1.25)');
                            $input.attr('value', linear_length)
                        }
                        // End custom changes
                    }
                } else {
                    $variantContainer.find('.variant_custom_value').remove();
                }
            }
        },
    });
    return ProductConfiguratorFormRenderer;
});