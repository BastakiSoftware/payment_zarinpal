import logging
import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class PaymentAcquirerZarinpal(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('zarinpal', 'Zarinpal')], ondelete={'zarinpal': 'set default'})

    zarinpal_merchant_id = fields.Char(string="Merchant ID", required_if_provider='zarinpal')

    def zarinpal_get_form_action_url(self):
        return "https://www.zarinpal.com/pg/StartPay/"  # Production URL

    def zarinpal_get_payment_data(self, reference, amount, currency, partner_name, partner_email):
        data = {
            'MerchantID': self.zarinpal_merchant_id,
            'Amount': int(amount),
            'CallbackURL': self.get_base_url() + '/payment/zarinpal/return',
            'Description': f"Payment for {reference}",
        }
        response = requests.post("https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json", json=data)
        response_data = response.json()
        if response_data.get('Status') == 100:
            return response_data['Authority']
        else:
            _logger.error("Zarinpal Error: %s", response_data.get('Errors'))
            raise ValueError("Unable to create Zarinpal payment.")
