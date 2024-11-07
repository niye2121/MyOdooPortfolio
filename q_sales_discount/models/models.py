from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    activate_sales_discount = fields.Boolean("Activate Sales Discount")
    sales_discount_method = fields.Selection(
        [('fixed', 'Fixed'), ('percentage', 'Percentage')],
        default='percentage',
        string="Sales Discount Method"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update({
            'activate_sales_discount': self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.activate_sales_discount'),
            'sales_discount_method': self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.sales_discount_method'),
        })
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('q_sales_discount.activate_sales_discount', self.activate_sales_discount)
        param.set_param('q_sales_discount.sales_discount_method', self.sales_discount_method)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Float(string="Discount Amount", help="Total discount to be applied on the sales order.")

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'order_line.discount')
    def _compute_amounts(self):
        # Check if sales discount is activated
        activate_discount = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.activate_sales_discount')
        discount_method = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.sales_discount_method')

        # Only apply discounts if the setting is activated
        if activate_discount:
            super(SaleOrder, self)._compute_amounts()
            if discount_method == 'fixed':
                # Fixed discount: Apply evenly distributed fixed amount
                total_order_amount = sum(line.price_subtotal for line in self.order_line)
                discount_ratio = (self.discount_amount / total_order_amount) if total_order_amount else 0
                for line in self.order_line:
                    line_discount = line.price_subtotal * discount_ratio
                    line.update({'discount': line_discount})
            elif discount_method == 'percentage':
                # Percentage discount: Apply based on line subtotal
                for line in self.order_line:
                    line_discount = line.price_subtotal * (self.discount_amount / 100)
                    line.update({'discount': line_discount})

            # Calculate total and update discount amount
            self.amount_total = sum(line.price_total - line.discount for line in self.order_line)
            self.discount_amount = sum(line.discount for line in self.order_line)
        else:
            # If not activated, compute as usual without discount
            super(SaleOrder, self)._compute_amounts()



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(string="Discount", digits=(16, 2), default=0.0, help="Discount applied to this line item.")

    @api.onchange('discount')
    def _apply_discount(self):
        # Fetch discount method from configuration
        discount_method = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.sales_discount_method')

        for line in self:
            if discount_method == 'fixed':
                # Fixed discount - directly subtract a fixed discount amount
                line.price_total = line.price_unit * line.product_uom_qty - line.discount
            elif discount_method == 'percentage':
                # Percentage discount - subtract a percentage-based discount
                line.price_total = line.price_unit * line.product_uom_qty * (1 - line.discount / 100 if line.discount else 1)