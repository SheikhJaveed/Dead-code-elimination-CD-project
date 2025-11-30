# Dead Code Elimination pass on TAC
from typing import List, Set
from .tac import Instr

def dead_code_elimination(instrs: List[Instr]) -> (List[Instr], List[Instr]):
    """
    Returns (optimized_instrs, dead_instrs)
    Simple backward liveness:
    - Start with variables used in print/return
    - Walk instructions backward; if instruction defines a variable that's not live, it's dead.
    - If it's live, add its operands to live set and keep the instruction.
    Note: we treat assignment to variables and temporaries uniformly.
    """
    live: Set[str] = set()
    keep = [False]*len(instrs)

    # Seed live set with operands in print/ret
    for idx, ins in enumerate(instrs):
        if ins.op == 'print' or ins.op == 'ret':
            for a in ins.args:
                if is_identifier(a):
                    live.add(a)

    # Backward scan
    for i in range(len(instrs)-1, -1, -1):
        ins = instrs[i]
        if ins.op in ('add','sub','mul','div'):
            # defines dest
            if ins.dest in live:
                # keep and mark operands live
                keep[i] = True
                for a in ins.args:
                    if is_identifier(a):
                        live.add(a)
            else:
                # dead, skip
                pass
        elif ins.op == 'assign':
            # defines dest variable
            if ins.dest in live or ins.dest.startswith('t') and ins.dest in live:
                keep[i] = True
                a = ins.args[0]
                if is_identifier(a):
                    live.add(a)
            else:
                # if dest is temporary (tX) and not live, then dead
                # if dest is a named variable but not live, also dead
                pass
        elif ins.op == 'print':
            keep[i] = True
            for a in ins.args:
                if is_identifier(a):
                    live.add(a)
        elif ins.op == 'ret':
            keep[i] = True
            for a in ins.args:
                if is_identifier(a):
                    live.add(a)
        else:
            # unknown ops: keep conservatively
            keep[i] = True
            for a in ins.args:
                if is_identifier(a):
                    live.add(a)

    optimized = [instrs[i] for i in range(len(instrs)) if keep[i]]
    dead = [instrs[i] for i in range(len(instrs)) if not keep[i]]
    return optimized, dead

def is_identifier(token: str) -> bool:
    # numbers are digits
    return not token.isdigit()
