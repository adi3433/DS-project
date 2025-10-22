# Data Structures Lab Exam Guide 📚

## SecureVote Pro - Data Structures Implementation

This document explains all data structures used in the voting system for lab exam demonstration.

---

## 🎯 Data Structures Overview

### 1. **Queue (Circular Queue)** - `voter_queue.py`

#### Concept
FIFO (First In First Out) - First voter to request gets processed first.

#### Implementation Details
- **Type**: Circular Queue (array-based)
- **Capacity**: Fixed size (1000 voters)
- **Key Operations**:
  - `enqueue()` - Add voter to rear - **O(1)**
  - `dequeue()` - Remove voter from front - **O(1)**
  - `peek()` - View front voter - **O(1)**
  - `is_empty()` - Check if empty - **O(1)**
  - `is_full()` - Check if full - **O(1)**

#### Real-World Use Case
Managing voter requests in order of arrival for fair processing.

#### Code Example
```python
# Create queue
voter_queue = VoterQueue(capacity=100)

# Enqueue voters
voter_queue.enqueue({"voter_id": "V001", "name": "Alice"})
voter_queue.enqueue({"voter_id": "V002", "name": "Bob"})

# Dequeue (process first voter)
first_voter = voter_queue.dequeue()  # Returns Alice

# Peek (view next without removing)
next_voter = voter_queue.peek()  # Returns Bob
```

#### Why Circular?
- Efficient space utilization
- No need to shift elements
- Reuses empty spaces at the beginning

---

### 2. **Priority Queue** - `voter_queue.py`

#### Concept
Higher priority items are processed first (VIP voters, elderly, disabled).

#### Implementation Details
- **Type**: Array-based with sorted insertion
- **Key Operations**:
  - `enqueue(data, priority)` - Insert with priority - **O(n)**
  - `dequeue()` - Remove highest priority - **O(1)**

#### Code Example
```python
priority_queue = PriorityVoterQueue()

# Add voters with priority
priority_queue.enqueue({"voter_id": "V001"}, priority=5)  # Normal
priority_queue.enqueue({"voter_id": "V002"}, priority=10) # VIP

# Dequeue returns highest priority first
vip_voter = priority_queue.dequeue()  # Returns V002 (priority 10)
```

---

### 3. **Stack (Audit Stack)** - `audit_stack.py`

#### Concept
LIFO (Last In First Out) - Last operation can be undone first.

#### Implementation Details
- **Type**: Array-based stack
- **Key Operations**:
  - `push()` - Add event to top - **O(1)**
  - `pop()` - Remove event from top - **O(1)**
  - `peek()` - View top event - **O(1)**
  - `is_empty()` - Check if empty - **O(1)**

#### Real-World Use Case
- Audit trail tracking
- Undo operations (demo mode)
- Operation history

#### Code Example
```python
audit_stack = AuditStack()

# Push operations
audit_stack.push({"type": "CAST", "voter": "V001"})
audit_stack.push({"type": "CAST", "voter": "V002"})

# Pop (undo last operation)
last_operation = audit_stack.pop()  # Returns V002 operation

# Peek (view without removing)
current_top = audit_stack.peek()  # Returns V001 operation
```

#### Stack Applications
1. **Undo/Redo**: Reverse last action
2. **History Tracking**: Maintain operation sequence
3. **Backtracking**: Return to previous state

---

### 4. **Array (Candidate Array)** - `candidate_array.py`

#### Concept
Fixed-size contiguous memory storage for candidates.

#### Implementation Details
- **Type**: Fixed-size array
- **Capacity**: 50 candidates max
- **Key Operations**:
  - `insert()` - Add candidate - **O(n)** (duplicate check)
  - `search_by_id()` - Linear search - **O(n)**
  - `increment_vote()` - Update vote count - **O(n)**
  - `get_results()` - Sort by votes - **O(n log n)**
  - `get_winner()` - Find max votes - **O(n)**

#### Real-World Use Case
Managing fixed number of candidates with vote counting.

#### Code Example
```python
candidate_array = CandidateArray(capacity=10)

# Insert candidates
candidate_array.insert("CAND001", "Alice Johnson")
candidate_array.insert("CAND002", "Bob Smith")

# Search for candidate (Linear Search)
index = candidate_array.search_by_id("CAND001")  # Returns 0

# Increment vote
candidate_array.increment_vote("CAND001")

# Get winner
winner = candidate_array.get_winner()

# Get sorted results
results = candidate_array.get_results()  # Sorted by vote count
```

#### Array Operations Demonstrated
1. **Insertion**: Add at next position
2. **Linear Search**: Sequential scan O(n)
3. **Deletion**: Shift elements left
4. **Traversal**: Iterate through all elements
5. **Sorting**: Arrange by vote count

---

### 5. **Hash Table** - `candidate_array.py`

#### Concept
Key-value storage with O(1) average lookup using hash function.

#### Implementation Details
- **Type**: Hash table with chaining (collision handling)
- **Capacity**: 10,000 buckets
- **Hash Function**: Sum of ASCII values mod capacity
- **Collision Resolution**: Chaining (linked list per bucket)

#### Key Operations
- `insert()` - Add key-value pair - **O(1) average**
- `search()` - Find by key - **O(1) average**
- `update()` - Modify value - **O(1) average**
- `delete()` - Remove entry - **O(1) average**

#### Real-World Use Case
Fast voter lookup by ID hash (O(1) instead of O(n)).

#### Code Example
```python
hash_table = VoteHashTable(capacity=100)

# Insert voter
hash_table.insert("voter_hash_123", {
    "voter_id": "V001",
    "has_voted": False
})

# Search (O(1) average)
voter_data = hash_table.search("voter_hash_123")

# Update
voter_data["has_voted"] = True
hash_table.update("voter_hash_123", voter_data)

# Delete
hash_table.delete("voter_hash_123")
```

#### Hash Function Explained
```python
def _hash_function(self, key: str) -> int:
    hash_value = 0
    for char in key:
        hash_value += ord(char)  # Sum ASCII values
    return hash_value % self.capacity  # Mod to fit in array
```

#### Collision Handling
When two keys hash to same index:
- **Chaining**: Store multiple items in a list at that index
- **Load Factor**: size / capacity (optimal < 0.75)

---

## 📊 Time Complexity Comparison

| Operation | Queue | Stack | Array | Hash Table |
|-----------|-------|-------|-------|------------|
| Insert | O(1) | O(1) | O(n) | O(1) avg |
| Delete | O(1) | O(1) | O(n) | O(1) avg |
| Search | O(n) | O(n) | O(n) | O(1) avg |
| Access | O(1) | O(1) | O(1) | O(1) avg |

---

## 🎬 Lab Demonstration Flow

### Step 1: Initialize Data Structures
```python
# In voting_service.py __init__
self.voter_queue = VoterQueue(capacity=1000)
self.candidate_array = CandidateArray(capacity=50)
self.voter_hash_table = VoteHashTable(capacity=10000)
self.audit_stack = AuditStack()
```

### Step 2: Register Voters (Hash Table)
```python
# O(1) insertion into hash table
voter_hash = hash_voter_id("V001")
self.voter_hash_table.insert(voter_hash, {
    "has_voted": False,
    "registered_at": datetime.now()
})
```

### Step 3: Cast Vote (Multiple DS)
```python
# 1. Hash Table: O(1) voter lookup
voter_data = self.voter_hash_table.search(voter_hash)

# 2. Array: O(n) candidate search + O(1) update
self.candidate_array.increment_vote(candidate_id)

# 3. Stack: O(1) push audit event
self.audit_stack.push({"type": "CAST", "details": {...}})
```

### Step 4: Get Results (Array)
```python
# O(n log n) sorting
results = self.candidate_array.get_results()

# O(n) linear scan for winner
winner = self.candidate_array.get_winner()
```

### Step 5: Undo Operation (Stack)
```python
# O(1) pop from stack
last_event = self.audit_stack.pop()

# Reverse the operation
self.candidate_array.decrement_vote(candidate_id)
```

---

## 🔍 Key Concepts to Explain

### 1. **Why Queue for Voters?**
- Fair processing (FIFO)
- No voter gets priority unfairly
- Circular queue prevents wasted space

### 2. **Why Stack for Audit?**
- Natural undo mechanism (LIFO)
- Recent operations on top
- Easy to reverse last action

### 3. **Why Array for Candidates?**
- Fixed number of candidates
- Simple iteration for results
- Direct index access O(1)

### 4. **Why Hash Table for Voters?**
- Fast lookup O(1) vs O(n)
- Millions of voters need efficiency
- Collision handling demonstrates advanced concept

---

## 💡 Interview Questions & Answers

### Q1: Why use Circular Queue instead of Linear Queue?
**A:** Circular queue reuses empty spaces at the beginning after dequeue operations. Linear queue would waste space and require shifting elements.

### Q2: What happens when Hash Table has collisions?
**A:** We use chaining - each bucket stores a list of items. When collision occurs, we append to that bucket's list. Search becomes O(k) where k is chain length.

### Q3: Why is Array search O(n) but Hash Table O(1)?
**A:** Array requires checking each element sequentially. Hash Table computes index directly using hash function, jumping to exact location.

### Q4: When would Stack be better than Queue?
**A:** Stack is better for undo/redo, backtracking, parsing expressions. Queue is better for task scheduling, breadth-first search.

### Q5: What is Load Factor in Hash Table?
**A:** Load Factor = size / capacity. If > 0.75, too many collisions occur. Solution: resize and rehash all elements.

---

## 🧪 Testing Commands

```bash
# Run the application
python main.py

# Access admin dashboard
http://localhost:8000/admin

# View API documentation
http://localhost:8000/docs

# Check data structure stats
GET /api/stats
```

---

## 📈 Performance Analysis

### Space Complexity
- **Queue**: O(n) where n = capacity
- **Stack**: O(n) where n = max events
- **Array**: O(n) where n = capacity
- **Hash Table**: O(n + m) where n = items, m = capacity

### Best Use Cases
- **Queue**: Task scheduling, BFS, request handling
- **Stack**: DFS, undo/redo, expression evaluation
- **Array**: Fixed-size collections, direct access
- **Hash Table**: Fast lookups, caching, indexing

---

## 🎓 Lab Exam Tips

1. **Explain Time Complexity**: Always mention Big-O notation
2. **Draw Diagrams**: Visualize queue/stack operations
3. **Compare Alternatives**: Why this DS over others?
4. **Real-World Examples**: Connect to practical applications
5. **Handle Edge Cases**: Empty, full, collision scenarios

---

## 📝 Summary

This voting system demonstrates:
- ✅ **Queue** - Voter request management (FIFO)
- ✅ **Stack** - Audit trail and undo (LIFO)
- ✅ **Array** - Candidate storage and tallying
- ✅ **Hash Table** - Fast voter lookup with collision handling

All fundamental data structures with practical real-world application! 🚀
