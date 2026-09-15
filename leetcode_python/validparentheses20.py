class ArrayStack:
    def __init__(self):
        self._data = []
    
    def __len__(self):
        return len(self._data)
    
    def is_empty(self):
        return len(self._data) == 0
    
    def push(self, e):
        self._data.append(e)
    
    def top(self):
        if self.is_empty():
            raise Empty('Stack is empty')
        return self._data[-1]
    
    def pop(self):
        if self.is_empty():
            raise Empty('Stack is empty')
        return self._data.pop()

class Empty(Exception):
    pass

class Solution:
    def isValid(self, s: str) -> bool:
        lefty = '({['
        righty = ')}]'
        S = ArrayStack()
        for c in s:
            if c in lefty:
                S.push(c)
            elif c in righty:
                if S.is_empty():
                    return False
                if righty.index(c) != lefty.index(S.pop()):
                    return False
        return S.is_empty()

    def isValid2(self, s: str) -> bool:
        S = ArrayStack()
        for c in s:
            if c == '(' or c == '[' or c == '{':
                S.push(c)
            if c == ')' or c == ']' or c == '}':
                match c:
                    case ')':
                        if not S.is_empty() and S.top() == '(':
                            S.pop()
                        else:
                            S.push(c)                        
                    case ']':
                        if not S.is_empty() and S.top() == '[':
                            S.pop()
                        else:
                            S.push(c)                        
                    case '}':
                        if not S.is_empty() and S.top() == '{':
                            S.pop()
                        else:
                            S.push(c)
                        
        if S.is_empty():
            return True
        else:
            return False

if __name__ == '__main__':
    sol = Solution()
    str = "()"
    res = sol.isValid2(str)
    print(res)
                        