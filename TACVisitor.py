"""Author: Alison Venâncio"""

from miniCVisitor import miniCVisitor
from miniCParser import miniCParser

class TACVisitor(miniCVisitor):
    def __init__(self):
        self.code = []
        self._t = 0
        self._l = 0
        self._break = []
        self._cont = []
        self.func_rets = {}

    def _new_t(self):
        self._t += 1
        return f"t{self._t}"

    def _new_l(self):
        self._l += 1
        return f"L{self._l}"

    def visitProgram(self, ctx):
        for d in ctx.definition():
            d.accept(self)
        return None

    def visitDefinition(self, ctx):
        return self.visitChildren(ctx)

    def visitData_definition(self, ctx):
        typ = ctx.type_specifier().getText()
        for d in ctx.declarator():
            name = d.IDENTIFIER().getText()
            self.code.append(f"var {typ} {name}")
            if d.getChildCount() >= 3 and d.getChild(1).getText() == '=':
                init = d.getChild(2).getText()
                self.code.append(f"{name} = {init}")
        return None

    def visitFunction_definition(self, ctx):
        rett = "int"
        if ctx.type_specifier():
            rett = ctx.type_specifier().getText()
        fname = ctx.function_header().declarator().getText()
        self.func_rets[fname] = rett
        self.code.append(f"func {rett} {fname}")

        plist = ctx.function_header().parameter_list()
        if plist and plist.parameter():
            for p in plist.parameter():
                self.code.append(f"param {p.type_specifier().getText()} {p.declarator().getText()}")
        else:
            pdecl = None
            if plist and hasattr(plist, 'parameter_declaration'):
                pdecl = plist.parameter_declaration()
            if pdecl:
                ptyp = pdecl.type_specifier().getText()
                for d in pdecl.declarator():
                    self.code.append(f"param {ptyp} {d.getText()}")

        ctx.function_body().accept(self)
        self.code.append(f"endfunc {fname}")
        return None

    def visitFunction_body(self, ctx):
        for dd in ctx.data_definition():
            dd.accept(self)
        for st in ctx.statement():
            st.accept(self)
        return None

    def visitStatement(self, ctx):
        k = ctx.getChild(0).getText()
        if k == ';':
            return None
        if ctx.block():
            for s in ctx.block().statement():
                s.accept(self)
            return None
        if k == 'return':
            if ctx.expression():
                v = ctx.expression().accept(self)
                self.code.append(f"ret {v}")
            else:
                self.code.append("ret")
            return None
        if k == 'if':
            cond = ctx.expression().accept(self)
            l_else = self._new_l()
            l_end = self._new_l()
            self.code.append(f"ifz {cond} goto {l_else}")
            ctx.statement(0).accept(self)
            if ctx.statement(1) is not None:
                self.code.append(f"goto {l_end}")
                self.code.append(f"label {l_else}")
                ctx.statement(1).accept(self)
                self.code.append(f"label {l_end}")
            else:
                self.code.append(f"label {l_else}")
            return None
        if k == 'while':
            l_start = self._new_l()
            l_end = self._new_l()
            self._break.append(l_end)
            self._cont.append(l_start)
            self.code.append(f"label {l_start}")
            cond = ctx.expression().accept(self)
            self.code.append(f"ifz {cond} goto {l_end}")
            ctx.statement(0).accept(self)
            self.code.append(f"goto {l_start}")
            self.code.append(f"label {l_end}")
            self._cont.pop()
            self._break.pop()
            return None
        if k == 'break':
            self.code.append(f"goto {self._break[-1]}")
            return None
        if k == 'continue':
            self.code.append(f"goto {self._cont[-1]}")
            return None
        if ctx.expression():
            ctx.expression().accept(self)
            return None
        return None

    def visitExpression(self, ctx):
        return ctx.binary().accept(self)

    def visitUnary(self, ctx):
        if ctx.IDENTIFIER():
            name = ctx.IDENTIFIER().getText()
            op = ctx.getChild(0).getText()
            one = self._new_t()
            self.code.append(f"{one} = 1")
            if op == '++':
                self.code.append(f"{name} = {name} + {one}")
                return name
            else:
                self.code.append(f"{name} = {name} - {one}")
                return name
        return ctx.primary().accept(self)

    def visitPrimary(self, ctx):
        if ctx.IDENTIFIER() and ctx.getChildCount() == 1:
            return ctx.IDENTIFIER().getText()
        if ctx.CONSTANT_INT():
            return ctx.CONSTANT_INT().getText()
        if hasattr(ctx, "CONSTANT_CHAR") and ctx.CONSTANT_CHAR():
            return ctx.CONSTANT_CHAR().getText()
        if ctx.expression():
            return ctx.expression().accept(self)
        if ctx.IDENTIFIER() and ctx.getChildCount() >= 3 and ctx.getChild(1).getText() == '(':
            fname = ctx.IDENTIFIER().getText()
            if fname == 'printf' and ctx.argument_list() and ctx.argument_list().CONSTANT_STRING():
                args = ctx.argument_list().binary() if ctx.argument_list() else []
                if args:
                    val = args[0].accept(self)
                    self.code.append(f"print {val}")
                    return None
            args = []
            if ctx.argument_list():
                if hasattr(ctx.argument_list(), 'binary'):
                    args = ctx.argument_list().binary() or []
            vals = [a.accept(self) for a in args]
            for v in vals:
                self.code.append(f"arg {v}")

            rett = self.func_rets.get(fname, "int")
            if rett == "void":
                self.code.append(f"call {fname}, {len(vals)}")
                return None

            res = self._new_t()
            self.code.append(f"{res} = call {fname}, {len(vals)}")
            return res
        return None

    def visitBinary(self, ctx):
        n = ctx.getChildCount()
        if n == 1:
            return ctx.getChild(0).accept(self)
        if n == 3 and ctx.getChild(1).getText() in ['=', '+=', '-=', '*=', '/=', '%='] and ctx.getChild(0).getText().isidentifier():
            lhs = ctx.getChild(0).getText()
            op = ctx.getChild(1).getText()
            r = ctx.getChild(2).accept(self)
            if op == '=':
                self.code.append(f"{lhs} = {r}")
                return lhs
            base = {'+=':'+', '-=':'-', '*=':'*', '/=':'/', '%=':'%'}[op]
            t = self._new_t()
            self.code.append(f"{t} = {lhs} {base} {r}")
            self.code.append(f"{lhs} = {t}")
            return lhs
        if n == 3:
            left_node = ctx.getChild(0)
            op = ctx.getChild(1).getText()
            if hasattr(left_node, "getChildCount") and left_node.getChildCount() == 3:
                left_op = left_node.getChild(1).getText()
                if left_op == '=' and left_node.getChild(0).getText().isidentifier():
                    lhs = left_node.getChild(0).getText()
                    e1 = left_node.getChild(2).accept(self)
                    e2 = ctx.getChild(2).accept(self)
                    t = self._new_t()
                    self.code.append(f"{t} = {e1} {op} {e2}")
                    self.code.append(f"{lhs} = {t}")
                    return t
        if n == 3:
            a = ctx.getChild(0).accept(self)
            op = ctx.getChild(1).getText()
            b = ctx.getChild(2).accept(self)
            t = self._new_t()
            self.code.append(f"{t} = {a} {op} {b}")
            return t
        return None