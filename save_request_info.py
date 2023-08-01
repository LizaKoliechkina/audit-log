import json
import typing as T
from functools import wraps

from audit_log.log_entry_model import EventType
from audit_log.logger import grt_logger


def save_request_info_log(event_type: EventType) -> T.Callable:
    def wrapper(func: T.Callable) -> T.Callable:
        @wraps(func)
        async def inner(*args, **kwargs) -> T.Any:
            result = await func(*args, **kwargs)
            request = kwargs['request']
            event = f'{request.method}_{func.__name__.upper()}'
            request_params = kwargs.copy()
            request_params.pop('request', None)
            request_params.pop('db', None)
            request_params = f'Request params: {request_params}' if request_params else ''

            grt_logger.info(json.dumps({
                'user_id': request.state.id,
                'user_name': request.state.user_name,
                'event_type': event_type.name,
                'event': event,
                'message': f'Request processed successfully. {request_params}',
            }))

            return result
        return inner
    return wrapper
