import re, typing
from caspian_token_objs import *

__all__ = ('Token', 'tokens', 'grammar')

Token = TokenMain.TokenBase()

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
    (Token.Null,    Token.Label.match('null')),
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
                    |Token.Label.match('in')._('in')),
    (Token.Operation, (Token.Expr&Token.Operator&Token.Expr).neg_lookahead(Token.Star&Token.Slash)),
    (Token.NegativeVal, Token.Minus&Token.Expr),
    (Token.Comment,   Token.Slash&Token.Slash),
    (Token.CommaList, (Token.Expr&Token.Comma&Token.Expr
                      |Token.Expr&Token.Comma&Token.CommaList
                      |Token.ArrayUnpack
                      |Token.MapUnpack
                      |Token.CommaList&Token.Comma&Token.CommaList
                      |Token.CommaList&Token.Comma&Token.Expr).ml),
    (Token.MapCommaList, (Token.Expr&Token.Colon&Token.Expr&Token.Comma&Token.Expr&Token.Colon&Token.Expr
                      |Token.Expr&Token.Colon&Token.Expr&Token.Comma&Token.MapCommaList
                      |Token.MapUnpack
                      |Token.MapCommaList&Token.Comma&Token.MapCommaList
                      |Token.MapCommaList&Token.Comma&Token.Expr&Token.Colon&Token.Expr).ml),
    (Token.Array,   (Token.OBracket&Token.CBracket
                      |Token.OBracket&Token.Expr&Token.CBracket
                      |Token.OBracket&Token.CommaList&Token.CBracket).ml),
    (Token.Map,     (Token.OBrace&Token.CBrace
                      |Token.OBrace&Token.Expr&Token.Colon&Token.Expr&Token.CBrace
                      |Token.OBrace&Token.MapCommaList&Token.CBrace).ml),
    (Token.ImmutableContainer, Token.Pound&Token.Array
                               |Token.Pound&Token.Map),
    (Token.ArrayUnpack, Token.Dot&Token.Dot&Token.Expr),
    (Token.MapUnpack, Token.Dot&Token.Dot&Token.Dot&Token.Expr),
    (Token.Primative, Token.Label.match('primative')&Token.Colon&Token.Colon&Token.Label),
    (Token.ChainCall, (Token.Expr&Token.Pipe&Token.RArrow&Token.Expr
                      |Token.Expr&Token.Pipe&Token.RArrow&Token.ChainCall).ml),
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
                    |Token.Expr&Token.OParen&Token.CParen._('f_call')
                    |Token.Expr&Token.OParen&Token.CommaList&Token.CParen._('f_call')
                    |Token.ChainCall
                    ),

    (Token.Assign, (Token.Label
                    |Token.Array
                    |Token.Map
                    |Token.CommaList)
                    &Token.Eq
                    &(Token.Expr
                    |Token.CommaList)),
    

]
#TODO: getattr
#TODO: getitem
#TODO: inline conditional
#TODO: array comprehension
#TODO: map comprehension
#TODO: await <promise>
if __name__ == '__main__':
    print(grammar[6][-1])