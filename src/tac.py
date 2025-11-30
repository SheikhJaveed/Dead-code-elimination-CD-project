# Three-Address Code (TAC) generator from postfix expressions
from typing import List, Tuple
from dataclasses import dataclass
from .parser import Stmt

@dataclass
class Instr:
    op: str       # 'assign','add','sub','mul','div','print','ret'
    dest: str     # destination temporary or variable (for print/ret dest can be '')
    args: List[str]  # operands, variable names or constants

    def __repr__(self):
        if self.op == 'assign':
            return f"{self.dest} = {self.args[0]}"
        elif self.op in ('add','sub','mul','div'):
            sym = {'add':'+','sub':'-','mul':'*','div':'/'}[self.op]
            return f"{self.dest} = {self.args[0]} {sym} {self.args[1]}"
        elif self.op == 'print':
            return f"print {self.args[0]}"
        elif self.op == 'ret':
            return f"return {self.args[0]}"
        else:
            return f"{self.op} {self.args} -> {self.dest}"

class TACGenerator:
    def __init__(self):
        self.tmp_count = 0
        self.instrs: List[Instr] = []

    def new_tmp(self) -> str:
        self.tmp_count += 1
        return f"t{self.tmp_count}"

    def generate_from_stmtlist(self, stmts: List[Stmt]):
        for s in stmts:
            if s.kind == 'assign':
                result = self._gen_expr(s.expr)
                # result is either a name or const; if result is temp, assign to LHS
                if result.startswith('t'):
                    # move temp -> lhs
                    self.instrs.append(Instr('assign', s.target, [result]))
                else:
                    # constant or variable
                    self.instrs.append(Instr('assign', s.target, [result]))
            elif s.kind == 'print':
                result = self._gen_expr(s.expr)
                self.instrs.append(Instr('print', '', [result]))
            elif s.kind == 'return':
                result = self._gen_expr(s.expr)
                self.instrs.append(Instr('ret', '', [result]))

    def _gen_expr(self, postfix: List[str]) -> str:
        stack = []
        for tok in postfix:
            if tok in ('+','-','*','/'):
                b = stack.pop()
                a = stack.pop()
                tmp = self.new_tmp()
                opmap = {'+':'add','-':'sub','*':'mul','/':'div'}
                self.instrs.append(Instr(opmap[tok], tmp, [a,b]))
                stack.append(tmp)
            else:
                # number or id
                stack.append(tok)
        if len(stack) != 1:
            raise RuntimeError("Expression parse error, stack != 1")
        return stack[0]

    def get_instrs(self) -> List[Instr]:
        return self.instrs

# test
if __name__ == "__main__":
    from .parser import parse
    code = "a = b * 0; t = a + 5; print(t);"
    stmts = parse(code)
    gen = TACGenerator()
    gen.generate_from_stmtlist(stmts)
    for ins in gen.get_instrs():
        print(ins)
