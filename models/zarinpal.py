import requests
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

ZARINPAL_WEBSERVICE = "https://www.zarinpal.com/pg/services/WebGate/wsdl"
MMERCHANT_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # Replace with your Merchant ID


def get_access_token(client_id, client_secret):
    url = "https://next.zarinpal.com/api/v4/graphql/"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    headers = {"Accept": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        _logger.error("Failed to obtain access token: %s", response.text)
        raise ValidationError("Could not obtain access token.")


class PaymentAcquirerZarinpal(models.Model):
    _inherit = "payment.acquirer"

    def zarinpal_get_form_action_url(self):
        """Generates the payment request and redirects to Zarinpal using GraphQL."""
        try:
            tx = self.env["payment.transaction"].browse(self._context.get("active_id"))
            amount = int(tx.amount * 10)  # Convert to Toman
            description = tx.reference
            callback_url = (
                self.env["ir.config_parameter"].sudo().get_param("web.base.url")
                + "/payment/zarinpal/verify"
            )

            # Get Access Token
            access_token = get_access_token("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET")

            # Prepare GraphQL query
            query = {
                "query": """
                    mutation {
                        createPayment(input: {
                            amount: %d,
                            description: "%s",
                            email: "%s",
                            phone: "%s",
                            callbackUrl: "%s"
                        }) {
                            authority
                            status
                        }
                    }
                """
                % (
                    amount,
                    description,
                    tx.partner_email,
                    tx.partner_phone,
                    callback_url,
                )
            }

            # Send GraphQL request
            response = requests.post(
                "https://next.zarinpal.com/api/v4/graphql/",
                json=query,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )

            result = response.json()
            if (
                response.status_code == 200
                and result["data"]["createPayment"]["status"] == "SUCCESS"
            ):
                authority = result["data"]["createPayment"]["authority"]
                tx.sudo().write({"zarinpal_authority": authority})
                return f"https://www.zarinpal.com/pg/StartPay/{authority}"
            else:
                _logger.error("Zarinpal PaymentRequest failed. Response: %s", result)
                raise ValidationError("Error initiating payment. Please try again.")
        except Exception as e:
            _logger.exception("Zarinpal PaymentRequest error: %s", str(e))
            raise ValidationError("Error initiating payment. Please try again.")
