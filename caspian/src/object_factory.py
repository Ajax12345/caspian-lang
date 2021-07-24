import typing, state_objects as so
import internal_errors

class CaspianObj:
    def __init__(self, **kwargs) -> None:
        self.__dict__ = kwargs


class CaspianObjCall(CaspianObj):
    def __call__(self, _source_f:typing.Callable) -> 'CaspianObjCall':
        self.exec_source = {'type':so.ExecSource.Py(), 'payload':{'callable':_source_f}}
        return self

class _primative:
    def __init__(self, _factory:'CaspianObjFactor', _type:typing.Union[str, None]=None) -> None:
        self.factory = _factory
        self._type = _type

    def getitem(self, _f:typing.Callable) -> typing.Callable:
        return _f

    def toString(self, _f:typing.Callable) -> typing.Callable:
        return self.factory.create_primative_Py(_f, name='toString', _type=self._type)

    def Call(self, _f:typing.Callable) -> typing.Callable:
        return self.factory.create_primative_Call_Py(_f, name='Call', _type=self._type)

    def Bool(self, _f:typing.Callable) -> typing.Callable:
        return self.factory.create_primative_Py(_f, name='Bool', _type=self._type)

class CaspianObjFactor:
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
    def __init__(self, _heap:typing.Union[so.MemHeap, None] = None) -> None:
        self.heap = _heap if _heap is not None else so.MemHeap()
        self.name_bindings = so.NameBindings(self.heap)

    def create_fun_Py(self, _f:typing.Callable, name:typing.Union[str, None]=None, _type:typing.Union[str, None]=None) -> so.ObjRefId:
        _id = next(self.heap)
        _obj = CaspianObj(
            heap = self.heap, 
            name_bindings = self.name_bindings,
            ref_count = 1,
            _type = f'{"" if _type is None else _type+" "}function',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.name_bindings['String', True].instantiate(_f.__name__), 
                    '__type__':self.name_bindings['Fun']
                    '__id__':self.name_bindings['Integer', True].instantiate(_id.id)},
            private = {'toString':self.name_bindings['toString'],
                        'Bool':self.name_bindings['Bool'],
                        'Call':self.name_bindings['Call'](_f)}
        )
        self.heap[_id] = _obj
        if _f.__annotations__['return']:
            self.name_bindings[_f.__name__] = _id

        return _id

    def create_primative_Py(self, _f:typing.Callable, name:typing.Union[str, None]=None, _type:typing.Union[str, None]=None) -> so.ObjRefId:
        if name is None:
            raise internal_errors.InvalidPrimativeName(f"primative name cannot be 'None'")
        
        _id = next(self.heap)
        _obj = CaspianObj(
            heap = self.heap, 
            name_bindings = self.name_bindings,
            ref_count = 1,
            _type = f'{"" if _type is None else _type+" "}primative::{name}',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.name_bindings['String', True].instantiate(name), 
                    '__type__':self.name_bindings['Primative']
                    '__id__':self.name_bindings['Integer', True].instantiate(_id.id)},
            private = {'toString':self.name_bindings['toString'],
                        'Bool':self.name_bindings['Bool'],
                        'Call':self.name_bindings['Call'](_f)}
        )
        self.heap[_id] = _obj
        if _f.__annotations__['return']:
            self.name_bindings[_f.__name__] = _id

        return _id

    def create_primative_Call_Py(self, _f:typing.Callable, name:typing.Union[str, None]=None, _type:typing.Union[str, None]=None) -> so.ObjRefId:
        if name is None:
            raise internal_errors.InvalidPrimativeName(f"primative name cannot be 'None'")
        
        _id = next(self.heap)
        _obj = CaspianObjCall(
            heap = self.heap, 
            name_bindings = self.name_bindings,
            ref_count = 1,
            _type = f'{"" if _type is None else _type+" "}primative::{name}',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.name_bindings['String', True].instantiate(name), 
                    '__type__':self.name_bindings['Primative']
                    '__id__':self.name_bindings['Integer', True].instantiate(_id.id)},
            private = {'toString':self.name_bindings['toString'],
                        'Bool':self.name_bindings['Bool'],
                        'Call':so.NameSelf}
        )
        self.heap[_id] = _obj(_f)
        if _f.__annotations__['return']:
            self.name_bindings[_f.__name__] = _id

        return _id

    def create_null_Py(self, _f:typing.Callable) -> so.ObjRefId:
        _id = next(self.heap)
        _obj = Caspian(
            heap = self.heap, 
            name_bindings = self.name_bindings,
            ref_count = 1,
            _type = 'null',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.name_bindings['String', True].instantiate('null'), 
                    '__type__':self.name_bindings['NullType']
                    '__id__':self.name_bindings['Integer', True].instantiate(_id.id)},
            private = {'toString':self.name_bindings['toString'],
                        'Bool':self.name_bindings['Bool_']}
        )
        self.heap[_id] = _obj(_f)
        if _f.__annotations__['return']:
            self.name_bindings[_f.__name__] = _id

        return _id


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

    def class_(self, _f:typing.Callable) -> typing.Callable:
        return _f

    def static(self, _f:typing.Callable) -> typing.Callable:
        _self = self
        class _static:
            def generator(self, _f:typing.Callable) -> typing.Callable:
                return _f

            def primative(self, _f:typing.Callable) -> typing.Callable:
                return _primative(_self, 'static')

            def __call__(self, _f:typing.Callable) -> typing.Callable:
                return _self.create_fun_Py(_f, _type='static')

        return _static()

    def null(self, _f:typing.Callable) -> typing.Callable:
        return self.create_null_Py(_f)

    def __call__(self, _heap:so.MemHeap) -> 'CaspianObjFactor':
        self.heap = _heap
        return self