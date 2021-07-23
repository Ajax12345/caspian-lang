import typing, sys, functools
import warnings, internal_errors
import copy, collections

class BlockExits:
    class ExitStatus:
        pass
    
    class Break(ExitStatus):
        pass

    class Continue(ExitStatus):
        pass
    
    class Return(ExitStatus):
        pass
    
    class Yield(ExitStatus):
        pass

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

    class WhileBlock(ScopeBase):
        pass

    class ForBlock(ScopeBase):
        pass
    
    class FunctionBlock(ScopeBase):
        pass

    class YieldFunctionBlock(ScopeBase):
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


class CallStack:
    def __init__(self, max_depth = 1000) -> None:
        self.max_depth, self.c_count = max_depth, 0
        self.head = StackLevels.MainLevel()
        self.stack = collections.deque()

class ObjRefId:
    def __init__(self, _id:int) -> None:
        self.id = _id
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.id})'

class MemHeap:
    def __init__(self) -> None:
        self.ref_count = 0
        self.mem_objects = {}

    def __setitem__(self, _id:ObjRefId, _obj:'CaspianObj') -> None:
        self.mem_objects[_id] = _obj

    def __next__(self) -> ObjRefId:
        self.ref_count += 1
        return ObjRefId(self.ref_count)

class PyBaseObj:
    def __init__(self, _val:typing.Any, private=True) -> None:
        self.val, self.private = _val, private

class NameBindings:
    def __init__(self) -> None:
        self.bindings = {}

    def __getitem__(self, )