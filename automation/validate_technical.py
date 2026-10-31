"""Technical-validation stage: run every on-screen claim against a real interpreter.
Writes build/technical_validation.json; non-zero exit blocks rendering."""
import ast, dis, gc, importlib.util, io, json, py_compile, sys, tokenize, traceback, weakref
from config import *

def load_facts(ep):
    spec = importlib.util.spec_from_file_location("facts", ep_dir(ep) / "facts.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def run(ep):
    F = load_facts(ep); res = []
    def check(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": str(detail)}); print(("PASS " if ok else "FAIL ") + name, detail if not ok else "")

    check("interpreter matches narrated version", sys.version_info[:2] == F.PYTHON_MINOR, sys.version.split()[0])

    def add(a, b):
        return a + b
    rows = []
    for ins in dis.get_instructions(add):
        arg = f"{ins.arg} ({ins.argrepr})" if ins.argrepr else (str(ins.arg) if ins.opcode >= dis.HAVE_ARGUMENT else "")
        rows.append((str(ins.offset), ins.opname, arg))
    check("dis rows == on-screen rows", rows == [tuple(r) for r in F.ROWS], rows)
    co = add.__code__
    check("co_code prefix", " ".join(f"{b:02x}" for b in co.co_code[:4]) == F.CO_CODE_PREFIX, co.co_code[:4].hex())
    check("co_consts", repr(co.co_consts) == F.CO_CONSTS, co.co_consts)
    check("co_varnames", repr(co.co_varnames) == F.CO_VARNAMES, co.co_varnames)

    toks = [(t.string, tokenize.tok_name[t.type]) for t in tokenize.generate_tokens(io.StringIO("total = price * 2\n").readline)
            if t.type not in (tokenize.NEWLINE, tokenize.ENDMARKER)]
    check("tokenizer output (5 tokens)", toks == F.TOKENS, toks)
    n = ast.parse("total = price * 2").body[0]
    ok = (isinstance(n, ast.Assign) and n.targets[0].id == "total" and isinstance(n.value, ast.BinOp) and n.value.left.id == "price"
          and isinstance(n.value.op, ast.Mult) and n.value.right.value == 2)
    check("AST shape (Assign -> BinOp(Name, Mult, Constant))", ok)
    try:
        compile("total = * 2", "<s>", "exec"); check("syntax errors raised at compile time", False)
    except SyntaxError:
        check("syntax errors raised at compile time", True)

    class Obj: pass
    x = [1, 2, 3]; y = x
    check("assignment shares one object", x is y)
    check("refcount is 2 with two names", sys.getrefcount(x) - 1 == 2, sys.getrefcount(x) - 1)
    y.append(4); check("mutation visible through other name", x == [1, 2, 3, 4])
    y = None; check("refcount drops to 1", sys.getrefcount(x) - 1 == 1, sys.getrefcount(x) - 1)
    o = Obj(); w = weakref.ref(o); del o
    check("object freed immediately at refcount 0", w() is None)

    src = "\n".join(F.FRAME_SRC).replace("raw.strip()", "raw.strp()") + "\n"
    try:
        exec(compile(src, "app.py", "exec"), {})
    except AttributeError:
        got = [(f.lineno, f.name) for f in traceback.extract_tb(sys.exc_info()[2])][1:]   # drop this exec frame
        check("traceback frames/lines match call-stack scene", got == F.TRACEBACK, got)
    def rec(): rec()
    try: rec(); check("runaway recursion -> RecursionError", False)
    except RecursionError as e: check("runaway recursion -> RecursionError", "maximum recursion depth exceeded" in str(e))
    check("pyc cache filename", py_compile.importlib.util.cache_from_source("mymodule.py").endswith("__pycache__/" + F.PYC_FILE) or
          py_compile.importlib.util.cache_from_source("mymodule.py").endswith("__pycache__\\" + F.PYC_FILE))
    for _ in range(2000): add(2, 3)
    names = [i.opname for i in dis.get_instructions(add, adaptive=True)]
    check("3.11+ specializes hot bytecode (BINARY_OP_ADD_INT)", "BINARY_OP_ADD_INT" in names, names)
    # Reasoned (not machine-checkable) claims are listed so a human reviewer sees them:
    manual = ["PyPy has a JIT (documented by PyPy project)", "CPython 3.11 introduced the adaptive specializing interpreter (What's New 3.11)"]
    out = {"python": sys.version, "all_pass": all(r["pass"] for r in res), "checks": res, "documented_claims_for_human_review": manual}
    json.dump(out, open(build_dir(ep) / "technical_validation.json", "w"), indent=2)
    print(f"[validate] {sum(r['pass'] for r in res)}/{len(res)} passed"); return out["all_pass"]

if __name__ == "__main__":
    sys.exit(0 if run(sys.argv[1] if len(sys.argv) > 1 else "episode-001") else 1)
