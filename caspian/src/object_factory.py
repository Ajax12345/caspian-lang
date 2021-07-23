import typing, state_objects as so

class CaspianObj:
    def __init__(self, **kwargs) -> None:
        self.__dict__ = kwargs

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
        self.name_bindings = so.NameBindings()

    def create_fun_Py(self, _f:typing.Callable) -> so.ObjRefId:
        _id = next(self.heap)
        _obj = CaspianObj(
            heap = self.heap, 
            name_bindings = self.name_bindings,
            ref_count = 1,
            _type = 'function',
            name = _f.__name__,
            id = _id.id,
            public = {'__name__':self.name_bindings['String'].instantiate(_f.__name__), 
                    '__type__':self.name_bindings['Fun']
                    '__id__':self.name_bindings['Integer'].instantiate(_id.id)},
            private = {'toString':self.name_bindings['toString']}
        )
        self.heap[_id] = _obj
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
                return self.create_fun_Py(_f)

        return _fun()
        
    @property
    def primative(self) -> typing.Callable:
        class _primative:
            def getitem(self, _f:typing.Callable) -> typing.Callable:
                return _f

            def toString(self, _f:typing.Callable) -> typing.Callable:
                return _f

        return _primative()

    def base_class(self, _f:typing.Callable) -> typing.Callable:
        return _f

    def class_(self, _f:typing.Callable) -> typing.Callable:
        return _f

    def static(self, _f:typing.Callable) -> typing.Callable:
        class _static:
            def generator(self, _f:typing.Callable) -> typing.Callable:
                return _f

            def __call__(self, _f:typing.Callable) -> typing.Callable:
                return _f

        return _static()

    def __call__(self, _heap:so.MemHeap) -> 'CaspianObjFactor':
        self.heap = _heap
        return self