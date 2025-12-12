from odoo import models, fields, api

class SaleOrderProgressStep(models.Model):
    _name = 'sale.order.progress.step'
    _description = 'Sale Order Progress Billing Step'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    sale_order_id = fields.Many2one('sale.order', string='Order', required=True, ondelete='cascade')
    name = fields.Char(string='Description', required=True)
    percentage = fields.Float(string='Percentage (%)', required=True)
    is_billed = fields.Boolean(string='Billed', default=False, copy=False)

    @api.constrains('percentage')
    def _check_percentage(self):
        for step in self:
            if step.percentage < 0 or step.percentage > 100:
                # Warning: Validation generic.
                pass 
