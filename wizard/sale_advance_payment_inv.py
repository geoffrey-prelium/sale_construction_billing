from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    advance_payment_method = fields.Selection(selection_add=[
        ('progress_situation', 'Progress Situation (Construction)')
    ], ondelete={'progress_situation': 'cascade'})

    situation_percentage = fields.Float(string='Situation Percentage')

    @api.onchange('advance_payment_method')
    def _onchange_advance_payment_method_construction(self):
        if self.advance_payment_method == 'progress_situation':
            self.amount = 0 # Not used but good to reset
            # Try to find next logical percentage
            active_ids = self._context.get('active_ids')
            if active_ids:
                sale_order = self.env['sale.order'].browse(active_ids[0])
                if sale_order.billing_type == 'progress':
                    # Find next unbilled step
                    next_step = sale_order.progress_billing_step_ids.filtered(lambda s: not s.is_billed)
                    if next_step:
                        self.situation_percentage = next_step[0].percentage

    def _create_invoices(self, sale_orders):
        # Separation of concern: if creating progress situation, handle specifically
        situation_orders = sale_orders.filtered(lambda so: self.advance_payment_method == 'progress_situation')
        standard_orders = sale_orders - situation_orders
        
        invoices = self.env['account.move']
        if standard_orders:
            invoices = super(SaleAdvancePaymentInv, self)._create_invoices(standard_orders)

        if situation_orders:
            # Create down payment logic for construction
            self._create_construction_invoices(situation_orders)
            # Re-fetch invoices related to these orders to return them or add to list
            # We need to find newly created invoices.
            new_invoices = situation_orders.invoice_ids.sorted(key=lambda i: i.create_date, reverse=True)[:len(situation_orders)]
            invoices += new_invoices
        
        return invoices

    def _create_construction_invoices(self, sale_orders):
        product_id = self._default_product_id()
        if not product_id:
             raise UserError(_("Please define a down payment product in the sales settings."))

        for order in sale_orders:
            # Calculate amount (Situation Percentage of Total)
            amount_total = order.amount_total
            situation_amount = amount_total * (self.situation_percentage / 100.0)
            
            # 1. Prepare taxes
            taxes = product_id.taxes_id.filtered(lambda t: t.company_id == order.company_id)
            if order.fiscal_position_id:
                taxes = order.fiscal_position_id.map_tax(taxes)

            # 2. Create Down Payment Line on SO
            # Ensure section exists
            order._create_down_payment_section_line_if_needed()
            
            # Create the SO Line
            # We treat situation amount as "Fixed Amount" (Tax Included usually) behavior for simplicity in this custom flow
            # If taxes are price_included, price_unit = situation_amount
            # If taxes are excluded, price_unit = situation_amount / (1 + tax_rate) ... this is complicated.
            # STANDARD ODOO DP BEHAVIOR:
            # 'fixed' method: user inputs generic amount.
            context = {'lang': order.partner_id.lang}
            dp_name = _('Situation %s%%') % self.situation_percentage
            
            dp_line_values = {
                'name': dp_name,
                'is_downpayment': True,
                'order_id': order.id,
                'product_id': product_id.id,
                'price_unit': situation_amount, 
                'product_uom_qty': 0,
                'qty_delivered': 0,
                'tax_ids': [(6, 0, taxes.ids)],
                'sequence': max(order.order_line.mapped('sequence') or [10]) + 1,
            }
            dp_line = self.env['sale.order.line'].create(dp_line_values)
            
            del context

            # 3. Create Invoice
            invoice_vals = order._prepare_invoice()
            invoice_lines = []

            # A. Situation Line (positive)
            invoice_lines.append((0, 0, {
                'name': dp_name,
                'price_unit': situation_amount,
                'quantity': 1.0,
                'product_id': product_id.id,
                'product_uom_id': product_id.uom_id.id,
                'tax_ids': [(6, 0, taxes.ids)],
                'sale_line_ids': [(6, 0, [dp_line.id])],
            }))
            
            # B. Guarantee Retention (negative)
            if order.guarantee_retention_rate > 0:
                retention_amount = situation_amount * (order.guarantee_retention_rate / 100.0)
                invoice_lines.append((0, 0, {
                    'name': _('Retenue de Garantie (%.2f%%)') % order.guarantee_retention_rate,
                    'price_unit': -retention_amount,
                    'quantity': 1.0,
                    'product_id': product_id.id,
                    'product_uom_id': product_id.uom_id.id,
                    'tax_ids': [], # Usually no tax on retention hooks
                }))
                
            # C. Prorata (negative)
            if order.prorata_rate > 0:
                prorata_amount = situation_amount * (order.prorata_rate / 100.0)
                invoice_lines.append((0, 0, {
                    'name': _('Compte Prorata (%.2f%%)') % order.prorata_rate,
                    'price_unit': -prorata_amount,
                    'quantity': 1.0,
                    'product_id': product_id.id, 
                    'product_uom_id': product_id.uom_id.id,
                    'tax_ids': [],
                }))
                
            invoice_vals['invoice_line_ids'] = invoice_lines
            
            # Create and Post Invoice
            # Odoo 16+ often leaves it draft. We can leave it draft.
            self.env['account.move'].create(invoice_vals)
            
            # 4. Update Billing Step
            matching_step = order.progress_billing_step_ids.filtered(
                lambda s: not s.is_billed and abs(s.percentage - self.situation_percentage) < 0.01
            )
            if matching_step:
                matching_step.is_billed = True

    def _default_product_id(self):
        # 1. Try Config Parameter
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        if product_id:
            return self.env['product.product'].browse(int(product_id))
        
        # 2. Try generic search
        product = self.env['product.product'].search([('default_code', '=', 'DEPOSIT')], limit=1) or \
                  self.env['product.product'].search([('name', '=', 'Down Payment')], limit=1) or \
                  self.env['product.product'].search([('name', '=', 'Acompte')], limit=1)
        
        if product:
            return product
            
        # 3. Auto-create if missing (User cannot find setting)
        vals = {
            'name': _('Down Payment'),
            'type': 'service',
            'invoice_policy': 'order',
            'default_code': 'DEPOSIT',
            'taxes_id': [], # Avoid default taxes ? Or let default?
        }
        # Ideally set a good category or accounting options, but default is better than blocking.
        product = self.env['product.product'].create(vals)
        
        # Save it to config for next time
        self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', product.id)
        
        return product 
