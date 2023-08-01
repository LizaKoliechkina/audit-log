from datetime import datetime
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict

from loguru import logger as loguru_logger
from sqlalchemy.exc import SQLAlchemyError

from audit_log_db import AuditLogDatabase, get_audit_log_db
from log_entry_schema import LogEntry

AUDIT_LOG_DB_URL = os.environ.get('AUDIT_LOG_DB_URL')
audit_log_db = AuditLogDatabase(AUDIT_LOG_DB_URL)
db_address = AUDIT_LOG_DB_URL.split('@')[1].split('/')
loguru_logger.debug(f'AuditLog database {db_address[1]} is connected on server {db_address[0]}.')


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = loguru_logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]
        if level == 'INFO':
            level = 'DEBUG'

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        loguru_logger.bind(request_id='app').opt(depth=depth).log(level, record.getMessage())


def customize_logging(config: Dict):
    loguru_logger.remove()
    loguru_logger.add(
        sys.stdout,
        enqueue=True,
        backtrace=True,
        format=config['format']
    )
    loguru_logger.add(
        str(config['path']),
        rotation=config['rotation'],
        retention=config['retention'],
        enqueue=True,
        backtrace=True,
        format=config['format']
    )
    loguru_logger.add(
        log_to_db,
        format='{message}',
        filter=lambda record: record['level'].name == 'INFO'
    )
    for _log in ['uvicorn', 'uvicorn.access']:
        logging.getLogger(_log).handlers = [InterceptHandler()]
    return loguru_logger.bind(request_id=None, method=None)


def load_logging_config(config_path: Path):
    with open(config_path) as config_file:
        config = json.load(config_file)
    return config


def log_to_db(log):
    data = json.loads(log.record['message'])
    data['log_level'] = log.record['level'].name
    data['created_at'] = datetime.now()
    db = next(get_audit_log_db())
    log_entry = LogEntry(**data)
    try:
        db.add(log_entry)
        db.commit()
        return log_entry
    except SQLAlchemyError as ex:
        db.rollback()
        raise Exception(f'Fail to save log entry to the database: {ex}')


def make_logger(config_path: Path):
    config = load_logging_config(config_path)
    logger = customize_logging(
        config.get('logger')
    )
    return logger


config_path = Path(__file__).with_name('config.json')
grt_logger = make_logger(config_path)
