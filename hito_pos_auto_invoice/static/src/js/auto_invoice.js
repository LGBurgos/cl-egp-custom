/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

console.log("Auto invoice patch loaded!");

console.log("PaymentScreen:", PaymentScreen);
console.log("patch:", patch);

//patch(PaymentScreen.prototype, {
//    setup() {
//        super.setup();
//        console.log("Entra en la función setup del patch");
//        this.currentOrder.set_to_invoice(true);
//
//    }
//});

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        console.log("Entra en la función setup del patch");
        // Verificar si invoice_auto_check está activado en la configuración del POS
        if (this.pos.config.invoice_auto_check) {
            this.currentOrder.set_to_invoice(true);
            console.log("invoice_auto_check activado - Orden marcada para facturar");
        } else {
            console.log("invoice_auto_check desactivado - No se marca para facturar automáticamente");
        }
    }
});