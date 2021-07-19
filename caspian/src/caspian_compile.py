import typing, caspian_parser, state_objects
import collections, itertools

class CallStack:
    def __init__(self, max_depth = 1000) -> None:
        self.max_depth, self.c_count = max_depth, 0
        self.stack = collections.deque()

class MemHeap:
    def __init__(self) -> None:
        self.ref_count = 0
        self.mem_objects = {}

class CaspianCompile:
    def __init__(self) -> None:
        self.call_stack = CallStack()
        self.heap = MemHeap()

    def __enter__(self) -> 'CaspianCompile':
        return self

    def compile(self, resource:str, f:bool=True) -> None:
        pass
    
    def __exit__(self, *_) -> None:
        pass
    

if __name__ == '__main__':
    pass