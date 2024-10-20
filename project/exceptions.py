class BaseError(Exception):
    def __init__(self, msg=None, error_code=50000):
        Exception.__init__(self)
        self.code = 500  # http status code
        self.error_code = error_code  # customize code
        self.error_msg = msg

    def to_dict(self):
        return {'code': self.error_code, 'message': self.error_msg}


class APIError(BaseError):
    status_code = 400
    type = 'invalid_request_error'
    message = ''
    detail = ''
    code = '400'

    def __init__(self, msg=None, detail=None, status=None, payload=None):
        if msg is None:
            msg = self.message
        if status is None:
            status = self.status_code
        self.status_code = status
        self.message = msg
        if payload is None:
            payload = {
                'failure_code': self.code,
                'failure_msg': self.message if detail is None else detail,
            }
        self.payload = payload
        super(APIError, self).__init__(self.message)

    def to_dict(self):
        return dict(
            type=self.type,
            message=self.message,
            code=self.code,
            payload=self.payload)


class ValidationError(APIError):
    code = 40001
    message = "params error"
    type = "invalid_request"
