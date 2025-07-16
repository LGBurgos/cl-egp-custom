{
    "name": "Hito POS Auto Invoice",
    "version": "18.0",
    "depends": ["point_of_sale", "pos_hide_create_invoice_button"],
    "category": "Point of Sale",
    "summary": "Always enable invoice option by default in POS",
    "data": [
        'views/pos_config.xml'
    ],
    "assets": {
    "point_of_sale._assets_pos": [
        "hito_pos_auto_invoice/static/src/js/auto_invoice.js",
        ],
    },
    "installable": True,
    "application": False,
}
