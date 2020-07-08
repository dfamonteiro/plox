from typing import List, Any

import LoxCallable
import LoxInstance

class LoxClass(LoxCallable.LoxCallable):
    name : str

    def __init__(self, name):
        self.name = name
    
    def __str__(self) -> str:
        return self.name
    
    def call(self, interpreter, arguments : List[Any]) -> Any:
        instance = LoxInstance.LoxInstance(self)
        return instance

    def arity(self) -> int:
        return 0
