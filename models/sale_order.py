from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_pos_order_vals_from_sale(self, session):
        """Prepare POS Order values from the Sale Order."""
        self.ensure_one()
        order_lines = []
        amount_total = 0.0
        amount_tax = 0.0

        currency = self.pricelist_id.currency_id

        for line in self.order_line:
            # Compute taxes for line
            taxes = line.tax_id.compute_all(
                line.price_unit,
                currency=currency,
                quantity=line.product_uom_qty,
                product=line.product_id,
                partner=self.partner_id,
            )

            line_subtotal_excl = taxes['total_excluded']
            line_subtotal_incl = taxes['total_included']
            line_tax = line_subtotal_incl - line_subtotal_excl

            amount_total += line_subtotal_incl
            amount_tax += line_tax

            order_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'qty': line.product_uom_qty,
                'price_unit': line.price_unit,
                'discount': line.discount or 0.0,
                'tax_ids': [(6, 0, line.tax_id.ids)],
                # ✅ mandatory fields for pos.order.line
                'price_subtotal': line_subtotal_excl,
                'price_subtotal_incl': line_subtotal_incl,
            }))

        vals = {
            'session_id': session.id,
            'pricelist_id': self.pricelist_id.id,
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
            'lines': order_lines,
            # ✅ mandatory fields for pos.order
            'amount_total': amount_total,
            'amount_tax': amount_tax,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        }
        return vals

    def create_pos_order_from_sale(self, session):
        self.ensure_one()
        vals = self._prepare_pos_order_vals_from_sale(session)
        pos_order = self.env['pos.order'].create(vals)
        return pos_order

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        # Find an open POS session for Kitchen KDS
        session = self.env['pos.session'].search([
            ('state', '=', 'opened'),
            ('config_id.name', '=', 'Kitchen KDS')
        ], limit=1)

        if not session:
            raise UserError(_("No open POS session found for Kitchen KDS"))

        for order in self:
            order.create_pos_order_from_sale(session)

        return res
