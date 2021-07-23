import typing, object_factory
import state_objects as so

o = object_factory.CaspianObjFactor()

@o.class_
def Fun() -> True:
    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate('<type "function">')

@o.class_
def Bool() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, _bool:bool) -> False:
        this['_val'] = so.PyBaseObj(_bool)

    @o.primative.bool
    def Bool(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return this
    
    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate(str(this['_val'].val).lower())

    
@o.class_
def String() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, _str:str) -> False:
        this['_val'] = so.PyBaseObj(_str)

    @o.primative.bool
    def Bool(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['Bool'].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return this

    return constructor, toString, Bool

if __name__ == '__main__':
    pass