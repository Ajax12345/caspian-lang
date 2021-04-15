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
    (Token.Bool, Token.Label.match('true')
                    |Token.Label.match('false')),
    (Token.Null, Token.Label.match('null')),
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
    (Token.Expr, Token.Label
                    |Token.Operation
                    |Token.Integer
                    |Token.Float
                    |Token.String
                    |Token.NegativeVal),
]
if __name__ == '__main__':
    print(grammar[2])