from odoo import models, fields

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    zarinpal_authority = fields.Char(string="Zarinpal Authority", help="Authority token returned by Zarinpal.")
