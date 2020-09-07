import json

class PayloadError(Exception):
    http_code = None
    details = None
    response = None
    def __init__( self, description=None, response=None ):
        if not description:
            description = self.__class__.__name__
        if response:
            self.response = response
            self.details = self.response.get('details')
            description += '\n\n'+json.dumps(
                response,
                sort_keys=True,
                indent=4
            )
        super(PayloadError, self).__init__( description )

class UnknownResponse(PayloadError):
    pass

class BadRequest(PayloadError):
    http_code = 400

class TransactionDeclined(BadRequest):
    def __init__(self, *args, **kwargs):
        from .utils import map_object
        super().__init__(*args, **kwargs)
        self.transaction = self.details = map_object(self.response['details'])

class InvalidAttributes(BadRequest):
    pass

class Unauthorized(PayloadError):
    http_code = 401

class Forbidden(PayloadError):
    http_code = 403

class NotFound(PayloadError):
    http_code = 404

class TooManyRequests(PayloadError):
    http_code = 429

class InternalServerError(PayloadError):
    http_code = 500

class ServiceUnavailable(PayloadError):
    http_code = 503
