odoo.define('website_pos_bridge.load_orders', function(require) {
    const models = require('point_of_sale.models');

    models.load_models([{
        model: 'pos.order',
        fields: ['name', 'partner_id', 'lines', 'amount_total', 'state'],
        domain: [['state', '!=', 'cancel']], // optionally filter
        loaded: function(self, orders) {
            self.db.all_orders = orders;
            console.log("Loaded POS Orders from bridge:", orders);
        },
    }]);
});
