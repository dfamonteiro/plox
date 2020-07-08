# Autogenerated file

from Token import Token
from typing import List

class ExprVisitor:
    def visit_assign_expr(self, expr):
        raise NotImplementedError()
    def visit_binary_expr(self, expr):
        raise NotImplementedError()
    def visit_call_expr(self, expr):
        raise NotImplementedError()
    def visit_get_expr(self, expr):
        raise NotImplementedError()
    def visit_grouping_expr(self, expr):
        raise NotImplementedError()
    def visit_literal_expr(self, expr):
        raise NotImplementedError()
    def visit_logical_expr(self, expr):
        raise NotImplementedError()
    def visit_set_expr(self, expr):
        raise NotImplementedError()
    def visit_this_expr(self, expr):
        raise NotImplementedError()
    def visit_unary_expr(self, expr):
        raise NotImplementedError()
    def visit_variable_expr(self, expr):
        raise NotImplementedError()


class Expr:
    def accept(self, visitor : ExprVisitor):
        raise NotImplementedError()

class Assign(Expr):
    name : Token
    value : Expr

    def __init__(self, name : Token, value : Expr):
        self.name = name
        self.value = value

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_assign_expr(self)


class Binary(Expr):
    left : Expr
    operator : Token
    right : Expr

    def __init__(self, left : Expr, operator : Token, right : Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_binary_expr(self)


class Call(Expr):
    callee : Expr
    paren : Token
    arguments : List[Expr]

    def __init__(self, callee : Expr, paren : Token, arguments : List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_call_expr(self)


class Get(Expr):
    _object : Expr
    name : Token

    def __init__(self, _object : Expr, name : Token):
        self._object = _object
        self.name = name

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_get_expr(self)


class Grouping(Expr):
    expression : Expr

    def __init__(self, expression : Expr):
        self.expression = expression

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    value : object

    def __init__(self, value : object):
        self.value = value

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_literal_expr(self)


class Logical(Expr):
    left : Expr
    operator : Token
    right : Expr

    def __init__(self, left : Expr, operator : Token, right : Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_logical_expr(self)


class Set(Expr):
    _object : Expr
    name : Token
    value : Expr

    def __init__(self, _object : Expr, name : Token, value : Expr):
        self._object = _object
        self.name = name
        self.value = value

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_set_expr(self)


class This(Expr):
    keyword : Token

    def __init__(self, keyword : Token):
        self.keyword = keyword

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_this_expr(self)


class Unary(Expr):
    operator : Token
    right : Expr

    def __init__(self, operator : Token, right : Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    name : Token

    def __init__(self, name : Token):
        self.name = name

    def accept(self, visitor : ExprVisitor):
        return visitor.visit_variable_expr(self)


