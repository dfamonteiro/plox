# Autogenerated file

from Token import Token
from expr import Expr

class StmtVisitor:
    def visit_expression_stmt(self, stmt):
        raise NotImplementedError()
    def visit_print_stmt(self, stmt):
        raise NotImplementedError()
    def visit_var_stmt(self, stmt):
        raise NotImplementedError()


class Stmt:
    def accept(self, visitor : StmtVisitor):
        raise NotImplementedError()

class Expression(Stmt):
    expression : Expr

    def __init__(self, expression : Expr):
        self.expression = expression

    def accept(self, visitor : StmtVisitor):
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    expression : Expr

    def __init__(self, expression : Expr):
        self.expression = expression

    def accept(self, visitor : StmtVisitor):
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    name : Token
    initializer : Expr

    def __init__(self, name : Token, initializer : Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor : StmtVisitor):
        return visitor.visit_var_stmt(self)


