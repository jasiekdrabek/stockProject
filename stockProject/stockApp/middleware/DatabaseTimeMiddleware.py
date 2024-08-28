import time
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

class DatabaseTimeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Store start time for database operations
        request.db_start_time = time.time()

    def process_response(self, request, response):
        if request.get_full_path() == '/api/deleteDb':
            return response

        if hasattr(request, 'db_start_time'):
            # Measure the total database time
            db_time = sum(float(query['time']) for query in connection.queries)
            # Calculate the time since the request started
            application_time = time.time() - request.db_start_time

            # Log the time taken for database operations
            from stockApp.models import MarketLog
            if hasattr(request, 'request_id'):
                MarketLog.objects.using('test').filter(request_id=request.request_id).update(
                    database_time=db_time,
                    application_time=application_time
                )

        return response