class Solution:
    def sortArray(self, a: list[int]) -> list[int]:
        if len(a)>1:
            r=len(a)//2
            L=a[:r]
            M=a[r:]

            self.sortArray(L)
            self.sortArray(M)

            i=j=k=0

            while i<len(L) and j<len(M):
                if L[i]<M[j]:
                    a[k]=L[i]
                    i+=1
                else:
                    a[k]=M[j]
                    j+=1
                k+=1
            
            while i<len(L):
                a[k]=L[i]
                i+=1
                k+=1
            
            while j<len(M):
                a[k]=M[j]
                j+=1
                k+=1
        return a