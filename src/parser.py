# Parser for the toy language.
# Uses shunting-yard to parse expressions into postfix, then TAC generator uses postfix.
from typing import List, Tuple, Union
from dataclasses import dataclass
from .lexer import tokenize, Token

@dataclass
class Stmt:
    kind: str  # 'assign', 'print', 'return'
    target: str  # for assign: LHS name; for others, None
    expr: List[Union[str, Tuple]]  # postfix tokens (strings 'a','1' or operators '+','*')

def precedence(op: str) -> int:
    if op in ('+', '-'):
        return 1
    if op in ('*', '/'):
        return 2
    return 0

def shunting_yard(tokens: List[Token]) -> List[str]:
    """Return postfix list (tokens as strings)."""
    out = []
    stack = []
    for t in tokens:
        if t.type == 'NUMBER' or t.type == 'ID':
            out.append(t.value)
        elif t.type in ('PLUS','MINUS','TIMES','DIV'):
            op = t.value
            while stack and stack[-1] != '(' and precedence(stack[-1]) >= precedence(op):
                out.append(stack.pop())
            stack.append(op)
        elif t.type == 'LPAREN':
            stack.append('(')
        elif t.type == 'RPAREN':
            while stack and stack[-1] != '(':
                out.append(stack.pop())
            if not stack:
                raise RuntimeError("Mismatched parenthesis")
            stack.pop()
        else:
            raise RuntimeError(f"Unexpected token in expression: {t}")
    while stack:
        if stack[-1] == '(':
            raise RuntimeError("Mismatched parenthesis")
        out.append(stack.pop())
    return out

def parse(code: str) -> List[Stmt]:
    tokens = tokenize(code)
    i = 0
    stmts: List[Stmt] = []
    n = len(tokens)
    while i < n:
        t = tokens[i]
        # print statement
        if t.type == 'PRINT':
            # expect LPAREN expr RPAREN SEMICOLON
            if tokens[i+1].type != 'LPAREN': raise RuntimeError("Expected ( after print")
            j = i+2
            expr_tokens = []
            # collect until RPAREN
            while j < n and tokens[j].type != 'RPAREN':
                expr_tokens.append(tokens[j])
                j += 1
            if j >= n: raise RuntimeError("Missing ) after print")
            postfix = shunting_yard(expr_tokens)
            if tokens[j+1].type != 'SEMICOLON': raise RuntimeError("Missing ; after print")
            stmts.append(Stmt(kind='print', target=None, expr=postfix))
            i = j+2
        # return statement
        elif t.type == 'RETURN':
            if tokens[i+1].type != 'LPAREN': raise RuntimeError("Expected ( after return")
            j = i+2
            expr_tokens = []
            while j < n and tokens[j].type != 'RPAREN':
                expr_tokens.append(tokens[j])
                j += 1
            if j >= n: raise RuntimeError("Missing ) after return")
            postfix = shunting_yard(expr_tokens)
            if tokens[j+1].type != 'SEMICOLON': raise RuntimeError("Missing ; after return")
            stmts.append(Stmt(kind='return', target=None, expr=postfix))
            i = j+2
        # assignment
        elif t.type == 'ID' and i+1 < n and tokens[i+1].type == 'ASSIGN':
            lhs = t.value
            # collect expression tokens until semicolon
            j = i+2
            expr_tokens = []
            while j < n and tokens[j].type != 'SEMICOLON':
                expr_tokens.append(tokens[j])
                j += 1
            if j >= n: raise RuntimeError("Missing ; in assignment")
            postfix = shunting_yard(expr_tokens)
            stmts.append(Stmt(kind='assign', target=lhs, expr=postfix))
            i = j+1
        else:
            raise RuntimeError(f"Parse error at token {t} (position {i})")
    return stmts

# quick test
if __name__ == "__main__":
    code = "a = b * 0; t = a + 5; print(t);"
    s = parse(code)
    for st in s:
        print(st)
