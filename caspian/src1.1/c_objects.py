import typing, object_factory
import state_objects as so

__all__ = ('o',)

o = object_factory.CaspianObjFactory()

@o.primative.Eq
def Eq(this, _, scopes:so.Scopes, comp_obj:'CaspianObj') -> True:
    return scopes['Bool'].instantiate(this.id == comp_obj.id)

@o.primative.toString
def toString(this, _, scopes:so.Scopes) -> True:
    return scopes['String'].instantiate(f"<{this._type} '{this.name}' at {this.id}>")

@o.primative.toString
def toStringName(this, _, scopes:so.Scopes) -> True:
    return this.public['__name__']

@o.primative.Call
def InstantiateClassCall(this, _, scopes:so.Scopes, *args, **kwargs) -> True:
    return this.instantiate(*args, **kwargs)
 
@o.primative.Call
def Call(this, _, scopes:so.Scopes, *args, **kwargs) -> True:
    pass

@o.primative.Bool
def bool_(this, _, scopes:so.Scopes) -> True:
    return scopes['Bool', 'eval':True].instantiate(True)


@o.primative.Bool
def bool__(this, _, scopes:so.Scopes) -> True:
    return scopes['Bool', 'eval':True].instantiate(False)

@o.base_class
def BaseClass() -> True:
    @o.static.primative.toString
    def toString_(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate('<type "BaseClass">')
    
    return toString_,

@o.class_
def Fun() -> True:
    @o.static.primative.toString
    def toString_(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate('<type "Function">')

    return toString_,

@o.class_
def Bool() -> True:
    valid_op_types = [
        'Integer',
        'Bool',
        'Float'
    ]
    @o.fun
    def constructor(this, _, scopes:so.Scopes, _bool:bool) -> False:
        if not isinstance(_bool, (bool, int)):
            raise Exception(f"{_bool} is not a boolean or integer")

        this['_val'] = so.PyBaseObj(_bool)

    @o.primative.Bool
    def Bool(this, _, scopes:so.Scopes) -> False:
        return this._id
    
    @o.primative.toString
    def toString(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate(str(this['_val'].val).lower())

    @o.static.primative.toString
    def toString_(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate('<type "Bool">')

    @o.primative.Eq
    def Eq(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Bool cannot compare type "{c_obj.name}"')
        
        return scopes['Bool', 'eval':True].instantiate(this['_val'].val == c_obj['_val'].val)

    @o.primative.Add
    def Add(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Bool cannot add type "{c_obj.name}"')
        
        return scopes['Integer' if c_obj.name != 'Float' else 'Float', 'eval':True].instantiate(this['_val'].val + c_obj['_val'].val)

    @o.primative.Sub
    def Sub(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Bool cannot subtract type "{c_obj.name}"')
        
        return scopes['Integer' if c_obj.name != 'Float' else 'Float', 'eval':True].instantiate(this['_val'].val - c_obj['_val'].val)

    @o.primative.Mul
    def Mul(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Bool cannot multiply type "{c_obj.name}"')
        
        return scopes['Integer' if c_obj.name != 'Float' else 'Float', 'eval':True].instantiate(this['_val'].val * c_obj['_val'].val)

    @o.primative.Div
    def Div(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Bool cannot multiply type "{c_obj.name}"')
        
        return scopes['Float', 'eval':True].instantiate(this['_val'].val / c_obj['_val'].val)

    return constructor, Bool, toString, toString_, Eq, Add, Sub, Mul, Div

    
@o.class_
def String() -> True:
    @o.fun
    def constructor(this, _, scopes:so.Scopes, _str:str) -> False:
        if not isinstance(_str, str):
            raise Exception(f"{_str} is not a string")

        this['_val'] = so.PyBaseObj(_str)

    @o.primative.Bool
    def Bool(this, _, scopes:so.Scopes) -> False:
        return scopes['Bool', 'eval':True].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, _, scopes:so.Scopes) -> False:
        return this._id

    @o.static.primative.toString
    def toString_(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate('<type "String">')

    @o.primative.Add
    def Add(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if scopes['String'].not_eq(c_obj.public['__type__']):
            raise Exception(f'Cannot concatentate type "{c_obj.name}" to String')

        return scopes['String', 'eval':True].instantiate(this['_val'].val + c_obj['_val'].val)

    @o.primative.Add
    def Mul(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if scopes['Integer'].not_eq(c_obj.public['__type__']):
            raise Exception(f'Cannot extend String by type "{c_obj.name}"')

        return scopes['String', 'eval':True].instantiate(this['_val'].val * c_obj['_val'].val)


    return constructor, toString, toString_, Bool, Add, Mul


@o.class_
def Integer() -> True:
    valid_op_types = [
        'Integer',
        'Bool',
        'Float'
    ]
    @o.fun
    def constructor(this, _, scopes:so.Scopes, _val:int) -> False:
        if not isinstance(_val, int):
            raise Exception(f"{_val} is not an integer")

        this['_val'] = so.PyBaseObj(_val)

    @o.primative.Bool
    def Bool(this, _, scopes:so.Scopes) -> False:
        return scopes['Bool', 'eval':True].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate(str(this['_val']))

    @o.static.primative.toString
    def toString_(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate('<type "Integer">')

    @o.primative.Eq
    def Eq(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Integer cannot compare type "{c_obj.name}"')
        
        return scopes['Bool', 'eval':True].instantiate(this['_val'].val == c_obj['_val'].val)

    @o.primative.Add
    def Add(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Integer cannot add type "{c_obj.name}"')
        
        return scopes['Integer' if c_obj.name != 'Float' else 'Float', 'eval':True].instantiate(this['_val'].val + c_obj['_val'].val)

    @o.primative.Sub
    def Sub(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Integer cannot subtract type "{c_obj.name}"')
        
        return scopes['Integer' if c_obj.name != 'Float' else 'Float', 'eval':True].instantiate(this['_val'].val - c_obj['_val'].val)

    @o.primative.Mul
    def Mul(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Integer cannot multiply type "{c_obj.name}"')
        
        return scopes['Integer' if c_obj.name != 'Float' else 'Float', 'eval':True].instantiate(this['_val'].val * c_obj['_val'].val)

    @o.primative.Div
    def Div(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Integer cannot multiply type "{c_obj.name}"')
        
        return scopes['Float', 'eval':True].instantiate(this['_val'].val / c_obj['_val'].val)

    return constructor, toString, Bool, toString_, Eq, Add, Sub, Mul, Div

@o.class_
def Float() -> True:
    valid_op_types = [
        'Integer',
        'Bool',
        'Float'
    ]
    @o.fun
    def constructor(this, _, scopes:so.Scopes, _val:float) -> False:
        if not isinstance(_val, (float, int)):
            raise Exception(f"{_val} is not a float or an integer")

        this['_val'] = so.PyBaseObj(_val)

    @o.primative.Bool
    def Bool(this, _, scopes:so.Scopes) -> False:
        return scopes['Bool', 'eval':True].instantiate(bool(this['_val'].val))

    @o.primative.toString
    def toString(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate(str(this['_val']))

    @o.static.primative.toString
    def toString_(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate('<type "Float">')

    @o.primative.Eq
    def Eq(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Float cannot compare type "{c_obj.name}"')
        
        return scopes['Bool', 'eval':True].instantiate(this['_val'].val == c_obj['_val'].val)

    @o.primative.Add
    def Add(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Float cannot add type "{c_obj.name}"')
        
        return scopes['Float', 'eval':True].instantiate(this['_val'].val + c_obj['_val'].val)

    @o.primative.Sub
    def Sub(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Float cannot subtract type "{c_obj.name}"')
        
        return scopes['Float', 'eval':True].instantiate(this['_val'].val - c_obj['_val'].val)

    @o.primative.Mul
    def Mul(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Float cannot multiply type "{c_obj.name}"')
        
        return scopes['Float', 'eval':True].instantiate(this['_val'].val * c_obj['_val'].val)

    @o.primative.Div
    def Div(this, _, scopes:so.Scopes, c_obj:'CaspianObjectClassInstance') -> False:
        if not any(c_obj.public['__type__'].eq(scopes[_type]) for _type in valid_op_types):
            raise Exception(f'Float cannot multiply type "{c_obj.name}"')
        
        return scopes['Float', 'eval':True].instantiate(this['_val'].val / c_obj['_val'].val)


    return constructor, toString, Bool, toString_, Eq, Add, Sub, Mul, Div

@o.class_
def Primative() -> True:
    primatives = [
        'getitem', 
        'setitem', 
        'getattr', 
        'setattr', 
        'eq', 
        'ne', 
        'lt', 
        'le', 
        'gt', 
        'ge', 
        'add', 
        'sub', 
        'mul', 
        'div', 
        'iterator', 
        'type_check',
        'and', 
        'or'
    ]
    @o.fun
    def constructor(this, _, scopes:so.Scopes, _type:typing.Union[str, None] = None) -> False:
        if _type not in primatives:
            raise Exception(f"'{_type}' is not a valid primative")
            
        this['_val'] = so.PyBaseObj(_type)

    @o.primative.toString
    def toString(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate("<type Primative>" if this['_val'].val is None else f"primative::{this['_val'].val}")

    return constructor, toString

@o.class_
def null() -> True:
    @o.primative.toString
    def toString(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate("null")
    
    @o.static.primative.Bool
    def Bool(this, _, scopes:so.Scopes) -> False:
        return scopes['Bool', 'eval':True].instantiate(False)

    @o.static.primative.toString
    def toString_(this, _, scopes:so.Scopes) -> False:
        return scopes['String', 'eval':True].instantiate("null")

    return toString, Bool, toString_

if __name__ == '__main__':
    print('-'*10,'testing integers/floats', '-'*10)
    v1 = o.heap[o.scopes['Integer']].instantiate(1)
    print(id(o.scopes['Integer']))
    print(id(o.heap[v1].public['__type__']))
    print(o.heap[v1].name)
    print(o.heap[o.scopes['Integer']])
    v2 = o.heap[o.scopes['Integer']].instantiate(2)
    _v1 = o.heap[o.scopes['Integer']].instantiate(0)
    print(o.heap[o.heap[o.heap[o.heap[_v1].private['Bool']].private['Call']].exec_source['payload']['callable'](o.heap[_v1], None, o.scopes)]['_val'])
    v3 = o.heap[o.scopes['Float']].instantiate(1.4)
    print(o.heap[o.heap[o.heap[o.heap[v1].private['Add']].private['Call']].exec_source['payload']['callable'](o.heap[v1], None, o.scopes, o.heap[v2])]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[v1].private['Add']].private['Call']].exec_source['payload']['callable'](o.heap[v1], None, o.scopes, o.heap[v3])]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[v3].private['Bool']].private['Call']].exec_source['payload']['callable'](o.heap[v3], None, o.scopes)]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[o.scopes['Float']].private['toString']].private['Call']].exec_source['payload']['callable'](o.heap[o.scopes['Float']], None, o.scopes)]['_val'])
    print('-'*10,'testing null', '-'*10)
    v4 = o.scopes['null']
    print(o.heap[o.heap[o.heap[o.heap[o.scopes['null']].private['toString']].private['Call']].exec_source['payload']['callable'](o.heap[o.scopes['null']], None, o.scopes)]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[o.scopes['null']].private['Bool']].private['Call']].exec_source['payload']['callable'](o.heap[o.scopes['null']], None, o.scopes)]['_val'])
    #line should raise an error
    #print(o.heap[o.heap[o.heap[o.heap[v1].private['Div']].private['Call']].exec_source['payload']['callable'](o.heap[v1], None, o.scopes, o.heap[v4])])
    print('-'*10,'testing bool', '-'*10)
    v5 = o.heap[o.scopes['Bool']].instantiate(True)
    v6 = o.heap[o.scopes['Bool']].instantiate(False)
    print(o.heap[o.heap[o.heap[o.heap[o.scopes['Bool']].private['toString']].private['Call']].exec_source['payload']['callable'](o.heap[o.scopes['Bool']], None, o.scopes)]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[v6].private['toString']].private['Call']].exec_source['payload']['callable'](o.heap[v6], None, o.scopes)]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[v5].private['Add']].private['Call']].exec_source['payload']['callable'](o.heap[v5], None, o.scopes, o.heap[v6])]['_val'])
    print('-'*10,'testing string', '-'*10)
    v7 = o.heap[o.scopes['String']].instantiate('James')
    v8 = o.heap[o.scopes['String']].instantiate('Joe')
    v8 = o.heap[o.scopes['String']].instantiate('')
    print(o.heap[o.heap[o.heap[o.heap[v7].private['Add']].private['Call']].exec_source['payload']['callable'](o.heap[v7], None, o.scopes, o.heap[v8])]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[v7].private['Mul']].private['Call']].exec_source['payload']['callable'](o.heap[v7], None, o.scopes, o.heap[v2])]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[v7].private['Bool']].private['Call']].exec_source['payload']['callable'](o.heap[v7], None, o.scopes)]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[v8].private['Bool']].private['Call']].exec_source['payload']['callable'](o.heap[v8], None, o.scopes)]['_val'])
    print(o.heap[o.heap[o.heap[o.heap[o.scopes['String']].private['toString']].private['Call']].exec_source['payload']['callable'](o.heap[o.scopes['String']], None, o.scopes)]['_val'])
    print('-'*10,'testing primatives','-'*10)
    print(o.heap[o.heap[o.heap[v7].private['Add']].private['toString']])
    print(o.heap[o.scopes['Call']].__dict__)
    print('-'*10, 'testing parents', '-'*10)
    print(o.heap[o.scopes['Call']].parents[0].__dict__)
    print(o.heap[o.heap[o.heap[v8].public['__type__']].parents[0]].parents)
    print(o.heap[o.scopes['toString']].parents[0].__dict__)
    print('-'*10, 'testing primative class', '-'*10)
    v9 = o.heap[o.scopes['Primative']].instantiate('getitem')
    print(o.heap[o.heap[o.heap[o.heap[v9].private['toString']].private['Call']].exec_source['payload']['callable'](o.heap[v9], None, o.scopes)]['_val'])
    #print(o.heap[o.heap[o.heap[o.scopes['String']].private['toString']].exec_source['payload']['callable'](o.heap[o.scopes['String']], None, o.scopes)])