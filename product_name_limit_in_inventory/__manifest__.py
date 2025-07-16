{
    'name': 'Product Name Limit in Inventory',
    'version': '18.0',
    'depends': ['stock'],
    'author': 'Hito - Devman',
    'category': 'Inventory',
    'description': 'Permite configurar el límite de caracteres para el nombre del producto desde el menú de Inventario.',
    'data':[
        'security/ir.model.access.csv',
        'views/product_name_limit_menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}