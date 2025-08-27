# home/middleware/json_middleware.py
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from home.utils import responses

class JsonResponseMiddleware(MiddlewareMixin):
    """
    Converts common errors into JSON responses.
    """

    def process_exception(self, request, exception):
        # Handle unhandled exceptions → 500
        return responses.server_error(str(exception))

    def process_response(self, request, response):
        # Convert 404 or 403 into JSON
        if response.status_code == 404:
            return responses.not_found("The requested resource was not found")
        elif response.status_code == 403:
            return responses.unauthorized("Permission denied")
        return response
