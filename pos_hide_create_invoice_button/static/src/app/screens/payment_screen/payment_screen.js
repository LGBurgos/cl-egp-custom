/** @odoo-module */

import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {patch} from "@web/core/utils/patch";
import {onMounted} from "@odoo/owl";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => {
            // console.log("hello World");
            // console.log(this.pos.config.invoice_visibility)
            if (this.pos.config.invoice_visibility) {
                let js_invoice = document.getElementsByClassName('js_invoice');
                (js_invoice.length > 0) && (js_invoice[0].style.visibility = 'hidden');
            }
        });
    }
});
