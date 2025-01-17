from typing import List, Deque, Dict
from collections import deque
from enum import Enum, auto

import Expr
import Token
import lox
import Stmt
import Environment
import LoxCallable
import LoxFunction
import Interpreter

class ClassType(Enum):
    NONE     = auto()
    CLASS    = auto()
    SUBCLASS = auto()

class Resolver(Expr.ExprVisitor, Stmt.StmtVisitor):
    scopes : Deque[Dict[str, bool]]
    current_function : LoxFunction.FunctionType
    current_class : ClassType
    interpreter : Interpreter.Interpreter

    def __init__(self, interpreter : Interpreter.Interpreter):
        self.interpreter = interpreter
        self.scopes = deque()
        self.current_function = LoxFunction.FunctionType.NONE
        self.current_class = ClassType.NONE

    def visit_block_stmt(self, stmt : Stmt.Block):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
    
    def resolve(self, statements : List[Stmt.Stmt]):
        if isinstance(statements, Stmt.Stmt):
            statements.accept(self)
        elif isinstance(statements, Expr.Expr):
            statements.accept(self)
        else:
            for statement in statements:
                self.resolve(statement)
    
    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()
    
    def declare(self, name : Token.Token):
        if len(self.scopes) == 0:
            return
        
        if name.lexeme in self.scopes[-1]:
            lox.error(name, "Variable with this name already declared in this scope.")
        
        self.scopes[-1][name.lexeme] = False
    
    def define(self, name : Token.Token):
        if len(self.scopes) == 0:
            return
        
        self.scopes[-1][name.lexeme] = True

    def visit_logical_expr(self, expression : Expr.Logical):
        self.resolve(expression.left)
        self.resolve(expression.right)
    
    def visit_while_stmt(self, stmt : Stmt.While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    
    def visit_if_stmt(self, stmt : Stmt.If):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)

        if stmt.else_branch != None:
            self.resolve(stmt.else_branch)

    def visit_expression_stmt(self, stmt : Stmt.Expression):
        self.resolve(stmt.expression)

    def visit_print_stmt(self, stmt : Stmt.Print):
        self.resolve(stmt.expression)
    
    def visit_var_stmt(self, stmt : Stmt.Var):
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
    
    def visit_assign_expr(self, expr : Expr.Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)        

    def visit_binary_expr(self, expr : Expr.Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visit_function_stmt(self, stmt : Stmt.Function):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, LoxFunction.FunctionType.FUNCTION)
    
    def resolve_function(self, function, function_type : LoxFunction.FunctionType):
        enclosing_function = self.current_function
        self.current_function = function_type

        self.begin_scope()

        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.end_scope()

        self.current_function = enclosing_function

    
    def visit_return_stmt(self, stmt : Stmt.Return):
        if self.current_function == LoxFunction.FunctionType.NONE:
            lox.error(stmt.keyword, "Cannot return from top-level code.")

        if stmt.value != None:
            if self.current_function == LoxFunction.FunctionType.INITIALIZER:
                lox.error(stmt.keyword, "Cannot return a value from an initializer.")

            self.resolve(stmt.value)
    
    def visit_class_stmt(self, stmt : Stmt.Class):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass != None and stmt.name.lexeme == stmt.superclass.name.lexeme:
            lox.error(stmt.superclass.name, "A class cannot inherit from itself.")

        if stmt.superclass != None:
            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        
        if stmt.superclass != None:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = LoxFunction.FunctionType.METHOD
            
            if method.name.lexeme == "init":
                declaration = LoxFunction.FunctionType.INITIALIZER

            self.resolve_function(method, declaration)
        
        self.end_scope()

        if stmt.superclass != None:
            self.end_scope()

        self.current_class = enclosing_class

    def visit_this_expr(self, expr : Expr.This):
        if self.current_class == ClassType.NONE:
            lox.error(expr.keyword, "Cannot use 'this' outside of a class.")
            return
        self.resolve_local(expr, expr.keyword)
    
    def visit_set_expr(self, expr : Expr.Set):
        self.resolve(expr.value)
        self.resolve(expr._object)

    
    def visit_super_expr(self, expr : Expr.Super):

        if self.current_class == ClassType.NONE:
            lox.error(expr.keyword, "Cannot use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            lox.error(expr.keyword, "Cannot use 'super' in a class with no superclass.")
        
        self.resolve_local(expr, expr.keyword)
    
    def visit_call_expr(self, expr : Expr.Call):
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)
    
    def visit_get_expr(self, expr : Expr.Get):
        self.resolve(expr._object)

    def visit_grouping_expr(self, expr : Expr.Grouping):
        self.resolve(expr.expression)

    def visit_literal_expr(self, expr : Expr.Literal):
        pass

    def visit_unary_expr(self, expr : Expr.Unary):
        self.resolve(expr.right)

    def visit_variable_expr(self, expr : Expr.Variable):
        if len(self.scopes) > 0 and self.scopes[-1].get(expr.name.lexeme, None) == False:
            lox.error(expr.name, "Cannot read local variable in its own initializer.")
        
        self.resolve_local(expr, expr.name)
    
    def resolve_local(self, expr, name : Token.Token):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
