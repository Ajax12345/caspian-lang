import typing, caspian_parser, state_objects
import collections, itertools, re, os
import internal_errors, compile_states
import default_objects

class CaspianCompile:
    def __init__(self) -> None:
        self.call_stack = default_objects.o.call_stack
        self.heap = default_objects.o.heap
        self.var_scopes = state_objects.VariableScopes.provide_default(default_objects.o.name_bindings)
        self.lines = None

    def __enter__(self) -> 'CaspianCompile':
        return self

    def compile(self, resource:str, f:bool=True) -> None:
        if f:
            if not os.path.isfile(resource):
                raise internal_errors.InvalidSource(f"'{resource}' is not a file")
            
            self.call_stack.head = state_objects.StackLevels.FileFrame(resource)
            with open(resource) as f:
                resource = f.read()

        with caspian_parser.Parser(self) as p, caspian_parser.ASTGen(self) as astgen:
            lines, _r_obj = p.parse(resource)
            astgen.input_lines = lines
            ast = astgen.create_ast(_r_obj)
            print('resulting ast from compiler', ast)
            self.lines = lines
            _ = compile_states.Compiler.head_compile(self, ast)

    
    def __exit__(self, *_) -> None:
        pass
    

if __name__ == '__main__':
    with CaspianCompile() as c:
        c.compile('testing_file.txt')

