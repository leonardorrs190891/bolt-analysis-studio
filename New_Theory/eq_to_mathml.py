# -*- coding: utf-8 -*-
"""Converte uma linha de equação ASCII/Unicode do modelo em MathML (nível de
TOKEN — sem árvore de precedência, portanto seguro: só melhora a tipografia, não
reinterpreta a matemática). Subscritos (`k_b`→k com b pequeno), sobrescritos
(`x^k`, `F²`), símbolos gregos e operadores grandes (Σ, ∫) saem de verdade.

`is_convertible(line)` recusa linhas de PSEUDOCÓDIGO/prosa (label:, piecewise `|`,
palavras `se/senao/legacy/ISO`…) — essas ficam em monospace, honestamente.
"""
import html as _html
import re

FUNCS = {"arctan", "arcsin", "arccos", "min", "max", "hypot", "ln", "log",
         "exp", "sin", "cos", "tan", "sqrt", "abs"}

_SUB = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5",
        "₆": "6", "₇": "7", "₈": "8", "₉": "9", "ᵢ": "i", "ₙ": "n"}
_SUP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
        "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}
_OPMAP = {"*": "·", "-": "−"}

_SKIP = re.compile(r"\b(se|senao|sen[aã]o|apos|ap[oó]s|legacy|ISO|ou|gates?|"
                   r"dwell|onset|bending|axial_frac|knee|senão)\b", re.I)

_TOK = re.compile(
    r"(?P<ws>\s+)"
    r"|(?P<num>\d+\.?\d*)"
    r"|(?P<id>[A-Za-zΑ-Ωα-ω∞]"
    r"[A-Za-z0-9Α-Ωα-ω]*(?:_[A-Za-z0-9Α-Ωα-ω]+)*)"
    r"|(?P<caret>\^)"
    r"|(?P<open>[(\[{])"
    r"|(?P<close>[)\]}])"
    r"|(?P<op>[=+\-−·*/,;<>≤≥≈∝←⇒×÷∈∘•|])"
    r"|(?P<other>.)")


def _pre(s):
    for k, v in _SUB.items():
        s = s.replace(k, "_" + v)
    for k, v in _SUP.items():
        s = s.replace(k, "^" + v)
    return s


def is_convertible(part):
    p = part.strip()
    if not p or p in ("|",):
        return False
    if re.match(r"^[A-Za-z_][\w]*\s*:", p):     # rótulo de pseudocódigo (damage:, …)
        return False
    if "|" in p or "⇒" in p or "⇐" in p:
        return False
    if _SKIP.search(p):
        return False
    return True


def _ident(tok):
    if "_" in tok:
        base, rest = tok.split("_", 1)
        sub = rest.replace("_", " ")
        return "<msub><mi>%s</mi><mi>%s</mi></msub>" % (_html.escape(base), _html.escape(sub))
    return "<mi>%s</mi>" % _html.escape(tok)


def _tokens(s):
    out = []
    for m in _TOK.finditer(s):
        k = m.lastgroup
        out.append((k, m.group()))
    return out


def _read_operand(toks, i):
    """Operando de um sobrescrito: um grupo entre parênteses (sem os parênteses) ou
    um único token."""
    while i < len(toks) and toks[i][0] == "ws":
        i += 1
    if i < len(toks) and toks[i][0] == "open":
        inner, j = _group_inner(toks, i)
        return "<mrow>%s</mrow>" % inner, j
    if i < len(toks):
        k, t = toks[i]
        if k == "num":
            return "<mn>%s</mn>" % t, i + 1
        if k == "id":
            return _ident(t), i + 1
        if k in ("op", "other"):
            return "<mo>%s</mo>" % _html.escape(_OPMAP.get(t, t)), i + 1
    return "<mi></mi>", i


def _group_inner(toks, i):
    """Consome um grupo balanceado ( [ { ... } ] ) e devolve o MathML do MIOLO
    (sem os delimitadores) + índice após o fechamento."""
    assert toks[i][0] == "open"
    depth, j = 0, i
    while j < len(toks):
        if toks[j][0] == "open":
            depth += 1
        elif toks[j][0] == "close":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return _emit(toks[i + 1:j]), j + 1


def _emit(toks):
    out, i, n = [], 0, len(toks)
    while i < n:
        k, t = toks[i]
        if k == "ws":
            i += 1
        elif k == "caret":
            sup, i = _read_operand(toks, i + 1)
            base = out.pop() if out else "<mi></mi>"
            out.append("<msup>%s%s</msup>" % (base, sup))
        elif k == "open":
            inner, i = _group_inner(toks, i)
            out.append("<mo>%s</mo><mrow>%s</mrow><mo>%s</mo>"
                       % (_html.escape(t), inner, ")" if t == "(" else ("]" if t == "[" else "}")))
        elif k == "num":
            out.append("<mn>%s</mn>" % t); i += 1
        elif k == "id":
            out.append(_ident(t)); i += 1
        elif k == "close":
            out.append("<mo>%s</mo>" % _html.escape(t)); i += 1
        else:  # op / other
            out.append("<mo>%s</mo>" % _html.escape(_OPMAP.get(t, t))); i += 1
    return "".join(out)


def to_mathml(line):
    """MathML de uma linha de matemática limpa (assume is_convertible)."""
    toks = _tokens(_pre(line))
    return '<math display="block">%s</math>' % _emit(toks)
