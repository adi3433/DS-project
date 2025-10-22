"""
Candidate Array Implementation
Demonstrates array-based operations for candidate management and vote tallying
"""

class CandidateArray:
    """
    Fixed-size array for candidate management.
    Demonstrates fundamental array operations: insert, search, update, delete
    """
    
    def __init__(self, capacity=10):
        """
        Initialize fixed-size candidate array.
        
        Args:
            capacity: Maximum number of candidates
        """
        self.capacity = capacity
        self.array = [None] * capacity
        self.size = 0
    
    def is_empty(self) -> bool:
        """Check if array is empty. O(1)"""
        return self.size == 0
    
    def is_full(self) -> bool:
        """Check if array is full. O(1)"""
        return self.size == self.capacity
    
    def insert(self, candidate_id: str, candidate_name: str) -> bool:
        """
        Insert candidate at next available position.
        
        Args:
            candidate_id: Unique candidate identifier
            candidate_name: Candidate name
            
        Returns:
            True if successful, False if array is full
            
        Time Complexity: O(1) for insertion, O(n) for duplicate check
        """
        if self.is_full():
            return False
        
        # Check for duplicates
        if self.search_by_id(candidate_id) != -1:
            return False
        
        # Insert at next position
        self.array[self.size] = {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "vote_count": 0
        }
        self.size += 1
        return True
    
    def search_by_id(self, candidate_id: str) -> int:
        """
        Linear search for candidate by ID.
        
        Args:
            candidate_id: Candidate ID to search
            
        Returns:
            Index if found, -1 otherwise
            
        Time Complexity: O(n)
        """
        for i in range(self.size):
            if self.array[i] and self.array[i]["candidate_id"] == candidate_id:
                return i
        return -1
    
    def get_candidate(self, index: int) -> dict:
        """
        Get candidate at specific index.
        
        Args:
            index: Array index
            
        Returns:
            Candidate data or None
            
        Time Complexity: O(1)
        """
        if 0 <= index < self.size:
            return self.array[index]
        return None
    
    def increment_vote(self, candidate_id: str) -> bool:
        """
        Increment vote count for candidate.
        
        Args:
            candidate_id: Candidate ID
            
        Returns:
            True if successful, False if not found
            
        Time Complexity: O(n) for search + O(1) for update
        """
        index = self.search_by_id(candidate_id)
        if index == -1:
            return False
        
        self.array[index]["vote_count"] += 1
        return True
    
    def decrement_vote(self, candidate_id: str) -> bool:
        """
        Decrement vote count (for undo operations).
        
        Args:
            candidate_id: Candidate ID
            
        Returns:
            True if successful, False if not found
            
        Time Complexity: O(n)
        """
        index = self.search_by_id(candidate_id)
        if index == -1:
            return False
        
        if self.array[index]["vote_count"] > 0:
            self.array[index]["vote_count"] -= 1
        return True
    
    def get_all_candidates(self) -> list:
        """
        Get all candidates in array.
        
        Returns:
            List of candidate data
            
        Time Complexity: O(n)
        """
        return [self.array[i] for i in range(self.size)]
    
    def get_results(self) -> list:
        """
        Get voting results sorted by vote count.
        
        Returns:
            List of candidates sorted by votes (descending)
            
        Time Complexity: O(n log n) for sorting
        """
        candidates = self.get_all_candidates()
        # Bubble sort demonstration (can be replaced with built-in sort)
        return sorted(candidates, key=lambda x: x["vote_count"], reverse=True)
    
    def get_winner(self) -> dict:
        """
        Get candidate with most votes.
        
        Returns:
            Winning candidate or None
            
        Time Complexity: O(n)
        """
        if self.is_empty():
            return None
        
        max_votes = -1
        winner_index = -1
        
        for i in range(self.size):
            if self.array[i]["vote_count"] > max_votes:
                max_votes = self.array[i]["vote_count"]
                winner_index = i
        
        return self.array[winner_index] if winner_index != -1 else None
    
    def get_total_votes(self) -> int:
        """
        Calculate total votes cast.
        
        Returns:
            Total vote count
            
        Time Complexity: O(n)
        """
        total = 0
        for i in range(self.size):
            total += self.array[i]["vote_count"]
        return total
    
    def clear(self) -> None:
        """Clear all candidates. O(1)"""
        self.array = [None] * self.capacity
        self.size = 0
    
    def delete_candidate(self, candidate_id: str) -> bool:
        """
        Delete candidate by ID (shifts remaining elements).
        
        Args:
            candidate_id: Candidate ID to delete
            
        Returns:
            True if successful, False if not found
            
        Time Complexity: O(n)
        """
        index = self.search_by_id(candidate_id)
        if index == -1:
            return False
        
        # Shift elements left
        for i in range(index, self.size - 1):
            self.array[i] = self.array[i + 1]
        
        self.array[self.size - 1] = None
        self.size -= 1
        return True
    
    def get_stats(self) -> dict:
        """Get array statistics for lab demonstration."""
        return {
            "capacity": self.capacity,
            "current_size": self.size,
            "is_empty": self.is_empty(),
            "is_full": self.is_full(),
            "total_votes": self.get_total_votes(),
            "utilization_percent": (self.size / self.capacity) * 100
        }


class VoteHashTable:
    """
    Hash Table implementation for O(1) voter lookup.
    Demonstrates hashing with collision handling using chaining.
    """
    
    def __init__(self, capacity=100):
        """
        Initialize hash table with chaining.
        
        Args:
            capacity: Number of buckets
        """
        self.capacity = capacity
        self.table = [[] for _ in range(capacity)]
        self.size = 0
    
    def _hash_function(self, key: str) -> int:
        """
        Simple hash function using sum of ASCII values.
        
        Args:
            key: String key to hash
            
        Returns:
            Hash index
            
        Time Complexity: O(k) where k is key length
        """
        hash_value = 0
        for char in key:
            hash_value += ord(char)
        return hash_value % self.capacity
    
    def insert(self, key: str, value: dict) -> bool:
        """
        Insert key-value pair into hash table.
        
        Args:
            key: Voter ID hash
            value: Voter data
            
        Returns:
            True if inserted, False if key exists
            
        Time Complexity: O(1) average, O(n) worst case
        """
        index = self._hash_function(key)
        bucket = self.table[index]
        
        # Check if key already exists
        for item in bucket:
            if item["key"] == key:
                return False  # Duplicate
        
        # Insert new item
        bucket.append({"key": key, "value": value})
        self.size += 1
        return True
    
    def search(self, key: str) -> dict:
        """
        Search for value by key.
        
        Args:
            key: Key to search
            
        Returns:
            Value if found, None otherwise
            
        Time Complexity: O(1) average, O(n) worst case
        """
        index = self._hash_function(key)
        bucket = self.table[index]
        
        for item in bucket:
            if item["key"] == key:
                return item["value"]
        
        return None
    
    def update(self, key: str, value: dict) -> bool:
        """
        Update value for existing key.
        
        Args:
            key: Key to update
            value: New value
            
        Returns:
            True if updated, False if key not found
            
        Time Complexity: O(1) average
        """
        index = self._hash_function(key)
        bucket = self.table[index]
        
        for item in bucket:
            if item["key"] == key:
                item["value"] = value
                return True
        
        return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key-value pair.
        
        Args:
            key: Key to delete
            
        Returns:
            True if deleted, False if not found
            
        Time Complexity: O(1) average
        """
        index = self._hash_function(key)
        bucket = self.table[index]
        
        for i, item in enumerate(bucket):
            if item["key"] == key:
                bucket.pop(i)
                self.size -= 1
                return True
        
        return False
    
    def get_load_factor(self) -> float:
        """Calculate load factor (size / capacity)."""
        return self.size / self.capacity
    
    def get_stats(self) -> dict:
        """Get hash table statistics."""
        # Calculate collision statistics
        non_empty_buckets = sum(1 for bucket in self.table if len(bucket) > 0)
        max_chain_length = max(len(bucket) for bucket in self.table)
        
        return {
            "capacity": self.capacity,
            "size": self.size,
            "load_factor": self.get_load_factor(),
            "non_empty_buckets": non_empty_buckets,
            "max_chain_length": max_chain_length,
            "collision_rate": (self.size - non_empty_buckets) / self.size if self.size > 0 else 0
        }
