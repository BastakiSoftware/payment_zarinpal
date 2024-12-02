from odoo import models, fields, api
import requests
import json

class PaymentAcquirerZarinpal(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(selection_add=[("zarinpal", "Zarinpal")], ondelete={"zarinpal": "set default"})
    zarinpal_merchant_id = fields.Char(string="Merchant ID", required_if_provider="zarinpal")

    def _zarinpal_get_api_url(self):
        return "https://sandbox.zarinpal.com/pg/v4/payment/request.json" if self.state == "test" else "https://www.zarinpal.com/pg/v4/payment/request.json"

    def _zarinpal_get_verify_url(self):
        return "https://sandbox.zarinpal.com/pg/v4/payment/verify.json" if self.state == "test" else "https://www.zarinpal.com/pg/v4/payment/verify.json"

    def _zarinpal_request_payment(self, values):
        url = self._zarinpal_get_api_url()
        headers = {"Content-Type": "application/json"}
        data = {
            "merchant_id": self.zarinpal_merchant_id,
            "amount": values.get("amount"),
            "callback_url": values.get("return_url"),
            "description": values.get("description", "Payment via Odoo"),
            "metadata": {
                "email": values.get("payer_email"),
                "mobile": values.get("payer_phone"),
            },
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response_data = response.json()
        if response_data.get("data") and response_data["data"].get("code") == 100:
            return response_data["data"]["authority"]
        else:
            raise Exception(response_data.get("errors", {}).get("message", "Zarinpal payment request failed"))

    def zarinpal_form_generate_values(self, values):
        authority = self._zarinpal_request_payment(values)
        return {
            "action_url": f"https://sandbox.zarinpal.com/pg/StartPay/{authority}" if self.state == "test" else f"https://www.zarinpal.com/pg/StartPay/{authority}"
        }

    def zarinpal_get_return_url(self):
        return self._zarinpal_get_verify_url()
