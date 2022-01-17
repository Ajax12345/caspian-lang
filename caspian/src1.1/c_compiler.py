import typing, state_objects, c_objects
import c_ast, c_parser



class Compiler:
    def __init__(self, o:'CaspianObjFactory' = None) -> None:
        self.o_mem_main = o


    def __enter__(self) -> 'Compiler':
        if self.o_mem_main is None:
            self.o_mem_main = c_objects.o

        return self

    def __exit__(self, *_) -> None:
        pass   

    def shadow_param_assign(self, ast:c_ast.Ast, context:typing.Optional[typing.Union[0, 1]]=0) -> typing.Any:
        pass

    def exec_Assign(self, ast:c_ast.Assign, scope_path:state_objects.Scope, scope:state_objects.BodyScopes) -> None:
        print(ast)

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
