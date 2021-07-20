import typing, sys, functools
import warnings, internal_errors
import copy

class Scopes:
    class ScopeBase:
        def __str__(self) -> str:
            return f"<scope '{self.name}'>"

        @property
        def name(self) -> str:
            return self.__class__.__name__

        def __repr__(self) -> str:
            return str(self)
    
    class MainBlock(ScopeBase):
        pass


class StackLevels:
    class StackLevelBase:
        pass

    class MainLevel(StackLevelBase):
        def __str__(self) -> str:
            return '<main>'

    class FileLevel(StackLevelBase):
        def __init__(self, _f_path:str) -> None:
            self.f_path = _f_path
        def __str__(self) -> str:
            return self.f_path

class VariableScope:
    def __init__(self) -> None:
        self.names = {}

class VariableScopes:
    def __init__(self, set_default:bool=True) -> None:
        self.var_scope_paths:typing.List[VariableScope] = []
        if set_default:
            self.var_scope_paths.append(VariableScope())

    def __len__(self) -> int:
        return len(self.var_scope_paths)
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({(_l:=len(self))} scope{"s" if _l != 1 else ""})'

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
            if not hasattr(_self, 'stack_heap'):
                warnings.warn(f"'{_self}' has no associated 'stack_heap' attribute. This will become an error shortly")
            
            print(r.error_packet.gen_error)
            sys.exit(0)
        return r
    return error_logger
