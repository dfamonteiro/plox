
class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
    
    def __str__(self) -> str:
        return self.klass.name + " instance"