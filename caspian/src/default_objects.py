import typing, object_factory
import state_objects as so

__all__ = ('o',)

o = object_factory.CaspianObjFactory()

@o.primative.Eq
def Eq(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, comp_obj:'CaspianObj') -> True:
    return scope_vars['Bool'].instantiate(this.id == comp_obj.id)

@o.primative.toString
def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> True:
    return scope_vars['String'].instantiate(f"<{this._type} '{this.name}' at {this.id}>")

@o.primative.toString
def toStringName(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> True:
    return this.public['__name__']

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
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes, _type:typing.Union[str, None] = None) -> False:
        this['_val'] = so.PyBaseObj(_type)

    @o.static.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate("<type Primative>" if this['_val'].val is None else f"primative::{this['_val'].val}")

    return constructor, toString

@o.class_
def null() -> True:
    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate("null")
    
    @o.primative.Bool
    def bool__(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['Bool'].instantiate(False)

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scope_vars:so.VariableScopes) -> False:
        return scope_vars['String'].instantiate("<type NullType>")

    return toString, bool__, toString_

if __name__ == '__main__':
    print('-'*20)
    #print('result in here!!!', o.heap[o.heap[o.heap[null].instantiate()].private['Bool']].__dict__)
    print(Eq)
