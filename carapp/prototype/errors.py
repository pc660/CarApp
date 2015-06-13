def HttpRequest_format(Exception):
    """Exception that indicate that http request."""
   
    def __init__(self):
        Exception.__init__()

    def __str__(self):
        s = ("The http request should be a json"
        "object and the request should contain a 'data' attribute"
        return s

