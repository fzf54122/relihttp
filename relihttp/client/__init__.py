__all__ = ["SyncClient", "AsyncClient", "ClientTypeEnum", "AbstractClient"]

from .AsyncClient import AsyncClient
from .SyncClient import SyncClient

class ClientTypeEnum(object):
    SYNC = "sync"
    ASYNC = "async"

class AbstractClient:

    @classmethod
    def create_client(cls, mode,**kwargs):
        if mode == ClientTypeEnum.SYNC:
            return SyncClient(**kwargs)
        elif mode == ClientTypeEnum.ASYNC:
            return AsyncClient(**kwargs)
        else:
            raise ValueError("Invalid mode: {}".format(mode))