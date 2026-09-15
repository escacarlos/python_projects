class sorting:
    def bubbleSort(self, a):
        for i in range(len(a)):
            for j in range(0, len(a)-1-i):
                if(a[j]>a[j+1]):
                    a[j], a[j+1] = a[j+1], a[j]

    def selectionSort(self, a):
        for i in range(len(a)):
            minIndex=i
            for j in range(i+1, len(a)):
                if a[i]<a[minIndex]:
                    minIndex=j
            a[i], a[minIndex] = a[minIndex], a[i]

    def insertionSort(self, a):
        for i in range(1, len(a)):
            key=a[i]
            j=i-1
            while j>=0 and key<a[j]:
                a[j+1]=a[j]
                j-=1
            a[j+1]=key
    
    def mergeSort(self, a):
        if len(a)>1:
            r=len(a)//2
            L=a[:r]
            M=a[r:]

            self.mergeSort(L)
            self.mergeSort(M)

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

def printList(a):
    for i in range(len(a)):
        print(a[i], end= ", ")
    print()

if __name__ == '__main__':
    sort = sorting()
    arr=list()
    arr=[9,8,7,6,5,4,3,2,1,0]
    sort.mergeSort(arr)
    print(len(arr))
    printList(arr)
