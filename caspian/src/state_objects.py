import typing, sys, functools

class ExecStatus:
    def __init__(self, **kwargs) -> None:
        self._status = kwargs
    
    @property
    def error(self) -> bool:
        return self._status.get('error', False)

    def __getattr__(self, _n:str) -> typing.Any:
        return self._status.get(_n)


