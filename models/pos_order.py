from odoo import models, fields

class PosOrder(models.Model):
    _inherit = "pos.order"

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order",
        help="The Sale Order from which this POS Order was created",
        ondelete="set null"
    )
