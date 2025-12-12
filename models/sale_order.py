from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    billing_type = fields.Selection([
        ('standard', 'Standard'),
        ('progress', 'Progress / Situation')
    ], string='Billing Type', default='standard', required=True)

    guarantee_retention_rate = fields.Float(string='Guarantee Retention (%)', default=5.0)
    prorata_rate = fields.Float(string='Prorata Account (%)', default=0.0)
    
    progress_billing_step_ids = fields.One2many(
        'sale.order.progress.step', 'sale_order_id', string='Billing Steps'
    )
