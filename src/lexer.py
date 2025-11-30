import re
from dataclasses import dataclass
from typing import List

TOKEN_SPEC = [
    ('NUMBER',   r'\d+'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('ASSIGN',   r'='),
    ('SEMICOLON', r';'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('PLUS',     r'\+'),
    ('MINUS',    r'-'),
    ('TIMES',    r'\*'),
    ('DIV',      r'/'),
    ('COMMA',    r','),
    ('COMMENT',  r'\#.*'),       # ← FIX ADDED
    ('SKIP',     r'[ \t]+'),
    ('NEWLINE',  r'\n'),
    ('MISMATCH', r'.'),
]

TOKEN_RE = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC))

KEYWORDS = {'print', 'return'}

@dataclass
class Token:
    type: str
    value: str

def tokenize(code: str) -> List[Token]:
    tokens = []
    for mo in TOKEN_RE.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            tokens.append(Token('NUMBER', value))
        elif kind == 'ID':
            if value in KEYWORDS:
                tokens.append(Token(value.upper(), value))
            else:
                tokens.append(Token('ID', value))
        elif kind in ('ASSIGN','SEMICOLON','LPAREN','RPAREN','PLUS','MINUS','TIMES','DIV','COMMA'):
            tokens.append(Token(kind, value))
        elif kind == 'COMMENT':
            continue      # ← Ignore full-line or inline comments
        elif kind == 'NEWLINE' or kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character: {value}')
    return tokens
