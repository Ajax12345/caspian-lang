import typing, state_objects

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

    Obj inherits ObjParent:
        public:
            @attr __name__
            @attr __identity___ 
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
    def __init__(self, _heap:typing.Union['MemHeap', None] = None) -> None:
        self.heap = _heap
        self.name_bindings = {}

    @property
    def fun(self) -> typing.Callable:
        class _fun:
            def generator(self, _f:typing.Callable) -> typing.Callable:
                return _f

            def __call__(self, _f:typing.Callable) -> typing.Callable:
                return _f

        return _fun()
        
    @property
    def primative(self) -> typing.Callable:
        class _primative:
            def getitem(self, _f:typing.Callable) -> typing.Callable:

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

    def __call__(self, _heap:'MemHeap') -> 'CaspianObjFactor':
        self.heap = _heap
        return self