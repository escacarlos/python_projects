class Solution:
    def longestCommonPrefix(self, strs: list[str]) -> str:
        nWords = len(strs)
        min = []
        pattern = ""
        if nWords == 0:
            return pattern
        elif nWords == 1:
            return strs[0]
        else:
            shortest=len(strs[0])
            for i in range(1, nWords):
                if len(strs[i])<shortest:
                    shortest=len(strs[i])
            for i in range(1, nWords):
                k=0
                lw = list(strs[0])
                lo = list(strs[i])
                for j in range(0, shortest):
                    if lw[j]==lo[j]:
                        k+=1
                    else:
                        min.append(k)
                min.append(k)
            n=len(min)
            if n>0:
                newMin=min[0]
                for i in range(1, n):
                    if min[i]<newMin:
                        newMin=min[i]
                for i in range(0, newMin):
                    pattern+=lw[i]
            else:
                return pattern
            return pattern

if __name__=='__main__':
    sol=Solution()
    strs=["cir","car"]
    pattern = sol.longestCommonPrefix(strs)
    print(pattern)


        