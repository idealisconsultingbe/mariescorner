odoo.define('mc_sale.product_configurator_controller', function (require) {
    var ProductConfiguratorFormController = require('sale_product_configurator.ProductConfiguratorFormController');

    ProductConfiguratorFormController.include({
        init: function () {
            this._super.apply(this, arguments);
            this.comment = 'None';
            this.product_cost = -1;
        },

        /**
         * Override the standard method in order to catch changes of custom values.
         */
        _onFieldChanged: function (event) {
            if ('comment' in event.data.changes){
                this.comment = event.data.changes.comment
            }
            if ('product_cost' in event.data.changes){
                this.product_cost = event.data.changes.product_cost
            }
            if (!('product_template_id' in event.data.changes)){
                event.data.changes['product_template_id'] = {id: false}
            }
            var self = this;
            var productId = event.data.changes.product_template_id.id;

            // check to prevent traceback when emptying the field
            if (productId) {
                this._configureProduct(event.data.changes.product_template_id.id)
                    .then(function () {
                        self.renderer.renderConfigurator(self.renderer.configuratorHtml);
                    });
            }
        },

        /**
         * Override the standard method in order to send to the product configurator widget the custom values.
         */
        _addProducts: function (products) {
            products[0]['comment'] = this.comment;
            products[0]['product_cost'] = this.product_cost;
            this._super.apply(this, arguments);
        },
    });

    return ProductConfiguratorFormController;

});