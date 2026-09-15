class Solution:
    def romanToInt(self, s: str) -> int:
        roman = dict()
        roman = {"I":1, "V":5, "X":10, "L":50, "C":100, "D":500, "M":1000}
        entry = list(s)
        n = len(entry)
        integer = 0
        for i in range(0, n):
            if i < n-1:
                if entry[i]=="I" and (entry[i+1]=="V" or entry[i+1]=="X"):
                    roman["I"]=-1
                if entry[i]=="X" and (entry[i+1]=="L" or entry[i+1]=="C"):
                    roman["X"]=-10
                if entry[i]=="C" and (entry[i+1]=="D" or entry[i+1]=="M"):
                    roman["C"]=-100
            integer = integer + roman[entry[i]]
            roman["I"]=1
            roman["X"]=10
            roman["C"]=100
        return integer

if __name__=='__main__':
    str ="MCMXCIV"
    sol = Solution()
    res = sol.romanToInt(str)
    print(res) 