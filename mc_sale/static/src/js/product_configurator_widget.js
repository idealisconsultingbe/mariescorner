odoo.define('mc_sale.product_configurator_widget', function (require) {
    var ProductConfiguratorWidget = require('sale_product_configurator.product_configurator');

    /**
     * Extension of the ProductConfiguratorWidget to support product configuration.
     * It opens when a configurable product_template is set.
     * (multiple variants, or custom attributes)
     *
     * The product customization information includes :
     * - is_configurable_product
     * - product_template_attribute_value_ids
     *
     */
    ProductConfiguratorWidget.include({
        _openConfigurator: function (result, productTemplateId, dataPointId) {
            if (!result.mode || result.mode === 'configurator') {
                this._openProductConfigurator({
                        configuratorMode: result && result.has_optional_products ? 'options' : 'add',
                        default_pricelist_id: this._getPricelistId(),
                        default_product_template_id: productTemplateId,
                        default_tissue_meterage_1: this._getTissueMeterage1(),
                        default_tissue_meterage_2: this._getTissueMeterage2(),
                        default_product_price: this._getProductPrice(),
                        default_product_cost: this._getProductCost(),
                        default_comment: this._getComment(),
                    },
                    dataPointId
                );
                return Promise.resolve(true);
            }
            return Promise.resolve(false);
        },

        /**
         * Opens the product configurator in "edit" mode.
         * (see '_openProductConfigurator' for more info on the "edit" mode).
         * The requires to retrieve all the needed data from the SO line
         * that are kept in the "recordData" object.
         *
         * @private
         */
        _onEditProductConfiguration: function () {
            if (!this.recordData.is_configurable_product) {
                // if line should be edited by another configurator
                // or simply inline.
                this._super.apply(this, arguments);
                return;
            }
            // If line has been set up through the product_configurator:
            this._openProductConfigurator({
                    configuratorMode: 'edit',
                    default_product_template_id: this.recordData.product_template_id.data.id,
                    default_pricelist_id: this._getPricelistId(),
                    default_tissue_meterage_1: this._getTissueMeterage1(),
                    default_tissue_meterage_2: this._getTissueMeterage2(),
                    default_product_price: this._getProductPrice(),
                    default_product_cost: this._getProductCost(),
                    default_comment: this._getComment(),
                    default_product_template_attribute_value_ids: this._convertFromMany2Many(
                        this.recordData.product_template_attribute_value_ids
                    ),
                    default_product_no_variant_attribute_value_ids: this._convertFromMany2Many(
                        this.recordData.product_no_variant_attribute_value_ids
                    ),
                    default_product_custom_attribute_value_ids: this._convertFromOne2Many(
                        this.recordData.product_custom_attribute_value_ids
                    ),
                    default_quantity: this.recordData.product_uom_qty
                },
                this.dataPointID
            );
        },

        /**
         * This will convert the result of the product configurator into
         * "changes" that are understood by the basic_model.js
         *
         * For the product_custom_attribute_value_ids, we need to do a DELETE_ALL
         * command to clean the currently selected values and then a CREATE for every
         * custom value specified in the configurator.
         *
         * For the product_no_variant_attribute_value_ids, we also need to do a DELETE_ALL
         * command to clean the currently selected values and issue a single ADD_M2M containing
         * all the ids of the product_attribute_values.
         *
         * @param {Object} mainProduct
         *
         * @private
         */
        _getMainProductChanges: function (mainProduct) {
            var result = {
                product_id: {id: mainProduct.product_id},
                product_template_id: {id: mainProduct.product_template_id},
                product_uom_qty: mainProduct.quantity,
                tissue_meterage_1: mainProduct.tissue_meterage_1,
                tissue_meterage_2: mainProduct.tissue_meterage_2,
                comment: mainProduct.comment
            };

            var customAttributeValues = mainProduct.product_custom_attribute_values;
            var customValuesCommands = [{operation: 'DELETE_ALL'}];
            if (customAttributeValues && customAttributeValues.length !== 0) {
                _.each(customAttributeValues, function (customValue) {
                    // FIXME awa: This could be optimized by adding a "disableDefaultGet" to avoid
                    // having multiple default_get calls that are useless since we already
                    // have all the default values locally.
                    // However, this would mean a lot of changes in basic_model.js to handle
                    // those "default_" values and set them on the various fields (text,o2m,m2m,...).
                    // -> This is not considered as worth it right now.
                    customValuesCommands.push({
                        operation: 'CREATE',
                        context: [{
                            default_custom_product_template_attribute_value_id: customValue.custom_product_template_attribute_value_id,
                            default_custom_value: customValue.custom_value
                        }]
                    });
                });
            }

            result['product_custom_attribute_value_ids'] = {
                operation: 'MULTI',
                commands: customValuesCommands
            };

            var noVariantAttributeValues = mainProduct.no_variant_attribute_values;
            var noVariantCommands = [{operation: 'DELETE_ALL'}];
            if (noVariantAttributeValues && noVariantAttributeValues.length !== 0) {
                var resIds = _.map(noVariantAttributeValues, function (noVariantValue) {
                    return {id: parseInt(noVariantValue.value)};
                });

                noVariantCommands.push({
                    operation: 'ADD_M2M',
                    ids: resIds
                });
            }

            result['product_no_variant_attribute_value_ids'] = {
                operation: 'MULTI',
                commands: noVariantCommands
            };

            return result;
        },

        /**
         * Returns the tissue_meterage_1 set on the sale_order_line
         *
         * @private
         * @returns {float} tissue_meterage_1's value
         */
        _getTissueMeterage1: function () {
            return this.record.evalContext.tissue_meterage_1;
        },

        /**
         * Returns the tissue_meterage_2 set on the sale_order_line
         *
         * @private
         * @returns {float} tissue_meterage_2's value
         */
        _getTissueMeterage2: function () {
            return this.record.evalContext.tissue_meterage_2;
        },

        /**
         * Returns the product_price set on the sale_order_line
         *
         * @private
         * @returns {float} product_price's value
         */
        _getProductPrice: function () {
            return this.record.evalContext.product_price;
        },

        /**
         * Returns the product_price set on the sale_order_line
         *
         * @private
         * @returns {float} product_price's value
         */
        _getProductCost: function () {
            return this.record.evalContext.product_cost;
        },

        /**
         * Returns the product_price set on the sale_order_line
         *
         * @private
         * @returns {float} product_price's value
         */
        _getComment: function () {
            return this.record.evalContext.comment;
        },
    });

    return ProductConfiguratorWidget;

});
