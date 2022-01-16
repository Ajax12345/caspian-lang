import typing, object_factory
import state_objects as so

__all__ = ('o',)

o = object_factory.CaspianObjFactory()

@o.primative.Eq
def Eq(this, stack_heap:'CaspianCompile', scopes:so.Scopes, comp_obj:'CaspianObj') -> True:
    return scopes['Bool'].instantiate(this.id == comp_obj.id)

@o.primative.toString
def toString(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> True:
    return scopes['String'].instantiate(f"<{this._type} '{this.name}' at {this.id}>")

@o.primative.toString
def toStringName(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> True:
    return this.public['__name__']

@o.primative.Call
def InstantiateClassCall(this, stack_heap:'CaspianCompile', scopes:so.Scopes, *args, **kwargs) -> True:
    return this.instantiate(*args, **kwargs)
 
@o.primative.Call
def Call(this, stack_heap:'CaspianCompile', scopes:so.Scopes, *args, **kwargs) -> True:
    pass

@o.primative.Bool
def bool_(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> True:
    return scopes['Bool'].instantiate(True)


@o.primative.Bool
def bool__(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> True:
    return scopes['Bool'].instantiate(False)

@o.base_class
def BaseClass() -> True:
    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate('<type "BaseClass">')
    
    return toString_,

@o.class_
def Fun() -> True:
    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate('<type "Function">')

    return toString_,

@o.class_
def Bool() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scopes:so.Scopes, _bool:bool) -> False:
        this['_val'] = so.PyBaseObj(_bool)

    @o.primative.Bool
    def Bool(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return this
    
    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate(str(this['_val'].val).lower())

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate('<type "Bool">')

    return constructor, Bool, toString, toString_

    
@o.class_
def String() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scopes:so.Scopes, _str:str) -> False:
        this['_val'] = so.PyBaseObj(_str)

    @o.primative.Bool
    def Bool(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['Bool'].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return this

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate('<type "String">')

    return constructor, toString, toString_, Bool


@o.class_
def Integer() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scopes:so.Scopes, _val:int) -> False:
        this['_val'] = so.PyBaseObj(_val)

    @o.primative.Bool
    def Bool(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['Bool'].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate(str(this['_val']))

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate('<type "Integer">')

    @o.primative.Eq
    def Eq(this, _, scopes:so.Scopes, c_Int_obj:'CaspianObjectClassInstance') -> False:
        if this.public['__type__'].not_eq(c_Int_obj.public['__type__']):
            raise Exception(f'Integer cannot compare type "{c_Int_obj.name}"')
        
        return scopes['Bool', 'eval':True].instantiate(this['_val'].val == c_Int_obj['_val'].val)

    @o.primative.Add
    def Add(this, _, scopes:so.Scopes, c_Int_obj:'CaspianObjectClassInstance') -> False:
        if this.public['__type__'].not_eq(c_Int_obj.public['__type__']):
            raise Exception(f'Integer cannot add type "{c_Int_obj.name}"')
        
        return scopes['Integer', 'eval':True].instantiate(this['_val'].val + c_Int_obj['_val'].val)

    @o.primative.Sub
    def Sub(this, _, scopes:so.Scopes, c_Int_obj:'CaspianObjectClassInstance') -> False:
        if this.public['__type__'].not_eq(c_Int_obj.public['__type__']):
            raise Exception(f'Integer cannot subtract type "{c_Int_obj.name}"')
        
        return scopes['Integer', 'eval':True].instantiate(this['_val'].val - c_Int_obj['_val'].val)

    @o.primative.Mul
    def Mul(this, _, scopes:so.Scopes, c_Int_obj:'CaspianObjectClassInstance') -> False:
        if this.public['__type__'].not_eq(c_Int_obj.public['__type__']):
            raise Exception(f'Integer cannot multiply type "{c_Int_obj.name}"')
        
        return scopes['Integer', 'eval':True].instantiate(this['_val'].val * c_Int_obj['_val'].val)

    @o.primative.Div
    def Div(this, _, scopes:so.Scopes, c_Int_obj:'CaspianObjectClassInstance') -> False:
        if this.public['__type__'].not_eq(c_Int_obj.public['__type__']):
            raise Exception(f'Integer cannot multiply type "{c_Int_obj.name}"')
        
        return scopes['Float', 'eval':True].instantiate(this['_val'].val / c_Int_obj['_val'].val)

    return constructor, toString, Bool, toString_, Eq, Add, Sub, Mul, Div

@o.class_
def Float() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scopes:so.Scopes, _val:float) -> False:
        this['_val'] = so.PyBaseObj(_val)

    @o.primative.Bool
    def Bool(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['Bool'].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate(str(this['_val']))

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate('<type "Float">')

    return constructor, toString, Bool, toString_

@o.class_
def Primative() -> True:
    @o.fun
    def constructor(this, stack_heap:'CaspianCompile', scopes:so.Scopes, _type:typing.Union[str, None] = None) -> False:
        this['_val'] = so.PyBaseObj(_type)

    @o.static.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate("<type Primative>" if this['_val'].val is None else f"primative::{this['_val'].val}")

    return constructor, toString

@o.class_
def null() -> True:
    @o.primative.toString
    def toString(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate("null")
    
    @o.primative.Bool
    def bool__(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['Bool'].instantiate(False)

    @o.static.primative.toString
    def toString_(this, stack_heap:'CaspianCompile', scopes:so.Scopes) -> False:
        return scopes['String'].instantiate("<type NullType>")

    return toString, bool__, toString_

if __name__ == '__main__':
    
    v1 = o.heap[o.scopes['Integer']].instantiate(1)
    v2 = o.heap[o.scopes['Integer']].instantiate(2)
    print(o.heap[o.heap[o.heap[o.heap[v1].private['Div']].private['Call']].exec_source['payload']['callable'](o.heap[v1], None, o.scopes, o.heap[v2])])
    