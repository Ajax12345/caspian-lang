import re, typing
from caspian_token_objs import *

__all__ = ('Token', 'tokens', 'grammar')

Token = TokenMain.TokenBase()
TokenEOF = TokenMain.TokenEOF()
BlockTokenGroup  = TokenMain.BlockTokenGroup()

tokens = [
    (Token.Space, r'^\s+'),
    (Token.Label, r'^[a-zA-Z_]{1}(?:[a-zA-Z0-9_])+'),
    (Token.String, r'^".*?"'),
    (Token.String, r"^'.*?'"),
    (Token.String, r'^`.*?`'),
    (Token.Float, r'^\d+\.\d+'),
    (Token.Integer, r'^\d+'),
    (Token.OParen, r'^\('),
    (Token.CParen, r'^\)'),
    (Token.OBracket, r'^\['),
    (Token.CBracket, r'^\]'),
    (Token.OBrace, r'^\{'),
    (Token.CBrace, r'^\}'),
    (Token.Slash, r'^/'),
    (Token.Plus, r'^\+'),
    (Token.Minus, r'^\-'),
    (Token.Star, r'^\*'),
    (Token.Mod, r'^%'),
    (Token.Eq, r'^\='),
    (Token.LArrow, r'^\<'),
    (Token.RArrow, r'^\>'),
    (Token.Not, r'^\!'),
    (Token.And, r'^\&'),
    (Token.Or, r'^\|'),
    (Token.Comma, r'^,'),
    (Token.Colon, r'^:'),
    (Token.Dot, r'^\.'),
    (Token.Pound, r'^#'),
    (Token.At, r'^@')
]

grammar = [
    (Token.Bool,    Token.Label.match('true')
                    |Token.Label.match('false')),
    (Token.As,      Token.Label.match('as')),
    (Token.Null,    Token.Label.match('null')),
    (Token.In, Token.Label.match('in')),
    (Token.Operator, Token.Plus
                    |Token.Minus
                    |Token.Star
                    |Token.Mod
                    |Token.Slash
                    |(Token.Eq&Token.Eq)._('equals')
                    |Token.LArrow
                    |Token.RArrow
                    |Token.Or
                    |Token.And
                    |(Token.Not&Token.Eq)._('not_equals')
                    |Token.Label.match('and')._('bool_and')
                    |Token.Label.match('or')._('bool_or')
                    |Token.In),
    (Token.Operation, (Token.Expr&Token.Operator&Token.Expr).neg_lookahead(Token.Star&Token.Slash)),
    (Token.NegativeVal, Token.Minus&Token.Expr),
    (Token.Comment,   Token.Slash&Token.Slash),
    (Token.KeyValue, Token.Expr&Token.Colon&Token.Expr),
    (Token.SignatureEq, Token.Label&Token.Eq&Token.Expr
                        |Token.KeyValue&Token.Eq&Token.Expr),
    (Token.CommaList, (Token.Expr
                      |Token.Expr&Token.Comma&Token.CommaList
                      |Token.KeyValue
                      |Token.SignatureEq
                      |Token.ArrayUnpack
                      |Token.MapUnpack
                      |Token.CommaList&Token.Comma&Token.CommaList).ml),
    (Token.Array,   (Token.OBracket&Token.CBracket
                      |Token.OBracket&Token.CommaList&Token.CBracket).ml),
    (Token.Map,     (Token.OBrace&Token.CBrace
                      |Token.OBrace&Token.CommaList&Token.CBrace).ml),
    (Token.ImmutableContainer, Token.Pound&Token.Array
                               |Token.Pound&Token.Map),
    (Token.ArrayUnpack, Token.Dot&Token.Dot&Token.Expr),
    (Token.MapUnpack, Token.Dot&Token.Dot&Token.Dot&Token.Expr),
    (Token.Primative, Token.Label.match('primative')&Token.Colon&Token.Colon&Token.Label),
    (Token.ChainCall, (Token.Expr&Token.Pipe&Token.RArrow&Token.Expr
                      |Token.Expr&Token.Pipe&Token.RArrow&Token.ChainCall).ml),
    (Token.Getattr, Token.Expr&Token.Dot&Token.Expr),
    (Token.Getitem, Token.Expr&Token.OBracket&Token.CommaList&Token.CBracket),
    (Token.If,      Token.Label.match('if')),
    (Token.Elif,    Token.Label.match('elif')),
    (Token.Else,    Token.Label.match('else')),
    (Token.For,     Token.Label.match('for')),
    (Token.Yield,   Token.Label.match('yield')),
    (Token.YieldFrom,   Token.Yield&Token.Label.match('from')),
    (Token.Async,   Token.Label.match('async')),
    (Token.AsyncFor,  Token.Async&Token.For),
    (Token.Await,   Token.Label.match('await')),
    (Token.ForExpr, (Token.For|Token.AsyncFor)&Token.CommaList&Token.In&Token.Expr),
    (Token.ForBlockInline, Token.ForExpr&Token.ForExpr
                           |Token.ForExpr&Token.ForBlockInline),
    (Token.Expr,    Token.Label
                    |Token.Operation
                    |Token.Integer
                    |Token.Float
                    |Token.String
                    |Token.NegativeVal
                    |Token.ImmutableContainer
                    |Token.Array
                    |Token.Map
                    |(Token.OParen&Token.Expr&Token.CParen)._('paren_group')
                    |Token.Primative
                    |(Token.Expr&Token.OParen&Token.CParen)._('f_call')
                    |(Token.Expr&Token.OParen&Token.CommaList&Token.CParen)._('f_call')
                    |Token.ChainCall
                    |Token.Getattr
                    |Token.Getitem
                    |(Token.Expr&Token.If&Token.Expr&Token.Else&Token.Expr)._('inline_conditional')
                    |(Token.Await&Token.Expr)._('await')
                    |(Token.OBracket&Token.Expr&(Token.ForExpr|Token.ForBlockInline)&Token.CBracket)._('array_comp')
                    |(Token.OBracket&Token.Expr&(Token.ForExpr|Token.ForBlockInline)&Token.IfCond&Token.CBracket)._('array_comp_conditional')
                    |(Token.OBrace&Token.KeyValue&(Token.ForExpr|Token.ForBlockInline)&Token.CBrace)._('map_comp')
                    |(Token.OBrace&Token.KeyValue&(Token.ForExpr|Token.ForBlockInline)&Token.IfCond&Token.CBrace)._('map_comp_conditional')
                    ),

    (Token.Assign, (Token.Label
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
    (Token.Stmn,    (Token.Label.match('raise')&Token.Expr&TokenEOF)._('raise')
                    |(Token.Label.match('continue')&TokenEOF)._('continue')
                    |(Token.Label.match('break')&TokenEOF)._('break')
                    |Token.Import),
    (Token.IfCond, Token.If&Token.Expr),
    (Token.ElifCond, Token.Elif&Token.Expr),
    (Token.ElifBlock, Token.ElifCond&BlockTokenGroup(indent=True)
                      |Token.ElifBlock&Token.ElifBlock),
    (Token.Control, Token.IfCond&BlockTokenGroup(indent=True)
                    |Token.Control&Token.ElifBlock
                    |Token.Control&Token.Else&BlockTokenGroup(indent=True)),
    
]


if __name__ == '__main__':
    print(grammar)