from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Float(string="Discount Amount", help="Total discount to be applied on the sales order.")

    @api.onchange('discount_amount', 'order_line')
    def _apply_discount(self):
        total_order_amount = sum(line.price_unit * line.product_uom_qty for line in self.order_line)
        
        if total_order_amount > 0:
            discount_ratio = self.discount_amount / total_order_amount
        else:
            discount_ratio = 0

        for line in self.order_line:
            line_discount = line.price_unit * discount_ratio
            line.update({
                'discount': line_discount * 100 / line.price_unit if line.price_unit else 0
            })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(string="Discount (%)", digits=(16, 2), default=0.0, help="Discount applied to this line item.")
