from odoo import http
from odoo.http import request
import requests


class ZarinpalController(http.Controller):
    @http.route("/payment/zarinpal/return", type="http", auth="public", csrf=False)
    def zarinpal_return(self, **post):
        acquirer = request.env["payment.acquirer"].search(
            [("provider", "=", "zarinpal")], limit=1
        )
        verify_url = acquirer._zarinpal_get_verify_url()

        data = {
            "merchant_id": acquirer.zarinpal_merchant_id,
            "authority": post.get("Authority"),
            "amount": request.session.get("zarinpal_amount"),
        }

        response = requests.post(verify_url, json=data)
        response_data = response.json()
        if response_data.get("data") and response_data["data"].get("code") == 100:
            # Payment successful
            return request.render("payment.payment_success", {})
        else:
            # Payment failed
            return request.render("payment.payment_failure", {})
