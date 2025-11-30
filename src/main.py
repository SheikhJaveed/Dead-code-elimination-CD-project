# CLI to run the pipeline: parse -> TAC -> DCE -> report
import argparse
from .parser import parse
from .tac import TACGenerator
from .dce import dead_code_elimination
import os

def pretty_print_instrs(instrs):
    for i, ins in enumerate(instrs):
        print(f"{i:03}: {ins}")

def generate_c_from_instrs(instrs, out_path):
    # Very simple C generator for demonstration (makes a main with ints).
    lines = []
    lines.append("#include <stdio.h>")
    lines.append("int main(){")
    # declare variables (collect all non-temporary names)
    vars = set()
    for ins in instrs:
        if ins.op in ('assign','add','sub','mul','div'):
            if not ins.dest.startswith('t'):
                vars.add(ins.dest)
            for a in ins.args:
                if not a.isdigit() and not a.startswith('t'):
                    vars.add(a)
    if vars:
        decl = "int " + ", ".join(sorted(vars)) + " = 0;"
        lines.append(decl)
    # for temporaries we just inline the computations as assigned to declared vars or unused temps
    for ins in instrs:
        if ins.op == 'assign':
            lines.append(f"{ins.dest} = {ins.args[0]};")
        elif ins.op in ('add','sub','mul','div'):
            sym = {'add':'+','sub':'-','mul':'*','div':'/'}[ins.op]
            lines.append(f"int {ins.dest} = {ins.args[0]} {sym} {ins.args[1]};")
        elif ins.op == 'print':
            a = ins.args[0]
            lines.append(f"printf(\"%d\\n\", {a});")
        elif ins.op == 'ret':
            lines.append(f"return {ins.args[0]};")
    lines.append("return 0;")
    lines.append("}")
    with open(out_path, 'w') as f:
        f.write("\n".join(lines))
    return out_path

def run_file(path):
    with open(path, 'r') as f:
        code = f.read()
    print("=== Input code ===")
    print(code)
    # parse
    stmts = parse(code)
    gen = TACGenerator()
    gen.generate_from_stmtlist(stmts)
    instrs = gen.get_instrs()
    print("\n=== Generated TAC ===")
    pretty_print_instrs(instrs)
    optimized, dead = dead_code_elimination(instrs)
    print("\n=== Dead Instructions ===")
    if dead:
        pretty_print_instrs(dead)
    else:
        print("None")
    print("\n=== Optimized TAC ===")
    pretty_print_instrs(optimized)

    # produce C file for compiler comparison
    base = os.path.basename(path)
    c_out = os.path.splitext(base)[0] + "_from_tac.c"
    cpath = os.path.join(os.path.dirname(path), "..", c_out)
    generate_c_from_instrs(instrs, cpath)
    print(f"\nA C file was generated at: {cpath}")
    print("You can compile with: gcc -O2 {0} -o {1}.exe".format(cpath, cpath.replace('.c','')))
    print("Then inspect assembly with: gcc -O2 -S -o out.s {0}".format(cpath))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Toy compiler front-end + DCE")
    parser.add_argument("file", help="path to .toy file")
    args = parser.parse_args()
    run_file(args.file)
