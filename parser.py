from typing import List

from token import Token, TokenType
import expr
import lox

class ParseError(Exception):
    pass

class Parser:
    tokens : List[Token]
    current : int

    def __init__(self, tokens : List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def expression(self) -> expr.Expr:
        return self.equality()
    
    def equality(self) -> expr.Expr:
        expression = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expression = expr.Binary(expression, operator, right)
        
        return expression
    
    def match(self, *types) -> bool:
        for _type in types:
            if self.check(_type):
                self.advance()
                return True
        else:
            return False
        
    def check(self, _type : TokenType) -> True:
        if self.is_at_end():
            return False
        return self.peek().token_type == _type
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current]
    
    def comparison(self) -> expr.Expr:
        expression = self.addition()
        while self.match(TokenType.GREATER, 
                         TokenType.GREATER_EQUAL,
                         TokenType.LESS,
                         TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.addition()
            expression = expr.Binary(expression, operator, right)
        
        return expression

    
    def addition(self) -> expr.Expr:
        expression = self.multiplication()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.multiplication()
            expression = expr.Binary(expression, operator, right)
        
        return expression
    
    def multiplication(self) -> expr.Expr:
        expression = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expression = expr.Binary(expression, operator, right)
        
        return expression
    
    def unary(self) -> expr.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator, right)
        else:
            return self.primary()
    
    def primary(self) -> expr.Expr:
        if self.match(TokenType.FALSE):
            return expr.Literal(False)
        if self.match(TokenType.TRUE):
            return expr.Literal(True)
        if self.match(TokenType.NIL):
            return expr.Literal(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expr.Literal(self.previous().literal)
        
        if self.match(TokenType.LEFT_PAREN):
            expression = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(expression)
        
    def consume(self, _type : TokenType, message : str) -> Token:
        if self.check(_type):
            return self.advance()
        else:
            raise self.error(self.peek(), message)

    def error(self, token : Token, message : str) -> ParseError:
        lox.error(token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return
            
            if self.peek().token_type in (
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN
            ):
                return
            
            self.advance()