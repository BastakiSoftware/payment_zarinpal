from odoo import http
from odoo.http import request

class ZarinpalController(http.Controller):

    @http.route(['/payment/zarinpal/return'], type='http', auth='public', csrf=False)
    def zarinpal_return(self, **kwargs):
        _logger.info("Zarinpal return data: %s", kwargs)
        authority = kwargs.get('Authority')
        status = kwargs.get('Status')
        if status == 'OK':
            # Verify transaction
            transaction = request.env['payment.transaction'].sudo().search([('reference', '=', authority)], limit=1)
            if transaction:
                transaction._set_transaction_done()
                return request.redirect('/payment/process')
        return request.redirect('/payment/failure')
