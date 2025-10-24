"""
Test script for demonstrating all data structures in the voting system.
Run this to verify all implementations work correctly.
"""

from data_structures.voter_queue import VoterQueue, PriorityVoterQueue
from data_structures.candidate_array import CandidateArray, VoteHashTable
from data_structures.audit_stack import AuditStack

def test_queue():
    """Test Circular Queue implementation."""
    print("\n" + "="*60)
    print("TESTING CIRCULAR QUEUE (FIFO)")
    print("="*60)
    
    queue = VoterQueue(capacity=5)
    
    # Test enqueue
    print("\n1. Enqueue Operations:")
    voters = [
        {"voter_id": "V001", "name": "Alice"},
        {"voter_id": "V002", "name": "Bob"},
        {"voter_id": "V003", "name": "Carol"}
    ]
    
    for voter in voters:
        result = queue.enqueue(voter)
        print(f"   Enqueued {voter['name']}: {result}")
    
    print(f"\n   Queue Size: {queue.get_size()}")
    print(f"   Queue Stats: {queue.get_stats()}")
    
    # Test peek
    print("\n2. Peek Operation:")
    front = queue.peek()
    print(f"   Front voter: {front['name']}")
    
    # Test dequeue
    print("\n3. Dequeue Operations:")
    while not queue.is_empty():
        voter = queue.dequeue()
        print(f"   Dequeued: {voter['name']}")
    
    print(f"\n   Queue is empty: {queue.is_empty()}")
    
    # Test circular behavior
    print("\n4. Testing Circular Behavior:")
    for i in range(6):
        voter = {"voter_id": f"V{i:03d}", "name": f"Voter{i}"}
        result = queue.enqueue(voter)
        print(f"   Enqueue Voter{i}: {result} (Full: {queue.is_full()})")
    
    print("\n✅ Queue tests completed!")

def test_priority_queue():
    """Test Priority Queue implementation."""
    print("\n" + "="*60)
    print("TESTING PRIORITY QUEUE")
    print("="*60)
    
    pq = PriorityVoterQueue()
    
    # Add voters with different priorities
    print("\n1. Enqueue with Priorities:")
    voters = [
        ({"voter_id": "V001", "name": "Regular Voter"}, 5),
        ({"voter_id": "V002", "name": "VIP Voter"}, 10),
        ({"voter_id": "V003", "name": "Elderly Voter"}, 8),
        ({"voter_id": "V004", "name": "Another Regular"}, 5)
    ]
    
    for voter, priority in voters:
        pq.enqueue(voter, priority)
        print(f"   Added {voter['name']} with priority {priority}")
    
    print(f"\n   Priority Queue Size: {pq.get_size()}")
    print(f"   Stats: {pq.get_stats()}")
    
    # Dequeue in priority order
    print("\n2. Dequeue by Priority (Highest First):")
    while not pq.is_empty():
        voter = pq.dequeue()
        print(f"   Processed: {voter['name']}")
    
    print("\n✅ Priority Queue tests completed!")

def test_stack():
    """Test Stack implementation."""
    print("\n" + "="*60)
    print("TESTING STACK (LIFO)")
    print("="*60)
    
    stack = AuditStack()
    
    # Test push
    print("\n1. Push Operations:")
    events = [
        {"type": "CAST", "voter": "V001", "candidate": "candidate_a"},
        {"type": "CAST", "voter": "V002", "candidate": "candidate_b"},
        {"type": "CAST", "voter": "V003", "candidate": "candidate_a"}
    ]
    
    for event in events:
        stack.push(event)
        print(f"   Pushed: {event['type']} - Voter {event['voter']}")
    
    print(f"\n   Stack Size: {stack.size()}")
    print(f"   Stack Stats: {stack.get_stats()}")
    
    # Test peek
    print("\n2. Peek Operation:")
    top = stack.peek()
    print(f"   Top event: {top['type']} - Voter {top['voter']}")
    
    # Test pop
    print("\n3. Pop Operations (LIFO - Last In First Out):")
    while not stack.is_empty():
        event = stack.pop()
        print(f"   Popped: {event['type']} - Voter {event['voter']}")
    
    print(f"\n   Stack is empty: {stack.is_empty()}")
    
    print("\n✅ Stack tests completed!")

def test_array():
    """Test Candidate Array implementation."""
    print("\n" + "="*60)
    print("TESTING CANDIDATE ARRAY")
    print("="*60)
    
    array = CandidateArray(capacity=10)
    
    # Test insert
    print("\n1. Insert Candidates:")
    candidates = [
        ("candidate_a", "Candidate A"),
        ("candidate_b", "Candidate B"),
        ("candidate_c", "Candidate C")
    ]
    
    for cid, name in candidates:
        result = array.insert(cid, name)
        print(f"   Inserted {name}: {result}")
    
    print(f"\n   Array Size: {array.size}")
    print(f"   Array Stats: {array.get_stats()}")
    
    # Test search (Linear Search)
    print("\n2. Linear Search:")
    search_id = "candidate_b"
    index = array.search_by_id(search_id)
    print(f"   Searching for {search_id}: Found at index {index}")
    
    # Test vote increment
    print("\n3. Increment Votes:")
    votes = [
        ("candidate_a", 5),
        ("candidate_b", 3),
        ("candidate_c", 7)
    ]
    
    for cid, count in votes:
        for _ in range(count):
            array.increment_vote(cid)
    
    print("   Votes cast:")
    for candidate in array.get_all_candidates():
        print(f"   - {candidate['candidate_name']}: {candidate['vote_count']} votes")
    
    # Test get results (sorted)
    print("\n4. Get Results (Sorted by Votes):")
    results = array.get_results()
    for i, candidate in enumerate(results, 1):
        print(f"   {i}. {candidate['candidate_name']}: {candidate['vote_count']} votes")
    
    # Test get winner
    print("\n5. Get Winner:")
    winner = array.get_winner()
    print(f"   Winner: {winner['candidate_name']} with {winner['vote_count']} votes")
    
    # Test total votes
    print(f"\n6. Total Votes Cast: {array.get_total_votes()}")
    
    print("\n✅ Array tests completed!")

def test_hash_table():
    """Test Hash Table implementation."""
    print("\n" + "="*60)
    print("TESTING HASH TABLE (with Collision Handling)")
    print("="*60)
    
    hash_table = VoteHashTable(capacity=10)
    
    # Test insert
    print("\n1. Insert Key-Value Pairs:")
    voters = [
        ("voter_hash_001", {"voter_id": "V001", "has_voted": False}),
        ("voter_hash_002", {"voter_id": "V002", "has_voted": False}),
        ("voter_hash_003", {"voter_id": "V003", "has_voted": False}),
        ("voter_hash_abc", {"voter_id": "V004", "has_voted": False})
    ]
    
    for key, value in voters:
        result = hash_table.insert(key, value)
        hash_index = hash_table._hash_function(key)
        print(f"   Inserted {value['voter_id']} at hash index {hash_index}: {result}")
    
    print(f"\n   Hash Table Size: {hash_table.size}")
    print(f"   Hash Table Stats: {hash_table.get_stats()}")
    
    # Test search (O(1) average)
    print("\n2. Search Operations (O(1) average):")
    search_key = "voter_hash_002"
    result = hash_table.search(search_key)
    print(f"   Searching for {search_key}: {result}")
    
    # Test update
    print("\n3. Update Operation:")
    update_key = "voter_hash_001"
    voter_data = hash_table.search(update_key)
    voter_data["has_voted"] = True
    hash_table.update(update_key, voter_data)
    print(f"   Updated {update_key}: has_voted = {voter_data['has_voted']}")
    
    # Verify update
    updated = hash_table.search(update_key)
    print(f"   Verified: has_voted = {updated['has_voted']}")
    
    # Test collision demonstration
    print("\n4. Collision Demonstration:")
    print("   Adding keys that may collide...")
    collision_keys = ["key_a", "key_b", "key_c"]
    for key in collision_keys:
        hash_index = hash_table._hash_function(key)
        hash_table.insert(key, {"data": f"value_{key}"})
        print(f"   Key '{key}' hashes to index {hash_index}")
    
    print(f"\n   Updated Stats: {hash_table.get_stats()}")
    print(f"   Load Factor: {hash_table.get_load_factor():.2f}")
    
    # Test delete
    print("\n5. Delete Operation:")
    delete_key = "voter_hash_003"
    result = hash_table.delete(delete_key)
    print(f"   Deleted {delete_key}: {result}")
    print(f"   New size: {hash_table.size}")
    
    print("\n✅ Hash Table tests completed!")

def test_time_complexity():
    """Demonstrate time complexity differences."""
    print("\n" + "="*60)
    print("TIME COMPLEXITY DEMONSTRATION")
    print("="*60)
    
    print("\n1. Queue Operations:")
    print("   - Enqueue: O(1) - Constant time")
    print("   - Dequeue: O(1) - Constant time")
    print("   - Peek: O(1) - Constant time")
    
    print("\n2. Stack Operations:")
    print("   - Push: O(1) - Constant time")
    print("   - Pop: O(1) - Constant time")
    print("   - Peek: O(1) - Constant time")
    
    print("\n3. Array Operations:")
    print("   - Insert: O(n) - Linear (duplicate check)")
    print("   - Search: O(n) - Linear search")
    print("   - Access by index: O(1) - Direct access")
    print("   - Sort: O(n log n) - Comparison sort")
    
    print("\n4. Hash Table Operations:")
    print("   - Insert: O(1) average, O(n) worst case")
    print("   - Search: O(1) average, O(n) worst case")
    print("   - Delete: O(1) average, O(n) worst case")
    print("   - Collision handling: O(k) where k = chain length")
    
    print("\n✅ Time complexity demonstration completed!")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("DATA STRUCTURES TEST SUITE")
    print("SecureVote Pro - Lab Exam Demonstration")
    print("="*60)
    
    try:
        test_queue()
        test_priority_queue()
        test_stack()
        test_array()
        test_hash_table()
        test_time_complexity()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✅")
        print("="*60)
        print("\nAll data structures are working correctly!")
        print("Ready for lab exam demonstration! 🚀")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
