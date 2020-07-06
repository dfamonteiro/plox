from typing import List, Any

import LoxCallable
import stmt
import environment

class LoxFunction(LoxCallable.LoxCallable):
    declaration : stmt.Function

    def __init__(self, declaration : stmt.Function):
        self.declaration = declaration

    def call(self, interpreter, arguments : List[Any]) -> Any:
        env = environment.Environment(interpreter._globals)

        for i, param in enumerate(self.declaration.params):
            env.define(param.lexeme, arguments[i])
        
        interpreter.execute_block(self.declaration.body, env)

    def arity(self) -> int:
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"