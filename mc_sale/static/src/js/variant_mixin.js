odoo.define('mc_sale.VariantMixin', function (require) {
    var VariantMixin = require('sale.VariantMixin');

    VariantMixin.include({
        /**
         * Will add the "custom value" input for this attribute value if
         * the attribute value is configured as "custom" (see product_attribute_value.is_custom)
         *
         * @private
         * @param {MouseEvent} ev
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
                            $input.attr('placeholder', '1.25 m');
                        }
                        // End custom changes
                    }
                } else {
                    $variantContainer.find('.variant_custom_value').remove();
                }
            }
        },
    });
    return VariantMixin;
});