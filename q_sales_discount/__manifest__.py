{
    'name': 'Sales Order Line Item Discount',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Applies discounts on line items in sales orders by distributing a specified discount amount across the total order.',
    'description': """
        This module allows you to apply a specified discount amount on sales orders, distributing it evenly across all line items. It calculates and updates each line item’s discount based on its contribution to the total order amount.
    """,
    'author': 'Nigist(Queen)',
    'website': 'https://github.com/yourusername/odoo-portfolio',
    'depends': ['sale'],
    'data': [
        'views/sale_order_view.xml',
        'views/res_setting_config_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
