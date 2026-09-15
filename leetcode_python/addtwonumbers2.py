from typing import Optional

# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
    
    def append(self, val):
        new_node = ListNode(val)
        current_node = self

        while current_node.next is not None:
            next_node = current_node.next
            current_node = next_node
        
        current_node.next = new_node
    
    def print(self):
        current_node = self

        while current_node.next is not None:
            print(current_node.val)
            current_node = current_node.next
        
        print(current_node.val)


class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode()
        curr = dummy
        carry = 0
        
        while l1 or l2 or carry:
            v1 = l1.val if l1 else 0
            v2 = l2.val if l2 else 0
            
            # for example, 15 = 1, 5
            carry, val = divmod(v1 + v2 + carry, 10)
            curr.next = ListNode(val)
            
            # move to next digit
            curr = curr.next
            l1 = l1.next if l1 else None
            l2 = l2.next if l2 else None
        
        return dummy.next

if __name__=='__main__':
    l1 = ListNode(2)
    l1.append(6)
    l1.append(9)
    print("l1 list:")
    l1.print()

    l2 = ListNode(2)
    l2.append(6)
    l2.append(9)
    print("l2 list:")
    l2.print()
    
    sol = Solution()
    l3 = sol.addTwoNumbers(l1, l2)
    print("l3 list:")
    l3.print() 


