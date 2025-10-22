"""
Voter Queue Implementation using Circular Queue
Demonstrates FIFO (First In First Out) operations for voter request processing
"""

class VoterQueue:
    """
    Circular Queue implementation for managing voter requests.
    Demonstrates fundamental queue operations: enqueue, dequeue, peek
    Time Complexity: O(1) for all operations
    """
    
    def __init__(self, capacity=100):
        """
        Initialize circular queue with fixed capacity.
        
        Args:
            capacity: Maximum number of voters in queue
        """
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = -1
        self.size = 0
    
    def is_empty(self) -> bool:
        """Check if queue is empty. O(1)"""
        return self.size == 0
    
    def is_full(self) -> bool:
        """Check if queue is full. O(1)"""
        return self.size == self.capacity
    
    def enqueue(self, voter_data: dict) -> bool:
        """
        Add voter to queue (FIFO).
        
        Args:
            voter_data: Dictionary containing voter information
            
        Returns:
            True if successful, False if queue is full
            
        Time Complexity: O(1)
        """
        if self.is_full():
            return False
        
        # Circular increment
        self.rear = (self.rear + 1) % self.capacity
        self.queue[self.rear] = voter_data
        self.size += 1
        return True
    
    def dequeue(self) -> dict:
        """
        Remove and return voter from front of queue.
        
        Returns:
            Voter data or None if queue is empty
            
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        
        voter_data = self.queue[self.front]
        self.queue[self.front] = None  # Clear reference
        
        # Circular increment
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        
        return voter_data
    
    def peek(self) -> dict:
        """
        View front voter without removing.
        
        Returns:
            Voter data or None if queue is empty
            
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.queue[self.front]
    
    def get_size(self) -> int:
        """Get current queue size. O(1)"""
        return self.size
    
    def get_all_voters(self) -> list:
        """
        Get all voters in queue (for display purposes).
        
        Returns:
            List of voter data in FIFO order
            
        Time Complexity: O(n)
        """
        if self.is_empty():
            return []
        
        voters = []
        index = self.front
        for _ in range(self.size):
            voters.append(self.queue[index])
            index = (index + 1) % self.capacity
        
        return voters
    
    def clear(self) -> None:
        """Clear all voters from queue. O(1)"""
        self.queue = [None] * self.capacity
        self.front = 0
        self.rear = -1
        self.size = 0
    
    def get_stats(self) -> dict:
        """Get queue statistics for lab demonstration."""
        return {
            "capacity": self.capacity,
            "current_size": self.size,
            "is_empty": self.is_empty(),
            "is_full": self.is_full(),
            "utilization_percent": (self.size / self.capacity) * 100,
            "front_index": self.front,
            "rear_index": self.rear
        }


class PriorityVoterQueue:
    """
    Priority Queue for VIP voter processing.
    Higher priority voters are processed first.
    """
    
    def __init__(self):
        """Initialize priority queue using list."""
        self.queue = []
    
    def enqueue(self, voter_data: dict, priority: int = 0):
        """
        Add voter with priority.
        
        Args:
            voter_data: Voter information
            priority: Priority level (higher = more important)
            
        Time Complexity: O(n) for insertion in sorted position
        """
        item = {"data": voter_data, "priority": priority}
        
        # Insert in sorted order (higher priority first)
        inserted = False
        for i in range(len(self.queue)):
            if priority > self.queue[i]["priority"]:
                self.queue.insert(i, item)
                inserted = True
                break
        
        if not inserted:
            self.queue.append(item)
    
    def dequeue(self) -> dict:
        """
        Remove and return highest priority voter.
        
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.queue.pop(0)["data"]
    
    def peek(self) -> dict:
        """View highest priority voter. O(1)"""
        if self.is_empty():
            return None
        return self.queue[0]["data"]
    
    def is_empty(self) -> bool:
        """Check if queue is empty. O(1)"""
        return len(self.queue) == 0
    
    def get_size(self) -> int:
        """Get queue size. O(1)"""
        return len(self.queue)
    
    def get_stats(self) -> dict:
        """Get priority queue statistics."""
        priorities = [item["priority"] for item in self.queue]
        return {
            "size": len(self.queue),
            "is_empty": self.is_empty(),
            "priorities": priorities,
            "highest_priority": max(priorities) if priorities else None,
            "lowest_priority": min(priorities) if priorities else None
        }
