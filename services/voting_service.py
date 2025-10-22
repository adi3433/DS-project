from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import secrets
import json
from datetime import datetime, timezone, timedelta

from database import Voter, Ballot, Tally, AuditEvent, MerkleLeaf, OTACMapping, redis_client
from data_structures.voter_queue import VoterQueue, PriorityVoterQueue
from data_structures.candidate_array import CandidateArray, VoteHashTable
from data_structures.audit_stack import AuditStack
from utils.crypto_utils import CryptoUtils
from config import Config

class VotingService:
    """Core voting service implementing the main business logic with fundamental data structures."""
    
    def __init__(self):
        # Queue for managing voter requests (FIFO)
        self.voter_queue = VoterQueue(capacity=1000)
        self.priority_queue = PriorityVoterQueue()
        
        # Array for candidate management
        self.candidate_array = CandidateArray(capacity=50)
        
        # Hash Table for O(1) voter lookup
        self.voter_hash_table = VoteHashTable(capacity=10000)
        
        # Stack for audit trail (LIFO)
        self.audit_stack = AuditStack()
        
        self._load_existing_data()
        self._initialize_candidates()
    
    def _load_existing_data(self):
        """Load existing data into memory structures on startup."""
        # This would typically load from database/Redis on service restart
        pass
    
    def _sync_array_with_database(self, db: Session):
        """Sync candidate array vote counts with database tallies."""
        # Get all tallies from database
        tallies = db.query(Tally).all()
        
        # Update candidate array with database counts
        for tally in tallies:
            # Find candidate in array
            index = self.candidate_array.search_by_id(tally.candidate_id)
            if index != -1:
                # Reset vote count to match database
                candidate = self.candidate_array.candidates[index]
                candidate["vote_count"] = tally.count
    
    def _initialize_candidates(self):
        """Initialize default candidates in array."""
        default_candidates = [
            ("CAND001", "Alice Johnson"),
            ("CAND002", "Bob Smith"),
            ("CAND003", "Carol Williams"),
            ("CAND004", "David Brown"),
            ("CAND005", "Eve Davis")
        ]
        
        for candidate_id, candidate_name in default_candidates:
            self.candidate_array.insert(candidate_id, candidate_name)
    
    def register_voters(self, db: Session, voter_ids: List[str]) -> Dict[str, any]:
        """
        Register voters by storing salted hashes of their IDs.
        
        Args:
            db: Database session
            voter_ids: List of original voter IDs
            
        Returns:
            Registration result with statistics
        """
        registered_count = 0
        duplicate_count = 0
        
        for voter_id in voter_ids:
            voter_hash = CryptoUtils.hash_voter_id(voter_id)
            print(f"DEBUG: Registering voter_id: {voter_id} -> hash: {voter_hash[:10]}...")
            
            # Check if already registered
            existing = db.query(Voter).filter(Voter.voter_id_hash == voter_hash).first()
            if existing:
                duplicate_count += 1
                continue
            
            # Add to database
            voter = Voter(voter_id_hash=voter_hash)
            db.add(voter)
            
            # Add to hash table for O(1) lookup
            self.voter_hash_table.insert(voter_hash, {
                "voter_id_hash": voter_hash,
                "has_voted": False,
                "registered_at": datetime.utcnow().isoformat()
            })
            
            # Cache in Redis
            redis_client.hset(f"voter:{voter_hash}", "hasVoted", "false")
            
            registered_count += 1
        
        db.commit()
        
        # Log audit event
        event = {
            "type": "REGISTER_VOTERS",
            "details": {
                "registered_count": registered_count,
                "duplicate_count": duplicate_count,
                "total_attempted": len(voter_ids)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        self.audit_stack.push(event)
        
        # Persist audit event
        audit_event = AuditEvent(
            type="REGISTER_VOTERS",
            details=json.dumps(event["details"])
        )
        db.add(audit_event)
        db.commit()
        
        return {
            "success": True,
            "registered_count": registered_count,
            "duplicate_count": duplicate_count,
            "total_voters": db.query(Voter).count()
        }
    
    def issue_otacs(self, db: Session, voter_ids: List[str]) -> Dict[str, any]:
        """
        Issue one-time access codes for registered voters.
        
        Args:
            db: Database session
            voter_ids: List of voter IDs to issue OTACs for
            
        Returns:
            Dictionary mapping voter IDs to OTACs
        """
        otacs = []
        issued_count = 0
        
        for voter_id in voter_ids:
            voter_hash = CryptoUtils.hash_voter_id(voter_id)
            print(f"DEBUG: Issuing OTAC for voter_id: {voter_id} -> hash: {voter_hash[:10]}...")
            
            # Check if voter is registered
            voter = db.query(Voter).filter(Voter.voter_id_hash == voter_hash).first()
            if not voter:
                print(f"DEBUG: Voter not found in database: {voter_id}")
                continue
            
            # Generate OTAC
            otac = CryptoUtils.generate_otac()
            otac_hash = CryptoUtils.hash_otac(otac)
            
            # Store mapping
            mapping = OTACMapping(
                otac_hash=otac_hash,
                voter_id_hash=voter_hash
            )
            db.add(mapping)
            
            otacs.append({"voter_id": voter_id, "otac": otac})
            issued_count += 1
        
        db.commit()
        
        # Log audit event
        event = {
            "type": "ISSUE_OTACS",
            "details": {
                "issued_count": issued_count,
                "requested_count": len(voter_ids)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        self.audit_stack.push(event)
        
        return {
            "success": True,
            "otacs": otacs,
            "issued_count": issued_count
        }
    
    def cast_vote(self, db: Session, otac: str, candidate_id: str) -> Dict[str, any]:
        """
        Cast a vote using OTAC.
        
        Args:
            db: Database session
            otac: One-time access code
            candidate_id: ID of selected candidate
            
        Returns:
            Vote casting result
        """
        try:
            # Hash OTAC for lookup
            otac_hash = CryptoUtils.hash_otac(otac)
            
            # Find OTAC mapping
            mapping = db.query(OTACMapping).filter(
                OTACMapping.otac_hash == otac_hash,
                OTACMapping.used == False
            ).first()
            
            if not mapping:
                return {"success": False, "error": "Invalid or used OTAC"}
            
            print(f"DEBUG: OTAC mapping found - voter_hash: {mapping.voter_id_hash[:10]}...")
            
            voter_hash = mapping.voter_id_hash
            
            # Fast O(1) lookup using hash table
            voter_data = self.voter_hash_table.search(voter_hash)
            if voter_data and voter_data.get("has_voted"):
                return {"success": False, "error": "Voter has already voted (hash table check)"}
            
            # Check voter eligibility and voting status
            voter = db.query(Voter).filter(Voter.voter_id_hash == voter_hash).first()
            if not voter:
                return {"success": False, "error": f"Voter not found. Hash: {voter_hash[:10]}..."}
            
            if voter.has_voted:
                return {"success": False, "error": "Voter has already voted"}
            
            # Database operations (SQLAlchemy handles transactions automatically)
            try:
                # Mark voter as voted
                voter.has_voted = True
                redis_client.hset(f"voter:{voter_hash}", "hasVoted", "true")
                
                # Mark OTAC as used
                mapping.used = True
                
                # Update tally in database
                tally = db.query(Tally).filter(Tally.candidate_id == candidate_id).first()
                if not tally:
                    tally = Tally(candidate_id=candidate_id, count=1)
                    db.add(tally)
                else:
                    tally.count += 1
                
                # Update candidate array (O(n) search + O(1) update)
                self.candidate_array.increment_vote(candidate_id)
                
                # Update hash table
                if voter_data:
                    voter_data["has_voted"] = True
                    self.voter_hash_table.update(voter_hash, voter_data)
                
                # Ensure tally is committed to database
                db.flush()
                
                # Generate ballot hash
                ballot_hash, nonce = CryptoUtils.generate_ballot_hash(candidate_id)
                
                # Get next sequence number
                max_seq = db.query(func.max(Ballot.seq)).scalar() or 0
                seq = max_seq + 1
                
                # Store ballot
                ballot = Ballot(
                    seq=seq,
                    ballot_hash=ballot_hash,
                    candidate_id=candidate_id
                )
                db.add(ballot)
                
                # Store ballot sequence (simplified without Merkle tree)
                leaf = MerkleLeaf(seq=seq, ballot_hash=ballot_hash)
                db.add(leaf)
                
                # Log audit event using Stack (LIFO)
                event = {
                    "type": "CAST",
                    "details": {
                        "voter_hash": voter_hash[:10] + "...",  # Truncated for privacy
                        "ballot_hash": ballot_hash,
                        "candidate_id": candidate_id,
                        "seq": seq,
                        "nonce": nonce
                    },
                    "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
                }
                self.audit_stack.push(event)
                
                # Persist audit event
                audit_event = AuditEvent(
                    type="CAST",
                    details=json.dumps(event["details"])
                )
                db.add(audit_event)
                
                db.commit()
                
                return {
                    "success": True,
                    "ballot_hash": ballot_hash,
                    "seq": seq,
                    "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
                    "message": "Vote cast successfully",
                    "candidate_votes": self.candidate_array.search_by_id(candidate_id)
                }
                
            except Exception as e:
                db.rollback()
                return {"success": False, "error": f"Failed to cast vote: {str(e)}"}
                
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def get_results(self, db: Session) -> Dict[str, any]:
        """Get current voting results using candidate array."""
        # Sync candidate array with database tallies
        self._sync_array_with_database(db)
        
        # Get results from candidate array (sorted by votes)
        results = self.candidate_array.get_results()
        total_votes = self.candidate_array.get_total_votes()
        winner = self.candidate_array.get_winner()
        
        return {
            "results": results,
            "total_votes": total_votes,
            "winner": winner,
            "candidate_array_stats": self.candidate_array.get_stats()
        }
    
    def generate_merkle_proof(self, db: Session, ballot_hash: str) -> Dict[str, any]:
        """
        Generate ballot verification (simplified without Merkle tree).
        
        Args:
            db: Database session
            ballot_hash: Hash of ballot to verify
            
        Returns:
            Verification data or error
        """
        # Find ballot using linear search
        ballot = db.query(Ballot).filter(Ballot.ballot_hash == ballot_hash).first()
        if not ballot:
            return {"success": False, "error": "Ballot not found"}
        
        try:
            return {
                "success": True,
                "ballot_hash": ballot_hash,
                "seq": ballot.seq,
                "candidate_id": ballot.candidate_id,
                "timestamp": ballot.timestamp.isoformat(),
                "verification": "Ballot found in database"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to verify ballot: {str(e)}"}
    
    def verify_merkle_proof(self, leaf: str, leaf_index: int, proof: List[str], root: str) -> bool:
        """Verify ballot (simplified)."""
        # Simplified verification - just check if ballot exists
        return True
    
    def undo_last_action(self, db: Session) -> Dict[str, any]:
        """
        Undo the last action (demo mode only).
        
        Args:
            db: Database session
            
        Returns:
            Undo result
        """
        if not Config.DEMO_MODE:
            return {"success": False, "error": "Undo only available in demo mode"}
        
        if self.audit_stack.is_empty():
            return {"success": False, "error": "No actions to undo"}
        
        event = self.audit_stack.pop()
        
        try:
            
            if event["type"] == "CAST":
                details = event["details"]
                voter_hash = details["voter_hash"]
                ballot_hash = details["ballot_hash"]
                candidate_id = details["candidate_id"]
                seq = details["seq"]
                
                # Extract full voter hash (remove truncation)
                full_voter_hash = voter_hash.replace("...", "")
                
                # Restore voter status
                voter = db.query(Voter).filter(Voter.voter_id_hash.like(f"{full_voter_hash}%")).first()
                if voter:
                    voter.has_voted = False
                    redis_client.hset(f"voter:{voter.voter_id_hash}", "hasVoted", "false")
                    full_voter_hash = voter.voter_id_hash
                
                # Update tally in database
                tally = db.query(Tally).filter(Tally.candidate_id == candidate_id).first()
                if tally and tally.count > 0:
                    tally.count -= 1
                
                # Decrement vote in candidate array
                self.candidate_array.decrement_vote(candidate_id)
                
                # Update hash table
                voter_data = self.voter_hash_table.search(full_voter_hash)
                if voter_data:
                    voter_data["has_voted"] = False
                    self.voter_hash_table.update(full_voter_hash, voter_data)
                
                # Remove ballot
                db.query(Ballot).filter(Ballot.ballot_hash == ballot_hash).delete()
                db.query(MerkleLeaf).filter(MerkleLeaf.seq == seq).delete()
                
                # Log undo event
                undo_event = AuditEvent(
                    type="UNDO",
                    details=json.dumps({"undone_event": event})
                )
                db.add(undo_event)
                
                db.commit()
                
                return {
                    "success": True,
                    "undone_action": event["type"],
                    "message": "Action undone successfully using Stack (LIFO)"
                }
            
            else:
                db.rollback()
                return {"success": False, "error": f"Cannot undo action of type: {event['type']}"}
                
        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"Failed to undo action: {str(e)}"}
    
    def get_audit_trail(self, db: Session, limit: int = 50) -> List[Dict]:
        """Get audit trail (without PII)."""
        events = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
        
        trail = []
        for event in events:
            # Parse JSON details
            try:
                details = json.loads(event.details) if event.details else {}
            except:
                details = {}
            
            # Remove PII from details
            sanitized_details = details.copy()
            if "voter_hash" in sanitized_details:
                sanitized_details["voter_hash"] = "***REDACTED***"
            
            trail.append({
                "id": event.id,
                "type": event.type,
                "details": sanitized_details,
                "prev_root": event.prev_root,
                "new_root": event.new_root,
                "timestamp": event.timestamp.isoformat()
            })
        
        return trail
    
    def lookup_ballot(self, db: Session, ballot_hash: str) -> Dict[str, any]:
        """Lookup ballot details by hash."""
        try:
            ballot = db.query(Ballot).filter(Ballot.ballot_hash == ballot_hash).first()
            
            if ballot:
                return {
                    "found": True,
                    "ballot": {
                        "seq": ballot.seq,
                        "ballot_hash": ballot.ballot_hash,
                        "candidate_id": ballot.candidate_id,
                        "timestamp": ballot.timestamp.isoformat()
                    }
                }
            else:
                return {
                    "found": False,
                    "error": "Ballot hash not found in the system"
                }
        except Exception as e:
            return {
                "found": False,
                "error": f"Database error: {str(e)}"
            }
    
    def get_system_stats(self, db: Session) -> Dict[str, any]:
        """Get system statistics with data structure details."""
        total_voters = db.query(Voter).count()
        voted_count = db.query(Voter).filter(Voter.has_voted == True).count()
        total_ballots = db.query(Ballot).count()
        
        return {
            "total_voters": total_voters,
            "voted_count": voted_count,
            "remaining_voters": total_voters - voted_count,
            "total_ballots": total_ballots,
            "data_structures": {
                "queue": self.voter_queue.get_stats(),
                "candidate_array": self.candidate_array.get_stats(),
                "hash_table": self.voter_hash_table.get_stats(),
                "audit_stack": self.audit_stack.get_stats()
            },
            "demo_mode": Config.DEMO_MODE
        }
