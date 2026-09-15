from typing import List
class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        length: int = len(nums)
        k = length
        i: int = 0
        for iter in range(length):
            iter -= i
            if nums[iter] == val and iter < k:
                k -= 1
                if iter < k:
                    for j in range(iter, k):
                        nums[j], nums[j + 1] = nums[j + 1], nums[j]
                    i += 1
                else:
                    i += 0
        return k

class Solution1:
    def removeElement(self, nums: List[int], val: int) -> int:
        n=len(nums)
        i=0
        while(i<n):
            if nums[i]==val:
                for j in range(i, n-1):
                    nums[j]=nums[j+1]
                n-=1
                i-=1
            i+=1
        return n
    
if __name__ == '__main__':
    Sol = Solution1()
    nums = [2,2,2]
    val = 2
    res = Sol.removeElement(nums, val)
    print(nums)
    print(res)
