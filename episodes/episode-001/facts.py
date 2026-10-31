"""Single source of truth for every technical fact shown on screen.
Scenes import from here; automation/validate_technical.py proves each fact against a real CPython."""
PYTHON_MINOR = (3, 12)
# dis.dis(add) rows exactly as shown on screen: (offset, opname, displayed argument)
ROWS = [("0", "RESUME", "0"), ("2", "LOAD_FAST", "0 (a)"), ("4", "LOAD_FAST", "1 (b)"),
        ("6", "BINARY_OP", "0 (+)"), ("10", "RETURN_VALUE", "")]
CO_CODE_PREFIX = "97 00 7c 00"          # first bytes of add.__code__.co_code (3.12)
CO_CONSTS = "(None,)"
CO_VARNAMES = "('a', 'b')"
PYC_FILE = "mymodule.cpython-312.pyc"
TOKENS = [("total", "NAME"), ("=", "OP"), ("price", "NAME"), ("*", "OP"), ("2", "NUMBER")]
AST_LABELS = ["Assign", "Name: total", "BinOp", "Name: price", "Mult", "Constant: 2"]
FRAME_SRC = ['def parse(raw):', '    return raw.strip()', '', 'def load_user():', '    return parse(" Ada ")', '', 'load_user()']
TRACEBACK = [(7, "<module>"), (5, "load_user"), (2, "parse")]
