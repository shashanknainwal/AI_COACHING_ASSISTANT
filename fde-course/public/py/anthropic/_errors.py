class AnthropicError(Exception):
    pass


class APIError(AnthropicError):
    def __init__(self, message="API error", body=None):
        super().__init__(message)
        self.message = message
        self.body = body


class APIConnectionError(APIError):
    def __init__(self, message="Connection error."):
        super().__init__(message)


class APITimeoutError(APIConnectionError):
    def __init__(self, message="Request timed out."):
        super().__init__(message)


class APIStatusError(APIError):
    status_code = 0

    def __init__(self, message="", body=None, status_code=None):
        super().__init__(message or f"Error code: {status_code or self.status_code}", body)
        if status_code is not None:
            self.status_code = status_code


class BadRequestError(APIStatusError):
    status_code = 400


class AuthenticationError(APIStatusError):
    status_code = 401


class PermissionDeniedError(APIStatusError):
    status_code = 403


class NotFoundError(APIStatusError):
    status_code = 404


class RateLimitError(APIStatusError):
    status_code = 429


class InternalServerError(APIStatusError):
    status_code = 500


class OverloadedError(APIStatusError):
    status_code = 529
