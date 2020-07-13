from typing import List

import Token
import Expr
import lox
import Stmt

class ParseError(Exception):
    pass

class Parser:
    tokens : List[Token.Token]
    current : int

    def __init__(self, tokens : List[Token.Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        
        return statements

    def declaration(self) -> Stmt.Stmt:
        try:
            if self.match(Token.TokenType.CLASS):
                return self.class_declaration()
            elif self.match(Token.TokenType.FUN):
                return self.function("function")
            elif self.match(Token.TokenType.VAR):
                return self.var_declaration()
            else:
                return self.statement()
        except ParseError:
            self.synchronize()
            return None
        
    
    def class_declaration(self) -> Stmt.Stmt:
        name = self.consume(Token.TokenType.IDENTIFIER, "Expect class name.")
        
        superclass = None
        
        if self.match(Token.TokenType.LESS):
            self.consume(Token.TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Expr.Variable(self.previous())
        
        self.consume(Token.TokenType.LEFT_BRACE, "Expect '{' before class body.")
        
        methods = []

        while not self.check(Token.TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        
        self.consume(Token.TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return Stmt.Class(name, superclass, methods)
    
    def function(self, kind : str) -> Stmt.Function:
        name = self.consume(Token.TokenType.IDENTIFIER, f"Expect {kind} name.")
        parameters = []

        self.consume(Token.TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        if not self.check(Token.TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 parameters.")
                
                parameters.append(self.consume(Token.TokenType.IDENTIFIER, "Expect parameter name."))

                if not self.match(Token.TokenType.COMMA):
                    break
        
        self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self.consume(Token.TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()

        return Stmt.Function(name, parameters, body)

    def var_declaration(self) -> Stmt.Stmt:
        name = self.consume(Token.TokenType.IDENTIFIER, "Expect variable name.")
        
        initializer = None
        if self.match(Token.TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)
    
    def statement(self) -> Stmt.Stmt:
        if self.match(Token.TokenType.FOR):
            return self.for_statement()

        if self.match(Token.TokenType.IF):
            return self.if_statement()

        if self.match(Token.TokenType.PRINT):
            return self.print_statement()

        if self.match(Token.TokenType.RETURN):
            return self.return_statement()

        if self.match(Token.TokenType.WHILE):
            return self.while_statement()
        
        if self.match(Token.TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expression_statement()

    def return_statement(self) -> Stmt.Stmt:
        keyword = self.previous()
        value = None

        if not self.check(Token.TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after return value.")
        return Stmt.Return(keyword, value)

    def for_statement(self) -> Stmt.Stmt:
        self.consume(Token.TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None
        if self.match(Token.TokenType.SEMICOLON):
            initializer = None
        elif self.match(Token.TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        
        condition = None
        if not self.check(Token.TokenType.SEMICOLON):
            condition = self.expression()
        
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(Token.TokenType.RIGHT_PAREN):
            increment = self.expression()
        
        self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        if increment != None:
            body = Stmt.Block([body, Stmt.Expression(increment)])
        
        if condition == None:
            condition = Expr.Literal(True)
        
        body = Stmt.While(condition, body)

        if initializer != None:
            body = Stmt.Block([initializer, body])

        return body



    def while_statement(self) -> Stmt.Stmt:
        self.consume(Token.TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()

        return Stmt.While(condition, body)

    def if_statement(self) -> Stmt.Stmt:
        self.consume(Token.TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None

        if self.match(Token.TokenType.ELSE):
            else_branch = self.statement()
        
        return Stmt.If(condition, then_branch, else_branch)

    def block(self) -> List[Stmt.Stmt]:
        statements = []

        while not self.check(Token.TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(Token.TokenType.RIGHT_BRACE, "Expect '}' after block.")

        return statements

    def print_statement(self) -> Stmt.Stmt:
        value = self.expression()
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)
    
    def expression_statement(self) -> Stmt.Stmt:
        expr = self.expression()
        self.consume(Token.TokenType.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)
    
    def assignment(self) -> Expr.Expr:
        expression = self._or()

        if self.match(Token.TokenType.EQUAL):
            equals = self.previous()
            value  = self.assignment()

            if type(expression) == Expr.Variable:
                name = expression.name
                return Expr.Assign(name, value)
            elif type(expression) == Expr.Get:
                get = expression
                return Expr.Set(get._object, get.name, value)
            else:
                self.error(equals, "Invalid assignment target")
        
        return expression

    def _or(self) -> Expr.Expr:
        expression = self._and()

        while self.match(Token.TokenType.OR):
            operator = self.previous()
            right = self._and()
            expression = Expr.Logical(expression, operator, right)

        return expression
    
    def _and(self) -> Expr.Expr:
        expression = self.equality()

        while self.match(Token.TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expression = Expr.Logical(expression, operator, right)

        return expression

    def expression(self) -> Expr.Expr:
        return self.assignment()
    
    def equality(self) -> Expr.Expr:
        expression = self.comparison()

        while self.match(Token.TokenType.BANG_EQUAL, Token.TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expression = Expr.Binary(expression, operator, right)
        
        return expression
    
    def match(self, *types) -> bool:
        for _type in types:
            if self.check(_type):
                self.advance()
                return True
        else:
            return False
        
    def check(self, _type : Token.TokenType) -> True:
        if self.is_at_end():
            return False
        return self.peek().token_type == _type
    
    def advance(self) -> Token.Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().token_type == Token.TokenType.EOF
    
    def peek(self) -> Token.Token:
        return self.tokens[self.current]

    def previous(self) -> Token.Token:
        return self.tokens[self.current - 1]
    
    def comparison(self) -> Expr.Expr:
        expression = self.addition()
        while self.match(Token.TokenType.GREATER, 
                         Token.TokenType.GREATER_EQUAL,
                         Token.TokenType.LESS,
                         Token.TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.addition()
            expression = Expr.Binary(expression, operator, right)
        
        return expression

    
    def addition(self) -> Expr.Expr:
        expression = self.multiplication()
        while self.match(Token.TokenType.MINUS, Token.TokenType.PLUS):
            operator = self.previous()
            right = self.multiplication()
            expression = Expr.Binary(expression, operator, right)
        
        return expression
    
    def multiplication(self) -> Expr.Expr:
        expression = self.unary()
        while self.match(Token.TokenType.SLASH, Token.TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expression = Expr.Binary(expression, operator, right)
        
        return expression
    
    def unary(self) -> Expr.Expr:
        if self.match(Token.TokenType.BANG, Token.TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)
        else:
            return self.call()
    
    def call(self) -> Expr.Expr:
        expression = self.primary()

        while True:
            if self.match(Token.TokenType.LEFT_PAREN):
                expression = self.finish_call(expression)
            elif self.match(Token.TokenType.DOT):
                name = self.consume(Token.TokenType.IDENTIFIER, "Expect property name after '.'.")
                expression = Expr.Get(expression, name)
            else:
                break
        
        return expression
    
    def finish_call(self, callee : Expr.Expr) -> Expr.Expr:
        arguments = []
        if not self.check(Token.TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 arguments.")

                arguments.append(self.expression())
                
                if not self.match(Token.TokenType.COMMA):
                    break
        
        paren = self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Expr.Call(callee, paren, arguments)

    
    def primary(self) -> Expr.Expr:
        if self.match(Token.TokenType.FALSE):
            return Expr.Literal(False)
        if self.match(Token.TokenType.TRUE):
            return Expr.Literal(True)
        if self.match(Token.TokenType.NIL):
            return Expr.Literal(None)
        
        if self.match(Token.TokenType.NUMBER, Token.TokenType.STRING):
            return Expr.Literal(self.previous().literal)
        
        if self.match(Token.TokenType.SUPER):
            keyword = self.previous()

            self.consume(Token.TokenType.DOT, "Expect '.' after 'super'.")
            method = self.consume(Token.TokenType.IDENTIFIER, "Expect superclass method name.")
            return Expr.Super(keyword, method)

        if self.match(Token.TokenType.THIS):
            return Expr.This(self.previous())

        if (self.match(Token.TokenType.IDENTIFIER)):
            return Expr.Variable(self.previous())
        
        if self.match(Token.TokenType.LEFT_PAREN):
            expression = self.expression()
            self.consume(Token.TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expression)
        
        raise self.error(self.peek(), "Expect expression.")
        
    def consume(self, _type : Token.TokenType, message : str) -> Token.Token:
        if self.check(_type):
            return self.advance()
        else:
            raise self.error(self.peek(), message)

    def error(self, _token : Token.Token, message : str) -> ParseError:
        lox.error(_token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == Token.TokenType.SEMICOLON:
                return
            
            if self.peek().token_type in (
                Token.TokenType.CLASS,
                Token.TokenType.FUN,
                Token.TokenType.VAR,
                Token.TokenType.FOR,
                Token.TokenType.IF,
                Token.TokenType.WHILE,
                Token.TokenType.PRINT,
                Token.TokenType.RETURN
            ):
                return
            
            self.advance()