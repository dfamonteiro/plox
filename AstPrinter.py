import Expr
import Token

class AstPrinter(Expr.ExprVisitor):
    def print_ast(self, expression : Expr.Expr):
        return expression.accept(self)
    
    def visit_binary_expr(self, expr : Expr.Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    def visit_grouping_expr(self, expr : Expr.Grouping):
        return self.parenthesize("group", expr.expression)
    def visit_literal_expr(self, expr : Expr.Literal):
        return str(expr.value) if expr.value != None else "nil"
    def visit_unary_expr(self, expr : Expr.Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name : str, *expressions):
        res = "(" + name

        for expression in expressions:
            res += " " + expression.accept(self)
        
        res += ")"

        return res
    
if __name__ == "__main__":
    expression = Expr.Binary(
        Expr.Unary(
            Token.Token(Token.TokenType.MINUS, "-", None, 1),
            Expr.Literal(123)
        ),
        Token.Token(Token.TokenType.STAR, "*", None, 1),
        Expr.Grouping(
            Expr.Literal(45.67)
        )
    )

    print(AstPrinter().print_ast(expression))