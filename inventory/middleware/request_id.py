import uuid

class RequestIDMiddleware:
    """
    Middleware to generate a unique request_id per request
    and attach it to the request object.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())
        response = self.get_response(request)

        # Attach request_id to response if it's JSON
        if hasattr(response, 'data') and isinstance(response.data, dict):
            response.data['request_id'] = request.request_id

        return response
