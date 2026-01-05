{
    'name': 'Custom Website Enhancements',
    'version': '18.0.1.0',
    'category': 'Website',
    'summary': 'Customizations for the eCommerce website',
    'description': 'Add custom features and templates to your eCommerce website.',
    'author': 'Your Name or Company',
    'license': 'LGPL-3',
    'depends': ['website', 'website_sale'],
    'data': [
        'security/website_frontend_groups.xml',
        'views/website_index.xml',
    ],
    'installable': True,
    'application': True,  # <--- هذا مهم ليظهر الموديول على واجهة Odoo
    'auto_install': False,
    'groups': ['website_custom.group_website_frontend_dev'],  # يربط الموديول بالمجموعة
}

