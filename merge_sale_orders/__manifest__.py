# -*- coding: utf-8 -*-
{
    'name': 'Merge Sale Orders',
    'summary': "merge your existing sales order which are in Draft/Sent Stage Orders",
    'description': "merge your existing sales order which are in Draft/Sent Stage Orders",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Sales',
    'version': '18.0.0.1.0',
    'depends': ['sale_management'],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'wizard/merge_order.xml',
    ],

    'license': "OPL-1",

    'auto_install': False,
    'installable': True,

    'images': ['static/description/banner.png'],
    'pre_init_hook': 'pre_init_check',
}
