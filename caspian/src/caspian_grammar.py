import re, typing, itertools, collections
from caspian_token_objs import *

__all__ = ('Token', 'TokenEOF', 'BlockTokenGroup', 'tokens', 'grammar')

Token = TokenMain.TokenBase()
#TokenEOF = TokenMain.TokenEOF()
BlockTokenGroup  = TokenMain.BlockTokenGroup()

tokens = [
    (Token.Space, re.compile(r'^\s')),
    (Token.Label.rd, re.compile(r'^[a-zA-Z_]{1}(?:[a-zA-Z0-9_]+)*')),
    (Token.String.rd, re.compile(r'^".*?"')),
    (Token.String.rd, re.compile(r"^'.*?'")),
    (Token.String.rd, re.compile(r'^`.*?`')),
    (Token.Float.rd, re.compile(r'^\d+\.\d+')),
    (Token.Integer.rd, re.compile(r'^\d+')),
    (Token.OParen, re.compile(r'^\(')),
    (Token.CParen, re.compile(r'^\)')),
    (Token.OBracket, re.compile(r'^\[')),
    (Token.CBracket, re.compile(r'^\]')),
    (Token.OBrace, re.compile(r'^\{')),
    (Token.CBrace, re.compile(r'^\}')),
    (Token.Slash, re.compile(r'^/')),
    (Token.Plus, re.compile(r'^\+')),
    (Token.Minus, re.compile(r'^\-')),
    (Token.Star, re.compile(r'^\*')),
    (Token.Mod, re.compile(r'^%')),
    (Token.Eq, re.compile(r'^\=')),
    (Token.LArrow, re.compile(r'^\<')),
    (Token.RArrow, re.compile(r'^\>')),
    (Token.Not, re.compile(r'^\!')),
    (Token.And, re.compile(r'^\&')),
    (Token.Or, re.compile(r'^\|')),
    (Token.Comma, re.compile(r'^,')),
    (Token.Colon, re.compile(r'^:')),
    (Token.Dot, re.compile(r'^\.')),
    (Token.Pound, re.compile(r'^#')),
    (Token.At, re.compile(r'^@'))
]

grammar = [
    (Token.Bool.rd,    Token.Label.match('true')
                    |Token.Label.match('false')),
    (Token.As,      Token.Label.match('as')),
    (Token.Null.rd,    Token.Label.match('null')),
    (Token.In, Token.Label.match('in')),
    (Token.Operator, Token.Plus
                    |Token.Minus
                    |Token.Star
                    |Token.Mod
                    |Token.Slash
                    |(Token.Eq&Token.Eq)._('equals')
                    |(Token.LArrow&Token.Eq)._('le')
                    |(Token.RArrow&Token.Eq)._('ge')
                    |Token.LArrow
                    |Token.RArrow
                    |Token.Or
                    |Token.And
                    |(Token.Not&Token.Eq)._('not_equals')
                    |Token.Label.match('and')._('bool_and')
                    |Token.Label.match('or')._('bool_or')
                    |Token.In),
    (Token.Operation, (Token.Expr&Token.Operator&Token.Expr).neg_lookahead(Token.Star|Token.Slash)),
    (Token.NegativeVal.rd, Token.Minus&Token.Expr),
    (Token.Comment,   Token.Slash&Token.Slash),
    (Token.KeyValue, Token.Expr&Token.Colon&Token.Expr),
    (Token.SignatureEq, Token.ValueLabel&Token.Eq&Token.Expr
                    |Token.KeyValue&Token.Eq&Token.Expr),
    (Token.CommaList, (Token.Expr&Token.Comma&Token.Expr
                    |Token.Expr&Token.Comma&Token.CommaList
                    |Token.CommaList&Token.Comma&Token.Expr
                    |Token.CommaList&Token.Comma&Token.CommaList).ml),
    (Token.Array.rd1,   (Token.OBracket&Token.CBracket
                    |Token.OBracket&Token.Expr&Token.CBracket
                    |Token.OBracket&Token.CommaList&Token.CBracket).ml),
    (Token.Map,     (Token.OBrace&Token.CBrace
                    |Token.OBrace&Token.Expr&Token.CBrace
                    |Token.OBrace&Token.CommaList&Token.CBrace).ml),
    (Token.ImmutableContainer.rd, Token.Pound&Token.Array
                    |Token.Pound&Token.Map),
    (Token.ArrayUnpack, Token.Dot&Token.Dot&Token.Expr),
    (Token.MapUnpack, Token.Dot&Token.Dot&Token.Dot&Token.Expr),
    (Token.Primative.rd, Token.Label.match('primative')&Token.Colon&Token.Colon&Token.Label),
    (Token.ChainCall, (Token.Expr&Token.Pipe&Token.RArrow&Token.Expr
                    |Token.Expr&Token.Pipe&Token.RArrow&Token.ChainCall).ml),
    (Token.Getattr, Token.Expr&Token.Dot&Token.Expr),
    (Token.Getitem, Token.Expr&Token.OBracket&Token.CBracket
                    |Token.Expr&Token.OBracket&Token.Expr&Token.CBracket
                    |Token.Expr&Token.OBracket&Token.CommaList&Token.CBracket),
    (Token.If,      Token.Label.match('if')),
    (Token.Elif,    Token.Label.match('elif')),
    (Token.Else,    Token.Label.match('else')),
    (Token.Switch,  Token.Label.match('switch')),
    (Token.Case,    Token.Label.match('case')),
    (Token.Default, Token.Label.match('default')),
    (Token.Suppress,Token.Label.match('suppress')),
    (Token.Then, Token.Label.match('then')),
    (Token.For,     Token.Label.match('for')),
    (Token.While,     Token.Label.match('while')),
    (Token.Do,     Token.Label.match('do')),
    (Token.Yield,   Token.Label.match('yield')),
    (Token.Fun,   Token.Label.match('fun')),
    (Token.Class,   Token.Label.match('class')),
    (Token.Inherits, Token.Label.match('inherits')),
    (Token.Return, Token.Label.match('return')),
    (Token.Abstract,   Token.Label.match('abstract')),
    (Token.Static,   Token.Label.match('static')),
    (Token.YieldFrom,   Token.Yield&Token.Label.match('from')),
    (Token.Async,   Token.Label.match('async')),
    (Token.AsyncFor,  Token.Async&Token.For),
    (Token.Await,   Token.Label.match('await')),
    (Token.ForExpr, (Token.AsyncFor|Token.For)&(Token.Expr|Token.CommaList)&Token.In&Token.Expr),
    (Token.ForBlockInline, Token.ForExpr&Token.ForExpr
                           |Token.ForExpr&Token.ForBlockInline),
    (Token.ParenGroup, Token.OParen&(Token.Expr|Token.CommaList)&Token.CParen),
    (Token.FunSignature, (Token.Expr&Token.ParenGroup)._('fun_call')
                          |(Token.Expr&Token.OParen&Token.CParen)._('fun_call')),
    (Token.ValueLabel.rd1, Token.Label.nonmatch('true', 
                                         'false', 
                                         'null',
                                         'and',
                                         'or',
                                         'in',
                                         'as', 
                                         'if', 
                                         'elif', 
                                         'else', 
                                         'for',
                                         'while', 
                                         'do',
                                         'async', 
                                         'fun',
                                         'class',
                                         'inherits',
                                         'return', 
                                         'abstract',
                                         'static',
                                         'case', 
                                         'switch', 
                                         'yield', 
                                         'await', 
                                         'default', 
                                         'continue', 
                                         'break', 
                                         'raise', 
                                         'import', 
                                         'from', 
                                         'suppress', 
                                         'then')),
    (Token.Expr,    Token.ValueLabel
                    |Token.Operation
                    |Token.Integer
                    |Token.Float
                    |Token.String
                    |Token.NegativeVal
                    |Token.ImmutableContainer
                    |Token.Array
                    |Token.Map
                    |Token.ParenGroup
                    |Token.Primative
                    |Token.FunSignature
                    |Token.ChainCall
                    |Token.Getattr
                    |Token.Getitem
                    |Token.SignatureEq
                    |Token.KeyValue
                    |Token.ArrayUnpack
                    |Token.MapUnpack
                    |(Token.Expr&Token.If&Token.Expr&Token.Else&Token.Expr)._('inline_conditional')
                    |(Token.Await&Token.Expr)._('await')
                    |(Token.OBracket&Token.Expr&(Token.ForExpr|Token.ForBlockInline)&Token.CBracket)._('array_comp').ml
                    |(Token.OBracket&Token.Expr&(Token.ForExpr|Token.ForBlockInline)&Token.IfCond&Token.CBracket)._('array_comp_conditional').ml
                    |(Token.OBrace&Token.KeyValue&(Token.ForExpr|Token.ForBlockInline)&Token.CBrace)._('map_comp').ml
                    |(Token.OBrace&Token.KeyValue&(Token.ForExpr|Token.ForBlockInline)&Token.IfCond&Token.CBrace)._('map_comp_conditional').ml
                    |Token.LambdaFun
                    |Token.LambdaFunMulti),

    (Token.Assign, (Token.ValueLabel
                    |Token.Expr
                    |Token.Array
                    |Token.Map
                    |Token.CommaList
                    |Token.Getattr
                    |Token.Getitem
                    |Token.KeyValue)
                    &Token.Eq
                    &(Token.Expr
                    |Token.CommaList)),
    (Token.Import,  Token.Label.match('import')&Token.Expr
                    |(Token.Import&Token.As&Token.Label)._('import_as')),
    (Token.Stmn,    (Token.Label.match('raise')&Token.Expr.eof)._('raise')
                    |(Token.Label.match('continue').eof)._('continue')
                    |(Token.Label.match('break').eof)._('break')
                    |Token.Import
                    |(Token.Return&Token.Expr)._('return_stmn')),
    (Token.IfCond, Token.If&Token.Expr),
    (Token.ElifCond, Token.Elif&Token.Expr),
    (Token.ElifBlock, (Token.ElifCond&BlockTokenGroup)
                    |(Token.ElifBlock&Token.ElifBlock)),
    (Token.Control, (Token.IfCond&BlockTokenGroup)
                    |(Token.Control&Token.ElifBlock)
                    |(Token.Control&Token.Else&BlockTokenGroup)),
    (Token.CaseBlock, (Token.Case&Token.Expr&BlockTokenGroup)
                    |(Token.CaseBlock&Token.CaseBlock)),
    (Token.SwitchCase, (Token.Switch&Token.Expr&BlockTokenGroup&Token.CaseBlock)
                    |(Token.SwitchCase&Token.Default&BlockTokenGroup)),
    (Token.SuppressBlock, ((Token.Suppress&(Token.Expr|Token.CommaList))._('suppress_params')|Token.Suppress)&BlockTokenGroup
                    |(Token.SuppressBlock&((Token.Then&(Token.Expr|Token.CommaList))._('then_block')|Token.Then)&BlockTokenGroup)),
    (Token.ForLoop, Token.ForExpr&BlockTokenGroup),
    (Token.WhileLoop, (((Token.While&Token.Expr)|Token.While)&BlockTokenGroup)
                    |(Token.Do&BlockTokenGroup&((Token.While&Token.Expr)|Token.While))),
    (Token.FunctionStub, (Token.Fun&Token.FunSignature)
                    |(Token.FunctionStub&Token.Colon&Token.Expr)),
    (Token.FunctionBlock, Token.FunctionStub&BlockTokenGroup),
    (Token.AsyncFunctionBlock, Token.Async&Token.FunctionBlock),
    (Token.AbstractFunctionBlock, Token.Abstract&Token.FunctionBlock),
    (Token.AsyncAbstractFunctionBlock, Token.Abstract&Token.AsyncFunctionBlock),
    (Token.StaticFunctionBlock, Token.Static&Token.FunctionBlock),
    (Token.StaticAsyncFunctionBlock, Token.Static&Token.AsyncFunctionBlock),
    (Token.StaticAbstractFunctionBlock, Token.Static&Token.AbstractFunctionBlock),
    (Token.StaticAsyncAbstractFunctionBlock, Token.Static&Token.AsyncAbstractFunctionBlock),
    (Token.LambdaFun.rd, (Token.ParenGroup&Token.ParenGroup)
                    |(Token.KeyValue&Token.ParenGroup)),
    (Token.LambdaFunMulti.rd, (Token.ParenGroup&BlockTokenGroup)
                    |(Token.KeyValue&BlockTokenGroup)),
    (Token.Decorator, (Token.At&Token.Expr&Token.FunctionBlock)
                    |(Token.At&Token.Expr&Token.AsyncFunctionBlock)
                    |(Token.At&Token.Expr&Token.Decorator)),
    (Token.ClassStub, Token.Class&Token.ValueLabel),
    (Token.ClassInherit, Token.ClassStub&Token.Inherits&(Token.Expr|Token.CommaList)),
    (Token.ClassBlock, (Token.ClassInherit|Token.ClassStub)&BlockTokenGroup),
    
]

def generate_goto() -> dict:
    full_grammar = {a.raw_token_name:b for a, b in grammar}
    def get_token_stream(grammar_op:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> typing.Iterator:
        if hasattr(grammar_op, 'token_groups'):
            for i in grammar_op.token_groups:
                yield from get_token_stream(i)
        else:
            yield grammar_op

    def get_first_root(block:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr'], seen = []) -> typing.Iterator:
        if not hasattr(block, 'token_groups'):
            if block.raw_token_name not in full_grammar:
                yield block
            elif block.raw_token_name not in seen:
                yield from get_first_root(full_grammar[block.raw_token_name], seen=seen+[block.raw_token_name])
        elif isinstance(block, TokenMain.TokenOr):
            for i in block.token_groups:
                yield from get_first_root(i, seen)
        else:
            yield from get_first_root(block.token_groups[0], seen)

    def traverse_parents(block:'TokenRoot', seen = []) -> typing.Iterator:
        yield block
        for a, b in grammar:
            if a.raw_token_name not in seen:
                status = False
                if isinstance(b, TokenMain.TokenGroup):
                    status = isinstance(b.token_groups[-1], TokenMain.TokenRoot) and b.token_groups[-1] == block
                elif isinstance(b, TokenMain.TokenOr):
                    status = any(isinstance(j, TokenMain.TokenRoot) and j == block for j in b.token_groups)
                else:
                    status = b == block
                if status:
                    yield from traverse_parents(a, seen+[a.raw_token_name])

    grammar_trail = {a.raw_token_name:[*traverse_parents(a, [a.raw_token_name])] for a, _ in grammar}

    def _group_block_stream(block:'TokenGroup', parent:'TokenRoot') -> typing.Iterator:
        for i in itertools.product(*[get_token_stream(j) for j in block.token_groups]+[grammar_trail[parent.raw_token_name]]):
            for j in range(0, (l1:=len(i)) - 1):
                #if l1 == 2 or j < l1-2:
                if j+1 < l1 - 1:
                    if i[j+1].raw_token_name not in full_grammar:
                        yield (i[j].raw_token_name, i[j+1].raw_token_name, False)
                    else:
                        for k in get_first_root(i[j+1]):
                            yield (i[j].raw_token_name, k.raw_token_name, False)
                else:
                    yield (i[j].raw_token_name, i[j+1].raw_token_name, True)

    def _generate_goto(grammar_op:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr'], parent_op:typing.Union['TokenRoot', 'TokenGroup', 'TokenOr']) -> typing.Iterator:
        if isinstance(grammar_op, TokenMain.TokenGroup):
            if len(grammar_op.token_groups) > 1:
                yield from _group_block_stream(grammar_op, parent_op)
        elif isinstance(grammar_op, TokenMain.TokenOr):
            for i in grammar_op.token_groups:
                yield from _generate_goto(i, parent_op)
                
    def full_flatten(rr, tr, s, seen = []):
        yield from rr.get(s, [])
        for i in tr.get(s, []):
            if i not in seen:
                yield from full_flatten(rr, tr, i, seen+[i])

    _r_result = collections.defaultdict(set)
    _t_result = collections.defaultdict(set)
    for a, b in grammar:
        for j, k, f in _generate_goto(b, a):
            if not f:
                _r_result[j].add(k)
            elif j != k:
                _t_result[j].add(k)

    _buffer = collections.defaultdict(set)
    
    for a, b in _t_result.items():
        for j in b:
            for k in full_flatten(_r_result, _t_result, j, [j]):
                _buffer[a].add(k)
    
    for a, b in _buffer.items():
        for l in b:
            _r_result[a].add(l)

    for a, b in grammar_trail.items():
        for j in b:
            for k in _r_result[j.raw_token_name]:
                _r_result[a].add(k)

    


    return _r_result
    
    


goto = generate_goto()


if __name__ == '__main__':
    print(goto['Await'])