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
    pass

class Call(Ast):
    pass

class ImmutableContainer(Ast):
    pass

class MapUnpack(Ast):
    pass

class ArrayUnpack(Ast):
    pass

class GetAttr(Ast):
    pass

class Expr(Ast):
    pass

class Operation(Ast):
    pass

class Assign(Ast):
    pass

class AssignParam(Ast):
    pass

class KeyValue(Ast):
    pass

class ImpOp(Ast):
    pass

class InPlace(Ast):
    pass

class AsyncAwait(Ast):
    pass

class AsyncFun(Ast):
    pass

class NotOp(Ast):
    pass

class NegVal(Ast):
    pass

class Primative(Ast):
    pass

class Lambda(Ast):
    pass

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
    pass

class Comprehension(Ast):
    pass

class AsyncComprehensionBlock(Ast):
    pass

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