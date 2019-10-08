from enum import Enum


class OperationStatus(Enum):
    NEW = 'NEW'
    PENDING = 'PENDING'
    FAILED = 'FAILED'
    CRITICAL = 'CRITICAL'
    CANCELLED = 'CANCELLED'
    SUCCESS = 'SUCCESS'
