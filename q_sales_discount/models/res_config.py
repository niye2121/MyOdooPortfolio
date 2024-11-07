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

