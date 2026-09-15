class Solution0(object):
    def isPalindrome(self, x):
        res=False
        entry = str(x)
        rev=entry[::-1]
        if entry==rev:
            res=True
        return res

class Solution:
    def isPalindrome(self, x: int) -> bool:
        res=False
        entry = str(x)
        rev=entry[::-1]
        if entry==rev:
            res=True
        return res

if __name__=='__main__':
    x = input("Enter a number")
    isPa = int(x)
    sol = Solution()
    res = sol.isPalindrome(isPa)
    if res:
        print("yes it is")
    else:
        print("no, it is not")