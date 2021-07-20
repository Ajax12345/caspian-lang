import typing, sys, functools

class StackLevel:
    pass

class MainLevel(StackLevel):
    def __str__(self) -> str:
        return '<main>'

class FileLevel(StackLevel):
    def __init__(self, _f_path:str) -> None:
        self.f_path = _f_path

    def __str__(self) -> str:
        return self.f_path

class ExecStatus:
    def __init__(self, **kwargs) -> None:
        self._status = kwargs
    
    @property
    def error(self) -> bool:
        return self._status.get('error', False)

    def __getattr__(self, _n:str) -> typing.Any:
        return self._status.get(_n)

def log_errors(_f:typing.Callable) -> typing.Callable:
    @functools.wraps(_f)
    def error_logger(_self, *args, **kwargs) -> typing.Any:
        if isinstance((r:=_f(_self, *args, **kwargs)), ExecStatus) and r.error:
            print(r.error_packet.gen_error)
            sys.exit(0)
        return r
    return error_logger
