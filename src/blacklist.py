class blacklist_meta(type):
    # allow contains statically
    def __contains__(self, line):
        return blacklist.__contains__(line)
    
    def __and__(self, line):
        return blacklist.__and__(line)

class blacklist(metaclass=blacklist_meta):
    badwords = []

    @classmethod
    def load(cls, path, replace=False):
        with open(path) as file:
            if replace:
                cls.badwords.clear()
                
            cls.badwords.extend(file.read().lower().split('\n'))

    @classmethod
    def __contains__(cls, line):
        return any(word in line 
                   for word in cls.badwords)

    @classmethod
    def intersect(cls, line):
        return [idx + 1
                for idx, word in enumerate(cls.badwords) 
                if word in line]
    
    __and__ = intersect