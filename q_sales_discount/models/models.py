from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Float(
        string="Discount Amount",
        help="Total fixed discount to be applied on the sales order."
    )
    

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'order_line.discount')
    def _compute_amounts(self):
        super(SaleOrder, self)._compute_amounts()
        # Check if sales discount is activated
        activate_discount = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.activate_sales_discount')
        discount_method = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.sales_discount_method')

        for order in self:
            if activate_discount and discount_method == 'fixed':
                # Apply the fixed discount amount directly to the total
                order.amount_total = sum(line.price_total for line in order.order_line) - order.discount_amount
            elif activate_discount and discount_method == 'percentage':
                # Apply a percentage-based discount on each line
                total_discount = sum(line.price_subtotal * (order.discount_amount / 100) for line in order.order_line)
                order.amount_total = sum(line.price_total for line in order.order_line) - total_discount
                order.discount_amount = total_discount
            else:
                # If discounts are not activated, calculate the total as usual
                order.amount_total = sum(line.price_total for line in order.order_line)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(string="Discount", digits=(16, 2), default=0.0, help="Discount applied to this line item.")

    @api.onchange('discount')
    def _apply_discount(self):
        # Fetch discount method from configuration
        discount_method = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.sales_discount_method')

        for line in self:
            if discount_method == 'fixed':
                # Apply a fixed discount amount directly to price_total
                line.price_total = line.price_unit * line.product_uom_qty - line.discount
            elif discount_method == 'percentage':
                # Apply a percentage-based discount
                line.price_total = line.price_unit * line.product_uom_qty * (1 - line.discount / 100 if line.discount else 1)
