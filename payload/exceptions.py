import json

class PayloadError(Exception):
    http_code = None
    details = None
    def __init__( self, description=None, details=None ):
        if not description:
            description = self.__class__.__name__
        if details:
            self.details = details
            description += '\n\n'+json.dumps(
                details,
                sort_keys=True,
                indent=4
            )
        super(PayloadError, self).__init__( description )

class UnknownResponse(PayloadError):
    pass

class BadRequest(PayloadError):
    http_code = 400

class InvalidArguments(BadRequest):
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
