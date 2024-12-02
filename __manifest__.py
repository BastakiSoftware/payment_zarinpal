{
    'name': 'Zarinpal Payment Gateway',
    'version': '1.0',
    'summary': 'Integration with Zarinpal Payment Gateway',
    'category': 'Accounting/Payment',
    'author': 'Hamed Mohammadi',
    'website': 'https://bastakiss.com',
    'depends': ['payment'],
    'data': [
        'views/payment_acquirer_views.xml',
        'views/payment_acquirer_templates.xml',
        'data/payment_acquirer_data.xml',
        'data/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
