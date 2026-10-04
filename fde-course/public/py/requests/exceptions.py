class RequestException(IOError):
    def __init__(self, *args, response=None, request=None):
        super().__init__(*args)
        self.response = response
        self.request = request if request is not None else getattr(response, "request", None)


class HTTPError(RequestException):
    pass


class ConnectionError(RequestException):
    pass


class Timeout(RequestException):
    pass


class ConnectTimeout(ConnectionError, Timeout):
    pass


class ReadTimeout(Timeout):
    pass


class TooManyRedirects(RequestException):
    pass


class JSONDecodeError(RequestException, ValueError):
    pass
