# stockApp/middleware/LogRequestMiddleware.py
import datetime
import time
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from stockApp.models import MarketLog

class LogRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Store start time
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time') and hasattr(response, 'data'):
            total_time = time.time() - request.start_time
            db_time = sum(float(query['time']) for query in connection.queries)
            id = None
            if isinstance(response.data, list) and 'request_id' in response.data[-1]:
                id = response.data[-1]["request_id"]
            if isinstance(response.data, dict) and 'request_id' in response.data:
                id = response.data['request_id']
            if id:
                MarketLog.objects.using('test').create(
                    api_method=request.method,
                    application_time=total_time,
                    database_time=db_time,
                    endpoint_url=request.get_full_path(),
                    request_id=id,
                    timestamp = datetime.datetime.now()
                )

        return response
