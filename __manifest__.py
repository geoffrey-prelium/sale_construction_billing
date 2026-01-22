{
    'name': 'Construction Progress Billing',
    'version': '1.0',
    'author': 'Prelium',
    'category': 'Sales',
    'summary': 'Progress billing, Guarantee Retention, and Prorata for Construction',
    'description': """
        This module adds specific billing features for the construction industry:
        - Progress Billing (Facturation de situation)
        - Guarantee Retention (Retenue de garantie)
        - Prorata Account (Compte prorata)
    """,
    'depends': ['sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizard/sale_advance_payment_inv_views.xml',
        'reports/sale_order_report.xml',
        'reports/account_invoice_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
