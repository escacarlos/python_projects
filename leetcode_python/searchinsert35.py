def searchInsert(nums, target):
    numsSize = len(nums)
    if target==nums[numsSize-1]:
        return numsSize-1
    elif target>nums[numsSize-1]:
        return numsSize
    for i in range(0, numsSize):
        if nums[i]==target:
            return i
        elif target>nums[i] and target<nums[i+1]:
            return i+1
    return 0

if __name__=='__main__':
    nums = [1, 3, 5, 7]
    res = searchInsert(nums, 5)
    print(res)