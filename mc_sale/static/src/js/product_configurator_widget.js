odoo.define('mc_sale.product_configurator_widget', function (require) {
    var ProductConfiguratorWidget = require('sale_product_configurator.product_configurator');

    /**
     * Overwrite the standard method in order to load values for the custom fields (create mode).
     */
    ProductConfiguratorWidget.include({
        _openConfigurator: function (result, productTemplateId, dataPointId) {
            if (!result.mode || result.mode === 'configurator') {
                this._openProductConfigurator({
                        configuratorMode: result && result.has_optional_products ? 'options' : 'add',
                        default_pricelist_id: this._getPricelistId(),
                        default_product_template_id: productTemplateId,
                        // Custom changes
                        default_tissue_meterage_1: this._getTissueMeterage1(),
                        default_tissue_meterage_2: this._getTissueMeterage2(),
                        default_product_price: this._getProductPrice(),
                        default_product_cost: this._getProductCost(),
                        default_comment: this._getComment(),
                        // End custom changes
                    },
                    dataPointId
                );
                return Promise.resolve(true);
            }
            return Promise.resolve(false);
        },

        /**
         * Overwrite the standard method in order to load values for the custom fields (edit mode).
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
                    // Custom changes
                    default_tissue_meterage_1: this._getTissueMeterage1(),
                    default_tissue_meterage_2: this._getTissueMeterage2(),
                    default_product_price: this._getProductPrice(),
                    default_product_cost: this._getProductCost(),
                    default_comment: this._getComment(),
                    // End custom changes
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
         * Override the standard method in order to save the custom values onto the SO.
         */
        _getMainProductChanges: function (mainProduct) {
            result = this._super.apply(this, arguments);
            result['tissue_meterage_1'] = mainProduct.tissue_meterage_1;
            result['tissue_meterage_2'] = mainProduct.tissue_meterage_2;
            result['comment'] = mainProduct.comment;

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
