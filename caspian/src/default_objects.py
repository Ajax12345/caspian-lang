import typing, object_factory
import state_objects as so

o = object_factory.CaspianObjFactory()

@o.primative.toString
def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> True:
    return scope_vars['String'].instantiate(f"<{this._type} '{this.name}' at {this.id}>")

@o.primative.toString
def toStringName(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> True:
    return this['__name__']


@o.primative.Call
def InstantiateClassCall(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, *args, **kwargs) -> True:
    return this.instantiate(*args, **kwargs)
 
@o.primative.Call
def Call(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, *args, **kwargs) -> True:
    pass

@o.primative.Bool
def bool_(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> True:
    return scope_vars['Bool'].instantiate(True)


@o.primative.Bool
def bool__(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> True:
    return scope_vars['Bool'].instantiate(False)

@o.base_class
def BaseClass() -> True:
    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate('<type "BaseClass">')
    
    return toString_,

@o.class_
def Fun() -> True:
    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate('<type "Function">')

    return toString_,

@o.class_
def Bool() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, _bool:bool) -> False:
        this['_val'] = so.PyBaseObj(_bool)

    @o.primative.Bool
    def Bool(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return this
    
    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate(str(this['_val'].val).lower())

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate('<type "Bool">')

    return constructor, Bool, toString, toString_

    
@o.class_
def String() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, _str:str) -> False:
        this['_val'] = so.PyBaseObj(_str)

    @o.primative.Bool
    def Bool(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['Bool'].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return this

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate('<type "String">')

    return constructor, toString, toString_, Bool


@o.class_
def Integer() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, _val:int) -> False:
        this['_val'] = so.PyBaseObj(_val)

    @o.primative.Bool
    def Bool(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['Bool'].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate(str(this['_val']))

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate('<type "Integer">')

    return constructor, toString, Bool, toString_

@o.class_
def Float() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, _val:float) -> False:
        this['_val'] = so.PyBaseObj(_val)

    @o.primative.Bool
    def Bool(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['Bool'].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate(str(this['_val']))

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate('<type "Float">')

    return constructor, toString, Bool, toString_

@o.class_
def Primative() -> True:
    @o.static.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate("<type Primative>")

    return toString,

@o.class_
def NullType() -> True:
    @o.static.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate("<type NoneType>")

    return toString,


@o.null
def null() -> True:
    pass



if __name__ == '__main__':
    print('-'*20)
    print({type(i).__name__ for i in o.heap.mem_objects.values()})