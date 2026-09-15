class Solution():
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        n = len(nums)
        i: int = 0
        res: list[int] = []
        while i < (n - 1):
            for j in range(i + 1, n):
                if nums[i] + nums[j] == target:
                    res.append(i)
                    res.append(j)
                    return res
            i += 1
        return res

if __name__ == '__main__':
        nums = [3,3]
        target = 6
        sol = Solution()
        res = sol.twoSum(nums, target)
        print(res)