{
    "name": "L10n AR Withholding Manual Amount",
    "version": "18.0.1.0.0",
    "category": "Localization/Argentina",
    "summary": "Permite editar manualmente el monto de retenciones en pagos",
    "description": """
        Este módulo permite que el usuario edite manualmente el monto de una 
        retención en pagos de clientes, evitando que el onchange lo sobrescriba.
        
        Solución al ticket #3793 - El sistema recalcula retenciones (EGP).
        
        Cómo funciona:
        - Agrega un campo 'Monto Manual' en las líneas de retención
        - Cuando el usuario edita el monto, se marca automáticamente como manual
        - El cálculo automático respeta los montos marcados como manuales
        - Un botón permite volver al cálculo automático si se desea
    """,
    "author": "Hitofusion",
    "website": "https://www.hitofusion.com",
    "license": "LGPL-3",
    "depends": [
        "l10n_ar_tax_fix",
    ],
    "data": [
        "views/account_payment_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
