
SEP = '\\'

class Path:
    def __init__(self, path):
        if not hasattr(path, '__str__'):
            raise TypeError('path must be able to be cast to a string')
        path = str(path)
        if not path.isascii():
            raise ValueError('path contains non-ASCII characters')
        self.parts = path.split(SEP)


    def __div__(self, other):
        if isinstance(other, Path):
            self.parts += other.parts
            return self
        if not hasattr(other, '__str__'):
            raise TypeError(f'expected str or Path object, not {type(other).__name__}')
        other = str(other)
        if not other.isascii():
            raise ValueError(f'string "{other}" contains non-ASCII characters')
        self.parts += other.split(SEP)
        return self
        
    
    def __rtruediv__(self, other):
        if not hasattr(other, '__str__'):
            raise TypeError(f'expected str or Path object, not {type(other).__name__}')
        other = str(other)
        if not other.isascii():
            raise ValueError(f'string "{other}" contains non-ASCII characters')
        self.parts = other.split(SEP) + self.parts
        return self

    def __str__(self):
        return SEP + SEP.join(self.parts)