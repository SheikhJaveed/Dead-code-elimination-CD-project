# 🧠 Dead Code Elimination Based Compiler Front-End  
### *Using a Toy Language + TAC Generation + GCC Optimization Comparison* Inspired by: *"Finding Missed Optimizations through the Lens of Dead Code Elimination" (ASPLOS 2022)*

---

## 📌 Project Overview

This project implements a **mini-compiler front-end** for a simple *Toy Programming Language*.  
The system performs:

- **Lexical Analysis** - **Parsing (Shunting-Yard Algorithm for expressions)** - **Three-Address Code (TAC) Generation** - **Dead Code Elimination (DCE)** - **C Code Generation**
- **Comparison Against GCC `-O2` Optimizer** The project demonstrates how **Dead Code Elimination can be used to detect missed compiler optimizations**, replicating ideas from the 2022 ASPLOS research paper.

---

## 🎯 Motivation

Modern compilers like GCC/LLVM optimize programs heavily.  
However, they still **miss some optimizations**, especially when earlier passes (like constant folding or algebraic simplification) do not trigger.

The ASPLOS 2022 paper shows that **Dead Code Elimination (DCE)** is a powerful *lens* to detect these missed optimizations.

This project:

✔ Builds a toy compiler with DCE  
✔ Generates C code from TAC  
✔ Compiles the C using GCC `-O2`  
✔ Compares the optimizations  
✔ Highlights cases where GCC fails or succeeds  

This creates a **research-style analysis** suitable for academic evaluation.

---

## 🗂️ Project Structure

```text
compiler-dce-project/
├── README.md
├── requirements.txt
├── examples/
│   ├── sample1.toy
│   └── sample2.toy
└── src/
    ├── lexer.py
    ├── parser.py
    ├── tac.py
    ├── dce.py
    └── main.py
```

---

## 🔧 How the Compiler Works

### ✔ 1. Toy Language Input (.toy file)
A minimal instruction-based language:

```c
a = b * 0;
x = 5;
y = a + x;
unused = 100;
t1 = y * 1;
print(y);
```

### ✔ 2. Lexer (Tokenization)
Converts input characters → tokens:
`ID(a), ASSIGN(=), ID(b), TIMES(*), NUMBER(0), SEMICOLON(;)`

### ✔ 3. Parser
Uses Shunting-Yard Algorithm to convert expressions into postfix:
`a = b * 0;` → `[b, 0, *]`

Generates a list of structured statements.

### ✔ 4. TAC (Three Address Code) Generation
Expressions like:
```c
y = a + x;
```

Become TAC:
```text
t1 = a + x
y = t1
```
This intermediate representation is easier to optimize.

### ✔ 5. Dead Code Elimination (DCE)
Backward liveness analysis:
1. Start from `print()` and `return`
2. Mark required variables as live
3. Any instruction that doesn't contribute to output is dead

Example removed as dead:
```text
unused = 100
t3 = y * 1
t1 = t3
```

### ✔ 6. C Code Generation
Produces `sample1_from_tac.c` so we can test with real compilers.

### ✔ 7. GCC -O2 Optimization Comparison
Run:
```bash
gcc -O2 sample1_from_tac.c -S -o out.s
```
This produces assembly code (`out.s`).

Comparing:
1. Our DCE
2. GCC’s optimized output

shows whether GCC missed any optimizations.

---

## 📊 Architecture Diagram

```text
┌─────────┐       ┌────────┐       ┌────────────┐      ┌──────────────┐
│  .toy   │  -->  │ Lexer  │  -->  │   Parser   │ -->  │   TAC Gen    │
└─────────┘       └────────┘       └────────────┘      └──────┬───────┘
                                                              │
                                                        ┌─────▼──────┐
                                                        │    DCE     │
                                                        └─────┬──────┘
                                                              │
                                                       ┌──────▼────────┐
                                                       │ Optimized TAC │
                                                       └──────┬────────┘
                                                              │
                                                      ┌───────▼─────────┐
                                                      │   C Generator   │
                                                      └───────┬─────────┘
                                                              │
                                                      ┌───────▼─────────┐
                                                      │ GCC -O2 Compare │
                                                      └─────────────────┘
```

---

## 📝 Example Run

```bash
python -m src.main examples/sample1.toy
```

**Output:**
1. TAC before optimization
2. Dead instructions
3. Optimized TAC
4. Path of generated `.c` file

Then compile:
```bash
gcc -O2 sample1_from_tac.c -S -o out.s
```

---

## 🧪 What We Verify

This project checks:

✔ Did our DCE remove some dead instructions?
✔ Did GCC -O2 also remove them?
✔ Does GCC remove more because of constant folding?
✔ Does our tool catch dead code GCC missed?

This comparison embodies the research question:
> "Can DCE reveal optimization misses in real compilers?"

---

## 🔍 Example Result (Summary)

**Our DCE removed:**
```text
unused = 100
t3 = y * 1
t1 = t3
```

**GCC removed:**
* ALL of them
* PLUS it constant-folded: `y = 5`

**Final assembly only prints 5.**

This demonstrates:
1. GCC performs more advanced optimizations.
2. Our DCE reveals structural dead code.
3. This mirrors the ASPLOS 2022 paper’s key insight.

---

## 💡 Future Extensions

- Add constant folding
- Add algebraic simplification
- Add constant propagation
- Build a control-flow graph
- Convert TAC to SSA form
- Detect real compiler "missed optimizations"