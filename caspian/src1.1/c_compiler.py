import typing, state_objects, c_objects
import c_ast

class Compiler:
    def __init__(self) -> None:
        self.heap = state_objects.MemHeap()
        self.scopes = state_objects.Scopes()
    

    def compile(self, ast:c_ast.Ast) -> None:
        pass

if __name__ == '__main__':
    pass