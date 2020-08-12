odoo.define('mc_sale.product_configurator_controller', function (require) {
    var ProductConfiguratorFormController = require('sale_product_configurator.ProductConfiguratorFormController');

    ProductConfiguratorFormController.include({
        init: function () {
            this._super.apply(this, arguments);
            this.tissueMeterage1 = 0;
            this.tissueMeterage2 = 0;
            this.comment = '';
        },

        /**
         * This is overridden to allow catching the "select" event on our product template select field.
         *
         * @override
         * @private
         */
        _onFieldChanged: function (event) {
            if (event.data.changes.tissue_meterage_1){
                this.tissueMeterage1 = event.data.changes.tissue_meterage_1
            }
            if (event.data.changes.tissue_meterage_2){
                this.tissueMeterage2 = event.data.changes.tissue_meterage_2
            }
            if (event.data.changes.comment){
                this.comment = event.data.changes.comment
            }
            if (!event.data.changes.product_template_id){
                event.data.changes['product_template_id'] = {id: this.current_product_template_id}
            }
            this._super.apply(this, arguments);
        },

        /**
         * This triggers the close action for the window and
         * adds the product as the "infos" parameter.
         * It will allow the caller (typically the product_configurator widget) of this window
         * to handle the added products.
         *
         * @private
         * @param {Array} products the list of added products
         *   {integer} products.product_id: the id of the product
         *   {integer} products.quantity: the added quantity for this product
         *   {Array} products.product_custom_attribute_values:
         *     see variant_mixin.getCustomVariantValues
         *   {Array} products.no_variant_attribute_values:
         *     see variant_mixin.getNoVariantAttributeValues
         */
        _addProducts: function (products) {
            products[0]['tissue_meterage_1'] = this.tissueMeterage1;
            products[0]['tissue_meterage_2'] = this.tissueMeterage2;
            products[0]['comment'] = this.comment;
            this.do_action({type: 'ir.actions.act_window_close', infos: {
                    mainProduct: products[0],
                    options: products.slice(1)
                }});
        },
    });

    return ProductConfiguratorFormController;

});