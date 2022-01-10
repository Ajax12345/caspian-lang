import typing, sys, functools
import warnings, copy, operator
import collections, contextlib

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

class ScopeLookupObj:
    def __init__(self, **kwargs:dict) -> None:
        self._params = kwargs

    def __getattr__(self, name:str) -> typing.Any:
        if name in self._params:
            return self._params[name]

    def get(self, param:str, default:typing.Optional = None) -> typing.Any:
        if param in self._params:
            return self._params[param]

        return default

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

class NamePromise:
    def __init__(self, name:str) -> None:
        self.name = name
        self.op_path = []

    def __getattr__(self, name:str) -> 'NamePromise':
        self.op_path.append(lambda obj:getattr(obj, name))
        return self
    
    def __getitem__(self, params:typing.Union[str, tuple]) -> 'NamePromise':
        self.op_path.append(lambda obj:operator.getitem(obj, params))
        return self

    def __call__(self, *args, **kwargs) -> 'NamePromise':
        self.op_path.append(lambda obj:obj(*args, **kwargs))
        return self

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {", ".join("(...)" for _ in self.op_path)}>'

class ScopeBindings:
    def __init__(self, _id:int) -> None:
        self.scope_id = _id
        self.bindings = {}
        self.binding_parameters = {}

    @classmethod
    def lookup_wrapper(cls, params:typing.Union[str, tuple]) -> ScopeLookupObj:
        if isinstance(params, str):
            return ScopeLookupObj(name = params)
        
        d, r = collections.defaultdict(list), {}
        for i in params:
            d[type(i)].append(i)

        if str in d:
            r['name'] = d[str][0]
        
        if slice in d:
            r.update({i.start:i.step for i in r[slice]})

        return ScopeLookupObj(**r)

    def __getitem__(self, params:typing.Union[str, tuple]) -> ObjRefId:
        if (s_params:=self.__class__.lookup_wrapper(params)).name in self.bindings:
            return self.bindings[s_params.name]
        
        if s_params.get('provide_promise', True):
            return NamePromise(s_params.name)

    def __setitem__(self, params:typing.Union[str, tuple], obj:ObjRefId) -> None:
        #will need to dereference here
        #possibily increment obj reference
        self.bindings[(s_params:=self.__class__.lookup_wrapper(params)).name] = obj
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}#{self.scope_id}>'

class Scopes:
    def __init__(self) -> None:
        self.scope_count = 0
        self.scopes = {}

    def new_scope(self) -> int:
        self.scope_count += 1
        self.scopes[self.scope_count] = ScopeBindings(self.scope_count)
        return self.scope_count

    @classmethod
    def lookup_wrapper(cls, params:typing.Union[str, tuple]) -> ScopeLookupObj:
        if isinstance(params, str):
            return ScopeLookupObj(name = params)

        d, r = collections.defaultdict(list), {}
        for i in params:
            d[type(i)].append(i)
        
        if str in d:
            r['name'] = d[str][0]

        if int in d:
            r['scope'] = d[int][0]

        if slice in d:
            r.update({i.start:i.step for i in r[slice]})
        
        return ScopeLookupObj(**r)
        

    def __getitem__(self, params:typing.Union[tuple, str]) -> typing.Any:
        return self.scopes[(s_params:=self.__class__.lookup_wrapper(params)).get('scope', 1)][s_params.name]

    def __setitem__(self, params:typing.Union[tuple, str], obj:ObjRefId) -> typing.Any:
        self.scopes[(s_params:=self.__class__.lookup_wrapper(params)).get('scope', 1)][s_params.name] = obj

class Scope:
    def __init__(self, scopes:Scopes, default_scope:typing.Optional=None) -> None:
        self.scopes = scopes
        self.scope_path = [self.scopes.new_scope()] if default_scope is None else default_scope
    
    def new_scope(self) -> 'Scope':
        return self.__class__(self.scopes, self.scope_path+[self.scopes.new_scope()])

    def __repr__(self) -> str:
        return f'<scope {" -> ".join(map(str, self.scope_path[::-1]))}>'

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
    scopes = Scopes()
    scope = Scope(scopes)
    print(scopes['Call'].instantiate())
