import typing

class Ast:
    def __init__(self, **kwargs) -> None:
        self.vals = kwargs

    def __getattr__(self, attr:str) -> typing.Any:
        return self.vals[attr]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.vals})'

class Import(Ast):
    _fields = ['path', 'alias', 'line']

class Body(Ast):
    _fields = ['body']

class Pass(Ast):
    _fields = ['line']

class Fun(Ast):
    _fields = ['name', 'primative', 'settings', 'signature', 'return_type', 'body']

class CommaSeparatedItems(Ast):
    _fields = ['items']

class ParenItems(Ast):
    _fields = ['items']

class BraceItems(Ast):
    _fields = ['items']

class BracketItems(Ast):
    _fields = ['items']

class GetItem(Ast):
    _fields = ['obj', 'signature']
    assign = True
    signature = False
    container = False

class Call(Ast):
    _fields = ['obj', 'signature']
    assign = False
    signature = False
    container = False

class ImmutableContainer(Ast):
    _fields = ['container']
    assign = False
    signature = False
    container = False

class MapUnpack(Ast):
    _fields = ['container']
    assign = False
    signature = True
    container = True

class ArrayUnpack(Ast):
    _fields = ['container']
    assign = False
    signature = True
    container = True

class GetAttr(Ast):
    _fields = ['obj', 'attr']
    assign = True
    signature = False
    container = False

class Expr(Ast):
    assign = False
    signature = False
    container = False

class Operation(Ast):
    _fields = ['operand1', 'operator', 'operand2']
    assign = False
    signature = False
    container = False

class Assign(Ast):
    _fields = ['obj', 'value']
    assign = False
    signature = True
    container = False

class AssignParam(Ast):
    _fields = ['obj', 'value']
    assign = False
    signature = True
    container = False

class KeyValue(Ast):
    _fields = ['key', 'value']
    assign = True
    signature = True
    container = True

class ImpOp(Ast):
    _fields = ['obj', 'operator', 'value']

class InPlace(Ast):
    _fields = ['obj', 'operator']
    assign = False
    signature = False
    container = False

class AsyncAwait(Ast):
    _fields = ['obj']
    assign = False
    signature = False
    container = False

class AsyncFun(Ast):
    _fields = ['fun']

class NotOp(Ast):
    _fields = ['obj']
    assign = False
    signature = False
    container = False

class NegVal(Ast):
    _fields = ['obj']
    assign = False
    signature = False
    container = False

class Primative(Ast):
    _fields = ['name']
    assign = False
    signature = False
    container = False

class Lambda(Ast):
    _fields = ['params', 'body']
    assign = False
    signature = False
    container = False

class AssignExpr(Ast):
    _fields = ['obj', 'value']

class Return(Ast):
    _fields = ['expr']

class Yield(Ast):
    _fields = ['expr']

class YieldFrom(Ast):
    _fields = ['expr']

class RaiseException(Ast):
    _fields = ['exception']

class Conditional(Ast):
    _fields = ['value', 'condition', 'default']

class For(Ast):
    _fields = ['loop_param', 'iter_obj', 'body']

class AsyncFor(Ast):
    _fields = ['for_loop']

class ComprehensionBlock(Ast):
    _fields = ['loop_param', 'iter_obj']
    assign = False
    signature = False
    container = False

class Comprehension(Ast):
    _fields = ['value', 'body', 'condition']
    assign = False
    signature = False
    container = False

class AsyncComprehensionBlock(Ast):
    _fields = ['loop_param', 'iter_obj']
    assign = False
    signature = False
    container = False

class DecoratedCallable(Ast):
    _fields = ['wrappers', 'wrapped']

class Break(Ast):
    _fields = []

class Continue(Ast):
    _fields = []

class WhileLoop(Ast):
    _fields = ['condition', 'body']

class DoWhileLoop(Ast):
    _fields = ['condition', 'body']

class MultiLineLambda(Ast):
    _fields = ['params', 'body']

class IfStatement(Ast):
    _fields = ['condition', 'body', 'elif_statements', 'else_body']

class ElifCondition(Ast):
    _fields = ['condition', 'body']

class CaseStatement(Ast):
    _fields = ['parameter', 'body']

class SwitchCase(Ast):
    _fields = ['parameter', 'cases', 'default']

class Suppress(Ast):
    _fields = ['params', 'body', 'then_params', 'then_body']

class Class(Ast):
    _fields = ['name', 'inherits', 'abstract', 'body']

class Assert(Ast):
    _fields = ['condition']