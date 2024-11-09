from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Float(
        string="Discount Amount",
        help="Total discount amount applied to the sales order."
    )
    
    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.discount')
    def _compute_amounts(self):
        super(SaleOrder, self)._amount_all()
        activate_discount = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.activate_sales_discount')
        discount_method = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.sales_discount_method')
        _logger.info(f"_compute_amounts   ====activate_discount: {activate_discount}, discount_method: {discount_method}")
        for order in self:
            if activate_discount:
                if discount_method == 'fixed':
                    # Fixed discount directly from order's discount_amount
                    discount_amount = sum(line.discount for line in order.order_line)
                    _logger.info(f"discount_amount===: {discount_amount}")
                    order.amount_total -= discount_amount
                elif discount_method == 'percentage':
                    # Calculate total discount as percentage-based
                    total_discount = sum(line.price_subtotal * (order.discount_amount / 100) for line in order.order_line)
                    _logger.info(f"total_discount===: {total_discount}")
                    order.amount_total -= total_discount
                    order.discount_amount = total_discount
           

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(string="Discount (%)", digits=(16, 2), default=0.0, help="Discount percentage applied to this line item.")

    @api.depends('discount', 'price_unit', 'product_uom_qty')
    def _compute_discounted_price(self):
        discount_method = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.sales_discount_method')
        activate_sales_discount = self.env['ir.config_parameter'].sudo().get_param('q_sales_discount.activate_sales_discount')
        _logger.info(f"discount_method: {discount_method}, activate_sales_discount: {activate_sales_discount}")
        for line in self:
            if activate_sales_discount:
                if discount_method == 'fixed':
                    discount_amount = line.price_unit * line.product_uom_qty - line.discount
                    _logger.info(f"discount_amount: {discount_amount}")
                    line.price_total = discount_amount
                elif discount_method == 'percentage':
                    discount_amount = line.price_unit * line.product_uom_qty * (1 - line.discount / 100)
                    _logger.info(f"discount_amount: {discount_amount}")
                    line.price_total = discount_amount
           