from suds.client import Client
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class ZarinpalController(http.Controller):

    @http.route(['/payment/zarinpal/verify'], type='http', auth='public', csrf=False)
    def zarinpal_verify(self, **kwargs):
        """Handles payment verification callback from Zarinpal."""
        try:
            tx_reference = kwargs.get('Authority')
            status = kwargs.get('Status')

            # Locate transaction
            transaction = request.env['payment.transaction'].sudo().search(
                [('zarinpal_authority', '=', tx_reference)], limit=1)
            if not transaction:
                _logger.error("Transaction not found for Authority: %s", tx_reference)
                return "Transaction not found"

            if status == 'OK':
                client = Client(ZARINPAL_WEBSERVICE)
                result = client.service.PaymentVerification(
                    MMERCHANT_ID, tx_reference, int(transaction.amount * 10)
                )
                if result.Status == 100:
                    transaction._set_transaction_done()
                    transaction.sudo().write({'acquirer_reference': str(result.RefID)})
                    _logger.info("Zarinpal Payment successful. RefID: %s", result.RefID)
                    return request.redirect('/payment/process')
                elif result.Status == 101:
                    transaction._set_transaction_done()
                    _logger.info("Zarinpal Payment already verified. Status: %s", result.Status)
                    return request.redirect('/payment/process')
                else:
                    transaction._set_transaction_cancel()
                    _logger.warning("Zarinpal Payment failed. Status: %s", result.Status)
                    return request.redirect('/payment/failure')
            else:
                transaction._set_transaction_cancel()
                _logger.warning("Payment canceled or failed. Status: %s", status)
                return request.redirect('/payment/failure')
        except Exception as e:
            _logger.exception("Zarinpal verification error: %s", str(e))
            return "Internal server error"
