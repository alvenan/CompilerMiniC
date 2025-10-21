from miniCVisitor import miniCVisitor
from miniCParser import miniCParser
from miniCLexer import miniCLexer

class Visitor(miniCVisitor):
    def __init__(self):
        self.scopes = [{}]
        self.function_signatures = {}
        self.errors = []
        self.in_loop = 0

    def _lookup(self, name):
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None

    def _declare(self, name, typ, token):
        cur = self.scopes[-1]
        if name in cur:
            self.errors.append(f"Erro: ({token.line},{token.column}): variável '{name}' redeclarada")
        else:
            cur[name] = typ

    def visitFunction_definition(self, ctx):
        ret = 'int'
        if ctx.type_specifier():
            ret = ctx.type_specifier().getText()
        func_name = ctx.function_header().declarator().getText()
        param_decl = ctx.function_header().parameter_list().parameter_declaration()
        param_types = []
        if param_decl:
            ptype = param_decl.type_specifier().getText()
            nparams = len(param_decl.declarator())
            param_types = [ptype] * nparams
        self.function_signatures[func_name] = {"ret": ret, "params": param_types}
        self.scopes.append({})
        if param_decl:
            ptype = param_decl.type_specifier().getText()
            for d in param_decl.declarator():
                name = d.getText()
                tok = d.IDENTIFIER().getSymbol()
                self._declare(name, ptype, tok)
        ctx.function_body().accept(self)
        self.scopes.pop()
        return None

    def visitData_definition(self, ctx):
        type_spec = ctx.type_specifier().getText()
        for decl in ctx.declarator():
            var_name = decl.getText()
            token = decl.IDENTIFIER().getSymbol()
            self._declare(var_name, type_spec, token)
        return self.visitChildren(ctx)

    def visitBinary(self, ctx):
        if ctx.getChildCount() >= 3 and hasattr(ctx.getChild(0), "getSymbol") and ctx.getChild(0).getSymbol():
            left_tok = ctx.getChild(0).getSymbol()
            var_name = ctx.getChild(0).getText()
            op = ctx.getChild(1).getText()
            rhs = ctx.getChild(2)
            lhs_type = self._lookup(var_name)
            if lhs_type is None:
                self.errors.append(f"Erro: ({left_tok.line},{left_tok.column}): variável '{var_name}' usada sem declaração")
            else:
                rhs_type = self.infer_type(rhs)
                if op == '=':
                    if lhs_type != rhs_type:
                        self.errors.append(f"Erro: ({left_tok.line},{left_tok.column}): incompatibilidade de tipos na atribuição '=' entre '{lhs_type}' e '{rhs_type}'")
                elif op in ['+=', '-=', '*=', '/=', '%=']:
                    if lhs_type != 'int' or rhs_type != 'int':
                        self.errors.append(f"Erro: ({left_tok.line},{left_tok.column}): operadores aritméticos de '{op}' exigem operandos int (encontrado lhs='{lhs_type}', rhs='{rhs_type}')")
        return self.visitChildren(ctx)

    def visitPrimary(self, ctx):
        if ctx.IDENTIFIER() and ctx.getChildCount() >= 3 and ctx.getChild(1).getText() == '(':
            func_name = ctx.IDENTIFIER().getText()
            token = ctx.IDENTIFIER().getSymbol()
            args = ctx.argument_list().binary() if ctx.argument_list() else []
            arg_types = [self.infer_type(arg) for arg in args]
            sig = self.function_signatures.get(func_name)
            if not sig:
                self.errors.append(f"Erro: ({token.line},{token.column}): chamada de função '{func_name}' não definida")
            else:
                expected = sig["params"]
                if len(arg_types) != len(expected):
                    self.errors.append(f"Erro: ({token.line},{token.column}): número de argumentos incorreto na chamada de '{func_name}'")
                else:
                    for i, (e, a) in enumerate(zip(expected, arg_types), start=1):
                        if e != a:
                            self.errors.append(f"Erro: ({token.line},{token.column}): tipo do argumento {i} incorreto na chamada de '{func_name}' (esperado '{e}', encontrado '{a}')")
        return self.visitChildren(ctx)

    def visitStatement(self, ctx):
        first = ctx.getChild(0).getText()
        if first == 'while':
            self.in_loop += 1
            self.visitChildren(ctx)
            self.in_loop -= 1
            return None
        elif first == 'break':
            token = ctx.getChild(0).getSymbol()
            if self.in_loop == 0:
                self.errors.append(f"Erro: ({token.line},{token.column}): comando 'break' fora do laço")
        elif first == 'continue':
            token = ctx.getChild(0).getSymbol()
            if self.in_loop == 0:
                self.errors.append(f"Erro: ({token.line},{token.column}): comando 'continue' fora do laço")
        return self.visitChildren(ctx)

    def infer_type(self, ctx):
        if isinstance(ctx, miniCParser.PrimaryContext):
            if ctx.CONSTANT_INT():
                return 'int'
            if ctx.CONSTANT_CHAR():
                return 'char'
            if ctx.IDENTIFIER() and ctx.getChildCount() == 1:
                name = ctx.IDENTIFIER().getText()
                return self._lookup(name) or 'unknown'
            if ctx.IDENTIFIER() and ctx.getChildCount() >= 3 and ctx.getChild(1).getText() == '(':
                fname = ctx.IDENTIFIER().getText()
                sig = self.function_signatures.get(fname)
                return sig["ret"] if sig else 'unknown'
            if ctx.expression():
                return self.infer_type(ctx.expression())
            return 'unknown'
        if isinstance(ctx, miniCParser.UnaryContext):
            if ctx.IDENTIFIER():
                name = ctx.IDENTIFIER().getText()
                return self._lookup(name) or 'unknown'
            return self.infer_type(ctx.getChild(0))
        if isinstance(ctx, miniCParser.BinaryContext):
            if ctx.getChildCount() == 1:
                return self.infer_type(ctx.getChild(0))
            if ctx.getChildCount() == 3:
                op = ctx.getChild(1).getText()
                if op in ['+', '-', '*', '/', '%']:
                    left = self.infer_type(ctx.getChild(0))
                    right = self.infer_type(ctx.getChild(2))
                    if left != 'int' or right != 'int':
                        tok = ctx.getChild(1).getSymbol()
                        self.errors.append(f"Erro: ({tok.line},{tok.column}): operandos de operadores aritméticos devem ser do tipo int (encontrado '{left}' e '{right}')")
                    return 'int'
                if op in ['==', '!=', '<', '<=', '>=']:
                    return 'int'
            return 'unknown'
        if ctx.getChildCount() == 1:
            return self.infer_type(ctx.getChild(0))
        return 'unknown'