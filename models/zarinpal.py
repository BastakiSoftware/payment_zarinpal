from suds.client import Client
import logging

_logger = logging.getLogger(__name__)

ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'
MMERCHANT_ID = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'  # Replace with your Merchant ID


class PaymentAcquirerZarinpal(models.Model):
    _inherit = 'payment.acquirer'

    def zarinpal_get_form_action_url(self):
        """Generates the payment request and redirects to Zarinpal."""
        try:
            tx = self.env['payment.transaction'].browse(self._context.get('active_id'))
            amount = int(tx.amount * 10)  # Convert to Toman
            description = tx.reference
            callback_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url') + '/payment/zarinpal/verify'

            # Call Zarinpal's PaymentRequest API
            client = Client(ZARINPAL_WEBSERVICE)
            result = client.service.PaymentRequest(
                MMERCHANT_ID, amount, description, tx.partner_email, tx.partner_phone, callback_url
            )
            if result.Status == 100:
                # Save authority for future verification
                tx.sudo().write({'zarinpal_authority': result.Authority})
                return f'https://www.zarinpal.com/pg/StartPay/{result.Authority}'
            else:
                _logger.error("Zarinpal PaymentRequest failed. Status: %s", result.Status)
                raise ValidationError("Error initiating payment. Please try again.")
        except Exception as e:
            _logger.exception("Zarinpal PaymentRequest error: %s", str(e))
            raise ValidationError("Error initiating payment. Please try again.")
