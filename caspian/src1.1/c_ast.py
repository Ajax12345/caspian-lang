import typing

class Ast:
    def __init__(self, **kwargs) -> None:
        self.vals = kwargs

    def __getattr__(self, attr:str) -> typing.Any:
        return self.vals[attr]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.vals})'

class Import(Ast):
    pass

class Body(Ast):
    pass

class Pass(Ast):
    pass

class Fun(Ast):
    pass

class CommaSeparatedItems(Ast):
    pass

class ParenItems(Ast):
    pass

class BraceItems(Ast):
    pass

class BracketItems(Ast):
    pass

class GetItem(Ast):
    assign = True
    signature = False
    container = False

class Call(Ast):
    assign = False
    signature = False
    container = False

class ImmutableContainer(Ast):
    assign = False
    signature = False
    container = False

class MapUnpack(Ast):
    assign = False
    signature = True
    container = True

class ArrayUnpack(Ast):
    assign = False
    signature = True
    container = True

class GetAttr(Ast):
    assign = True
    signature = False
    container = False

class Expr(Ast):
    assign = False
    signature = False
    container = False

class Operation(Ast):
    assign = False
    signature = False
    container = False

class Assign(Ast):
    assign = False
    signature = True
    container = False

class AssignParam(Ast):
    assign = False
    signature = True
    container = False

class KeyValue(Ast):
    assign = True
    signature = True
    container = True

class ImpOp(Ast):
    pass

class InPlace(Ast):
    assign = False
    signature = False
    container = False

class AsyncAwait(Ast):
    assign = False
    signature = False
    container = False

class AsyncFun(Ast):
    pass

class NotOp(Ast):
    assign = False
    signature = False
    container = False

class NegVal(Ast):
    assign = False
    signature = False
    container = False

class Primative(Ast):
    assign = False
    signature = False
    container = False

class Lambda(Ast):
    assign = False
    signature = False
    container = False

class AssignExpr(Ast):
    pass

class Return(Ast):
    pass

class Yield(Ast):
    pass

class YieldFrom(Ast):
    pass

class RaiseException(Ast):
    pass

class Conditional(Ast):
    pass

class For(Ast):
    pass

class AsyncFor(Ast):
    pass

class ComprehensionBlock(Ast):
    assign = False
    signature = False
    container = False

class Comprehension(Ast):
    assign = False
    signature = False
    container = False

class AsyncComprehensionBlock(Ast):
    assign = False
    signature = False
    container = False

class DecoratedCallable(Ast):
    pass

class Break(Ast):
    pass

class Continue(Ast):
    pass

class WhileLoop(Ast):
    pass

class DoWhileLoop(Ast):
    pass

class MultiLineLambda(Ast):
    pass

class IfStatement(Ast):
    pass

class ElifCondition(Ast):
    pass

class CaseStatement(Ast):
    pass

class SwitchCase(Ast):
    pass

class Suppress(Ast):
    pass

class Class(Ast):
    pass