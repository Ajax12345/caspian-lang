import typing, sys, functools
import warnings, internal_errors
import copy, collections, contextlib

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

    class ClassBlock(ScopeBase):
        pass
    
    class FunctionBlock(ScopeBase):
        pass

    class YieldFunctionBlock(ScopeBase):
        pass

class ExecStatus:
    def __init__(self, **kwargs) -> None:
        self._status = kwargs
    
    @property
    def error(self) -> bool:
        return self._status.get('error', False)

    def __getattr__(self, _n:str) -> typing.Any:
        return self._status.get(_n)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(a+" = "+str(b) for a, b in self._status.items())})'

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

    def __getitem__(self, _id:ObjRefId) -> 'CaspianObj':
        return self.mem_objects[_id]

    def __next__(self) -> ObjRefId:
        self.ref_count += 1
        return ObjRefId(self.ref_count)

class ScopeBindings:
    def __init__(self, _id:int, heap:MemHeap) -> None:
        self.scope_id = _id
        self.heap = heap
        self.bindings = {}
        self.binding_parameters = {}

    def __contains__(self, name:str) -> bool:
        return name in self.bindings

    def __getitem__(self, name:str) -> ObjRefId:
        if name not in self:
            return False
    
        return self.bindings[name]

    def __setitem__(self, name:str, obj:ObjRefId) -> None:
        #will need to dereference here
        #possibily increment obj reference
        self.bindings[name] = obj
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}#{self.scope_id}>'

class Scopes:
    def __init__(self, heap:MemHeap) -> None:
        self.scope_count = 0
        self.heap = heap
        self.scopes = {}

    def new_scope(self) -> int:
        self.scope_count += 1
        self.scopes[self.scope_count] = ScopeBindings(self.scope_count, self.heap)
        return self.scope_count

    def __getitem__(self, params:typing.Union[tuple, str]) -> typing.Any:
        if isinstance(params, str):
            return self.scopes[1][params]

        return self.scopes[params[1]][params[0]]

    def __setitem__(self, params:typing.Union[tuple, str], obj:ObjRefId) -> typing.Any:
        if isinstance(params, str):
            self.scopes[1][params] = obj
        
        else:
            self.scopes[params[1]][params[0]] = obj

class PyBaseObj:
    def __init__(self, _val:typing.Any, private=True) -> None:
        self.val, self.private = _val, private

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.val}, private={self.private})'


class NameSelf:
    pass


class ExecSource:
    class Py:
        pass

    class Caspian:
        pass

if __name__ == '__main__':
    n = NameBindings()
    print(n['james'].instantiate(3, 4, 5))