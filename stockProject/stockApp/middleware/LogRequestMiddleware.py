# stockApp/middleware/LogRequestMiddleware.py
import time
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from stockApp.models import MarketLog

class LogRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Store start time and generate request ID
        request.start_time = time.time()

    def process_response(self, request, response):
        if request.get_full_path() == '/api/deleteDb':
            return response

        # Measure time taken for the view and database operations
        if hasattr(request, 'start_time') and hasattr(response, 'data'):
            total_time = time.time() - request.start_time
            db_time = sum(float(query['time']) for query in connection.queries)
            print(response.data)
            if isinstance(response.data, list):
                id = response.data[-1]["request_id"]
            else:
                id = response.data['request_id']
            # Log the request
            MarketLog.objects.using('test').create(
                api_method=request.method,
                application_time=total_time,
                database_time=db_time,
                endpoint_url=request.get_full_path(),
                request_id=id
            )

        return response
