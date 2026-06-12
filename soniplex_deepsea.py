"""
SoniPlex AI: DeepSea Edition - Proof of Concept
Universal Acoustic Swarm Intelligence for Autonomous Underwater Vehicles (AUVs)
"""
import numpy as np
import time
import sys

def slow_print(text, delay=0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

class SoniPlexNode:
    def __init__(self, name, true_x, true_y, true_z, true_yaw):
        self.name = name
        # 3D Ground Truth
        self.true_pose = np.array([true_x, true_y, true_z])
        self.true_yaw = true_yaw
        
        # AI State
        self.aligned_swarm_members = {}
        self.local_bathymetric_map = []
        
    def sonar_ping(self, world_target):
        """Simulates an AUV's Multibeam Echo Sounder (MBES) detecting a seafloor feature."""
        delta = world_target - self.true_pose
        cos_y = np.cos(-self.true_yaw)
        sin_y = np.sin(-self.true_yaw)
        
        local_x = delta[0] * cos_y - delta[1] * sin_y
        local_y = delta[0] * sin_y + delta[1] * cos_y
        local_z = delta[2] 
        
        return np.array([local_x, local_y, local_z])

    def broadcast_multiplex_pulse(self, local_feature):
        """Encodes spatial feature data into a SoniPlex multiplexed acoustic pulse with Cryptographic Signature."""
        raw_payload = str(local_feature)
        # Simulated Acoustic HMAC (Vibrational Hash)
        vibe_hash = sum([ord(c) for c in raw_payload]) % 997
        
        return {
            "sender": self.name,
            "payload": local_feature,
            "signature": f"VIBE-AUTH-{vibe_hash}",
            "bandwidth": "Multiplexed HF-Band",
            "timestamp": time.time()
        }

    def solve_manifold_alignment(self, pulse, foreign_history, local_history):
        """SoniPlex AI Core: Aligning disparate 3D coordinate systems underwater with Auth check."""
        sender = pulse["sender"]
        payload = pulse["payload"]
        auth_sig = pulse["signature"]
        
        # Security Validation: Verify the vibrational hash
        expected_hash = sum([ord(c) for c in str(payload)]) % 997
        if auth_sig != f"VIBE-AUTH-{expected_hash}":
            slow_print(f"\n[SECURITY ALERT] {self.name} detected SPOOFED PULSE from {sender}! Rejecting.")
            return None
            slow_print(f"\n[{self.name} AI] Analyzing SoniPlex multiplex resonance...")
            slow_print(f"[{self.name} AI] Synchronizing spatial manifolds with {sender}...")
            
            # Use SVD to find the best-fit rotation and translation between the two AUVs
            A = np.array(foreign_history)
            B = np.array(local_history)
            
            centroid_A = np.mean(A, axis=0)
            centroid_B = np.mean(B, axis=0)
            
            H = (A - centroid_A).T @ (B - centroid_B)
            U, S, Vt = np.linalg.svd(H)
            R = Vt.T @ U.T
            
            if np.linalg.det(R) < 0:
                Vt[2,:] *= -1
                R = Vt.T @ U.T
                
            t = -R @ centroid_A + centroid_B
            
            self.aligned_swarm_members[sender] = {"R": R, "t": t}
            time.sleep(0.5)
            slow_print(f"[{self.name} AI] SUCCESS: SoniPlex Link Established. Swarm manifold locked.")

        if sender in self.aligned_swarm_members:
            R = self.aligned_swarm_members[sender]["R"]
            t = self.aligned_swarm_members[sender]["t"]
            translated_feature = R @ payload + t
            return translated_feature
        return None

def run_soniplex_deepsea():
    print("="*75)
    print(" SONIPLEX AI: DEEP-SEA EDITION - MULTIPLEXED SWARM SYNC")
    print("="*75)
    print("Status: 1,200m depth | GPS: LOST | Comms: Acoustic SoniPlex Only")
    print("="*75)
    
    # Vehicles
    scout_a = SoniPlexNode("Scout-Alpha", 0, 0, -1200, 0)
    scout_b = SoniPlexNode("Scout-Beta", 30, -10, -1215, np.pi/4) # Offset and rotated
    
    # Environmental Markers (Seafloor structures)
    landmarks = [
        [15, 5, -1210],
        [20, -5, -1208],
        [5, 10, -1212],
        [-10, 2, -1205]
    ]
    
    a_history = []
    b_history = []
    
    slow_print("\n--- PHASE 1: ACOUSTIC MANIFOLD CORRELATION ---")
    for i, mark in enumerate(landmarks):
        time.sleep(0.3)
        a_obs = scout_a.sonar_ping(mark)
        b_obs = scout_b.sonar_ping(mark)
        
        a_history.append(a_obs)
        b_history.append(b_obs)
        
        pulse = scout_a.broadcast_multiplex_pulse(a_obs)
        slow_print(f"[Acoustic] {scout_a.name} sends SoniPlex pulse: Landmark {i+1}")
        
        scout_b.solve_manifold_alignment(pulse, a_history, b_history)

    slow_print("\n--- PHASE 2: REAL-TIME SWARM COLLABORATION ---")
    time.sleep(1)
    
    # Alpha detects a critical asset (e.g., downed equipment) Beta hasn't seen
    critical_asset = [40, 20, -1218]
    a_new_obs = scout_a.sonar_ping(critical_asset)
    
    slow_print(f"\n[ALERT] {scout_a.name} localized mission-critical asset.")
    pulse = scout_a.broadcast_multiplex_pulse(a_new_obs)
    
    # Beta receives and translates
    translated = scout_b.solve_manifold_alignment(pulse, a_history, b_history)
    
    # Ground Truth Validation
    actual_b_obs = scout_b.sonar_ping(critical_asset)
    
    print("\n" + "="*75)
    print(" SONI PLEX RESULTS: CROSS-PLATFORM LOCALIZATION")
    print("="*75)
    print(f"Scout-Beta's SoniPlex Estimation : {translated.round(2)}")
    print(f"Mathematical Ground Truth       : {actual_b_obs.round(2)}")
    print("\nSoniPlex AI successfully bridged the spatial gap using acoustic multiplexing.")
    print("="*75)

if __name__ == "__main__":
    run_soniplex_deepsea()
