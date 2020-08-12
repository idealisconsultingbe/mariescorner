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
         * Override the standard method in order to catch changes of custom values.
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
         * Override the standard method in order to send to the product configurator widget the custom values.
         */
        _addProducts: function (products) {
            products[0]['tissue_meterage_1'] = this.tissueMeterage1;
            products[0]['tissue_meterage_2'] = this.tissueMeterage2;
            products[0]['comment'] = this.comment;
            this._super.apply(this, arguments);
        },
    });

    return ProductConfiguratorFormController;

});