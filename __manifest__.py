{
    'name': "Provision",
    'summary': "Calculate & Record Provisions",
    'description': """
    This module would be useable for adding provisions to product categories to update their cost while receiving products
    """,
    'author': "AxiomTeam",
    'website': "http://www.example.com",
    'category': 'Tools',
    'version': '16.1.0.1.0',
    'depends': ['purchase', 'sale_management', 'account_accountant', 'stock'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/provision_security.xml',
        'views/provision.xml',
        'views/sub_provision.xml',
        'views/product_template_ext.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
