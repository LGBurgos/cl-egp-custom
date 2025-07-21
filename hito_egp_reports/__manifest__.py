{
    "name": "Hito EGP Reports",
    "version": "18.0",
    "depends": ["l10n_ar_purchase","l10n_ar_purchase_stock","sale_management"],
    "category": "purchase",
    "summary": "Change the layout of the purchase order and quote report / sales order",
    "data": [
        'views/account_move.xml',
        'views/res_company.xml',
        'report/report_purchase_order.xml',
        'report/report_purchase_quotation.xml',
        'report/report_sale_order.xml',
        'report/report_invoice_document.xml',
        'report/report_delivery_document.xml',
        'report/report.xml',
    ],
    "installable": True,
    "application": False,
}