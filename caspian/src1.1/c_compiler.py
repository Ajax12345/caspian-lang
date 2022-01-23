import typing, state_objects, c_objects
import c_ast, c_parser, collections

__set_shadow_roots__ = True

class IteratorArrayBindingMapper:
    def __init__(self, bindings:list) -> None:
        self.bindings = bindings
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.bindings})'

class IteratorMapBindingMapper:
    def __init__(self, bindings:list) -> None:
        self.bindings = bindings
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.bindings})'

if __set_shadow_roots__:
    shadow_assign_asts = collections.defaultdict(list)
    for i in dir(c_ast):
        if i[0].isupper() and i != 'Ast':
            if not getattr((o:=getattr(c_ast, i)), 'assign', True):
                shadow_assign_asts[0].append(o.__name__)
            
            if not getattr(o, 'signature', True):
                shadow_assign_asts[1].append(o.__name__)
            
            if not getattr(o, 'container', True):
                shadow_assign_asts[2].append(o.__name__)
            

class Compiler:
    def __init__(self, o:'CaspianObjFactory' = None) -> None:
        self.o_mem_main = o


    def __enter__(self) -> 'Compiler':
        if self.o_mem_main is None:
            self.o_mem_main = c_objects.o

        return self

    def __exit__(self, *_) -> None:
        pass   

    def shadow_param_assign(self, ast:c_ast.Ast, context:int=0) -> typing.Any:
        if ast.__class__.__name__ in shadow_assign_asts[context]:
            raise Exception(f'Cannot assign to "{ast.__class__.__name__}"')

        if isinstance(ast, c_ast.BraceItems) and isinstance(ast.items, c_ast.CommaSeparatedItems):
            return IteratorArrayBindingMapper([self.shadow_param_assign(i, 2) for i in ast.items.items])
        
        if isinstance(ast, c_ast.BracketItems) and isinstance(ast.items, c_ast.CommaSeparatedItems):
            return IteratorMapBindingMapper([self.shadow_param_assign(i, 2) for i in ast.items.items])
        
        if isinstance(ast, c_ast.KeyValue):
            return c_ast.KeyValue(key=ast.key, value=self.shadow_param_assign(ast.value, 0))

        return ast


    def exec_Assign(self, ast:c_ast.Assign, scope_path:state_objects.Scope, scope:state_objects.BodyScopes) -> None:
        shadow_param = self.shadow_param_assign(ast.obj)
        print('shadow param', shadow_param)
        

    def exec_Body(self, ast:c_ast.Body, scope_path:state_objects.Scope, scope:state_objects.BodyScopes) -> None:
        for block in ast.body:
            if not hasattr(self, p:=f'exec_{block.__class__.__name__}'):
                raise Exception(f'c_ast.{block.__class__.__name__} not supported yet')
            
            getattr(self, p)(block, scope_path, scope)

    def compile(self, ast:c_ast.Ast) -> None:
        if not isinstance(ast, c_ast.Body):
            raise Exception('compiler main expects c_ast.Body')
        
        self.exec_Body(ast, self.o_mem_main.scope, state_objects.BodyScopes.Main)


if __name__ == '__main__':
    
    with open('test_file.txt') as f, Compiler() as compiler:
        p = c_parser.Parser(c_parser.Tokenizer(f.read()))
        body = p.body()
        #print(body)
        compiler.compile(body)
    
