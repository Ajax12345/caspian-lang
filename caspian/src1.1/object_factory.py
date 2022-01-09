import typing, state_objects as so
import internal_errors, collections
import re, copy

class CaspianClassBindings:
    def __init__(self, **kwargs) -> None:
        self.__dict__ = kwargs

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'

class CaspianObj:
    def __init__(self, **kwargs) -> None:
        self.__dict__ = kwargs

    def inc_ref(self) -> 'CaspianObj':
        self.ref_count += 1

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name})'

class CaspianObjCall(CaspianObj):
    def __call__(self, _source_f:typing.Callable, new_obj:bool = True) -> 'CaspianObjCall':
        _c = self.__class__()
        _c.__dict__ = {a:b for a, b in self.__dict__.items()}
        _c.exec_source = {'type':so.ExecSource.Py(), 'payload':{'callable':_source_f}}
        _c.ref_count = 1
        if new_obj:
            _id = next(self.heap)
            self.heap[_id] = _c

        return _c
        
class CaspianObjClassInstance(CaspianObj):
    def __setitem__(self, _name:str, _id:typing.Union[so.ObjRefId, so.PyBaseObj]) -> None:
        if isinstance(_id, so.ObjRefId):
            _ = self.heap[_id].inc_ref()
        #print('in an assignment', type(_id))
        self.public[_name] = _id

    def __getitem__(self, _name:str) -> so.ObjRefId:
        if _name not in self.public:
            raise internal_errors.MissingBindingName(f"'{_name}' not found in public bindings of '{self.name}'")
        
        return self.public[_name]

class CaspianObjClass(CaspianObj):
    def instantiate(self, *args, **kwargs) -> so.ObjRefId:
        #print('public bindings in here', self.name)
        _id = next(self.heap)
        self.inc_ref()
        _obj = CaspianObjClassInstance(
            heap = self.heap, 
            scopes = self.scopes,
            ref_count = 1,
            is_primative = False,
            o_type = None,
            _type = 'Class Instance',
            name = self.name,
            id = _id.id,
            public = {'__name__':so.HeapPromise('String').instantiate(self.name), 
                    '__type__':so.ObjRefId(self.id),
                    '__id__':so.HeapPromise('Integer').instantiate(_id.id),
                    **self.bindings.public},
            private = self.bindings.private
        )
        if 'constructor' in self.bindings.public:
            if isinstance((_call:=self.heap[self.bindings.public['constructor']].private['Call']), so.HeapPromise):
                _call = self.scopes[_call]
            else:
                _call = self.heap[_call]
                
            #print('finalized call object', _call.__dict__)
            _call.exec_source['payload']['callable'](_obj, None, self.scopes, *args, **kwargs)
        
        self.heap[_id] = _obj
        return _id

class _primative:
    def __init__(self, _factory:'CaspianObjFactory', _type:typing.Union[str, None]=None) -> None:
        self.factory = _factory
        self._type = _type

    def Getitem(self, _f:typing.Callable) -> typing.Callable:
        return self.factory.create_primative_Py(_f, name='Getitem', _type=self._type)

    def toString(self, _f:typing.Callable) -> typing.Callable:
        return self.factory.create_primative_Py(_f, name='toString', _type=self._type)

    def Eq(self, _f:typing.Callable) -> typing.Callable:
        return self.factory.create_primative_Py(_f, name='Eq', _type=self._type)

    def Call(self, _f:typing.Callable) -> typing.Callable:
        return self.factory.create_primative_Call_Py(_f, name='Call', _type=self._type)

    def Bool(self, _f:typing.Callable) -> typing.Callable:
        return self.factory.create_primative_Py(_f, name='Bool', _type=self._type)

class CaspianObjFactory:
    '''
    caspian object model
    ---------------------
    ObjParent:
        public:
            @attr __name__
        primative
            @method toString
            @method getitem
            @method call //actually creates the instance of Obj
            @method bool

    Obj inherits ObjParent:
        public:
            @attr __type___ 
            @attr __parent_count__
            @attr __id__
        primative:
            @method call //actually creates the instance of Obj
        bindings: //attributes that become bound to an instance of Obj
            public:
                //
            primative:
                //
        states:
            //stores particulars about how the Obj is executed
            on_exec:
                //the actual callable block, either a caspian ast or a Python callable
        @int ref_count //how many pointers to the object
        @list parents //stores the parent base classes

    '''
    def __init__(self, heap:typing.Union[so.MemHeap, None] = None, scopes:typing.Union[so.Scopes, None]) -> None:
        self.heap = heap if heap is not None else so.MemHeap()
        self.scopes = scopes if scopes is not None else so.Scopes(self.heap)
        #self.scopes = so.NameBindings(self.heap)

    def call_clone_handler(self, _f:typing.Callable) -> so.ObjRefId:
        if isinstance((_s_obj:=self.scopes['Call']), so.HeapPromise):
            return _s_obj(_f)

        _id = next(self.heap)
        _new_call = self.heap[self.scopes['Call']](_f, False)
        self.heap[_id] = _new_call
        return _id

    def _(self, _obj:typing.Union[CaspianObj, so.HeapPromise]) -> typing.Union[CaspianObj, so.HeapPromise]:
        if not isinstance(_obj, so.HeapPromise):
            if isinstance(_obj, CaspianObj):
                _obj.inc_ref()
            elif isinstance(_obj, so.ObjRefId):
                self.heap[_obj].inc_ref()
        return _obj

    def create_fun_Py(self, _f:typing.Callable, name:typing.Union[str, None]=None, _type:typing.Union[str, None]=None) -> so.ObjRefId:
        _id = next(self.heap)
        _obj = CaspianObj(
            heap = self.heap, 
            scopes = self.scopes,
            ref_count = 1,
            is_primative = False,
            o_type = _type,
            _type = f'{"" if _type is None else _type+" "}function',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.scopes['String', True].instantiate(_f.__name__), 
                    '__type__':self._(self.scopes['Fun']),
                    '__id__':self.scopes['Integer'].instantiate(_id.id)},
            private = {'toString':self._(self.scopes['toString']),
                        'Eq':self._(self.scopes['Eq']),
                        'Bool':self._(self.scopes['bool_']),
                        'Call':self.call_clone_handler(_f)}
        )
        self.heap[_id] = _obj
        if _f.__annotations__['return']:
            self.scopes[_f.__name__] = _id
        #print('primative object after creation (function)', _obj.__dict__)

        return _id

    def create_primative_Py(self, _f:typing.Callable, name:typing.Union[str, None]=None, _type:typing.Union[str, None]=None) -> so.ObjRefId:
        if name is None:
            raise internal_errors.InvalidPrimativeName(f"primative name cannot be 'None'")
        
        _id = next(self.heap)
        _obj = CaspianObj(
            heap = self.heap, 
            scopes = self.scopes,
            ref_count = 1,
            is_primative = True,
            o_type = _type,
            _type = f'{"" if _type is None else _type+" "}primative::{name}',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.scopes['String'].instantiate(name), 
                    '__type__':self._(self.scopes['Primative']),
                    '__id__':self.scopes['Integer'].instantiate(_id.id)},
            private = {'toString':self._(self.scopes['toString']),
                        'Eq':self._(self.scopes['Eq']),
                        'Bool':self._(self.scopes['bool_']),
                        'Call':self.call_clone_handler(_f)}
        )
        self.heap[_id] = _obj
        if _f.__annotations__['return']:
            self.scopes[_f.__name__] = _id
        #print('primative object after creation (primative)', _obj.__dict__)
        return _id

    def create_primative_Call_Py(self, _f:typing.Callable, name:typing.Union[str, None]=None, _type:typing.Union[str, None]=None) -> so.ObjRefId:
        if name is None:
            raise internal_errors.InvalidPrimativeName(f"primative name cannot be 'None'")
        
        _id = next(self.heap)
        _obj = CaspianObjCall(
            heap = self.heap, 
            scopes = self.scopes,
            is_primative = True,
            o_type = _type,
            ref_count = 1,
            _type = f'{"" if _type is None else _type+" "}primative::{name}',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.scopes['String'].instantiate(name), 
                    '__type__':self._(self.scopes['Primative']),
                    '__id__':self.scopes['Integer'].instantiate(_id.id)},
            private = {'toString':self._(self.scopes['toString']),
                        'Eq':self._(self.scopes['Eq']),
                        'Bool':self._(self.scopes['bool_']),
                        'Call':so.NameSelf}
        )
        self.heap[_id] = _obj(_f)
        if _f.__annotations__['return']:
            self.scopes[_f.__name__] = _id
        #print('primative object after creation (call)', _obj.__dict__)
        return _id

    def create_null_Py(self, _f:typing.Callable) -> so.ObjRefId:
        raise internal_errors.DepreciatedMethod('null method no longer supported')
        _id = next(self.heap)
        _obj = CaspianObj(
            heap = self.heap, 
            scopes = self.scopes,
            ref_count = 1,
            is_primative = False,
            o_type = None,
            _type = 'null',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.scopes['String'].instantiate('null'), 
                    '__type__':self._(self.scopes['NullType']),
                    '__id__':self.scopes['Integer'].instantiate(_id.id)},
            private = {'toString':self._(self.scopes['toStringName']),
                        'Eq':self._(self.scopes['Eq']),
                        'Bool':self._(self.scopes['bool__'])}
        )
        self.heap[_id] = _obj
        if _f.__annotations__['return']:
            self.scopes[_f.__name__] = _id
        #print('primative object after creation (null)', _obj.__dict__)
        return _id
    
    def create_base_class_Py(self, _f:typing.Callable) -> so.ObjRefId:
        _id = next(self.heap)
        _obj = CaspianObjClass(
            heap = self.heap, 
            scopes = self.scopes,
            ref_count = 1,
            is_primative = False,
            o_type = None,
            _type = 'BaseClass',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.scopes['String'].instantiate('BaseClass'), 
                    '__type__':so.NameSelf,
                    '__id__':self.scopes['Integer'].instantiate(_id.id)},
            private = {'toString':_f()[0],
                        'Eq':self._(self.scopes['Eq']),
                        'Bool':self._(self.scopes['bool_']),
                        'Call':self._(self.scopes['InstantiateClassCall'])},
            bindings = CaspianClassBindings(
                public = {

                },
                private={'toString':self._(self.scopes['toString']),
                        'Eq':self._(self.scopes['Eq']),
                        'Bool':self._(self.scopes['bool_'])}
            )
        )
        self.heap[_id] = _obj
        if _f.__annotations__['return']:
            self.scopes[_f.__name__] = _id
        #print('primative object after creation (base class)', _obj.__dict__)
        return _id

    def create_class_Py(self, _f:typing.Callable) -> so.ObjRefId:
        attr_bindings = collections.defaultdict(dict)
        for i in _f():
            if (_obj:=self.heap[i]).is_primative in attr_bindings[_obj.o_type == 'static']:
                attr_bindings[_obj.o_type == 'static'][_obj.is_primative].append((_obj, i))
            else:
                attr_bindings[_obj.o_type == 'static'][_obj.is_primative] = [(_obj, i)]
        
        _id = next(self.heap)
        _obj = CaspianObjClass(
            heap = self.heap, 
            scopes = self.scopes,
            ref_count = 1,
            is_primative = False,
            o_type = 'Class',
            _type = 'Class',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.scopes['String'].instantiate('BaseClass'), 
                    '__type__':self._(self.scopes['BaseClass']),
                    '__id__':self.scopes['Integer'].instantiate(_id.id),
                    **{o.name:i for o, i in attr_bindings.get(1, {}).get(0, [])}},
            private = {'toString':self._(self.scopes['toString']),
                        'Eq':self._(self.scopes['Eq']),
                        'Bool':self._(self.scopes['bool_']),
                        'Call':self._(self.scopes['InstantiateClassCall']),
                        **{self.create_primative_name(o.name):i for o, i in attr_bindings.get(1, {}).get(1, [])}},
            bindings = CaspianClassBindings(
                public = {o.name:i for o, i in attr_bindings.get(0, {}).get(0, [])},
                private={'toString':self._(self.scopes['toString']),
                        'Eq':self._(self.scopes['Eq']),
                        'Bool':self._(self.scopes['bool_']),
                        **{self.create_primative_name(o.name):i for o, i in attr_bindings.get(0, {}).get(1, [])}}
            )
        )
        self.heap[_id] = _obj
        if _f.__annotations__['return']:
            self.scopes[_f.__name__] = _id

        return _id

    def create_primative_name(self, _name:str) -> str:
        return re.sub('_+$', '', _name)

    @property
    def fun(self) -> typing.Callable:
        _self = self
        class _fun:
            def generator(self, _f:typing.Callable) -> typing.Callable:
                return _f

            def __call__(self, _f:typing.Callable) -> typing.Callable:
                return _self.create_fun_Py(_f)

        return _fun()
        
    @property
    def primative(self) -> typing.Callable:
        return _primative(self)

    def base_class(self, _f:typing.Callable) -> typing.Callable:
        return self.create_base_class_Py(_f)

    def class_(self, _f:typing.Callable) -> typing.Callable:
        return self.create_class_Py(_f)

    @property
    def static(self) -> typing.Callable:
        _self = self
        class _static:
            def generator(self, _f:typing.Callable) -> typing.Callable:
                return _f

            @property
            def primative(self) -> typing.Callable:
                return _primative(_self, 'static')

            def __call__(self, _f:typing.Callable) -> typing.Callable:
                return _self.create_fun_Py(_f, _type='static')

        return _static()

    def null(self, _f:typing.Callable) -> typing.Callable:
        raise internal_errors.DepreciatedMethod('null method no longer supported')
        return self.create_null_Py(_f)

    def __call__(self, stack_heap:'CaspianCompile') -> 'CaspianObjFactory':
        self.heap = stack_heap.heap
        return self