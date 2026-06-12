"""
SoniPlex AI: Surface Edition - Proof of Concept
Universal Acoustic Swarm Intelligence for Heterogeneous Land/Air Robots
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
    def __init__(self, name, true_x, true_y, true_theta):
        self.name = name
        self.true_pose = np.array([true_x, true_y])
        self.true_theta = true_theta
        self.aligned_nodes = {}
        self.local_map = []
        
    def sense_obstacle(self, world_obs):
        dx = world_obs[0] - self.true_pose[0]
        dy = world_obs[1] - self.true_pose[1]
        local_x = dx * np.cos(-self.true_theta) - dy * np.sin(-self.true_theta)
        local_y = dx * np.sin(-self.true_theta) + dy * np.cos(-self.true_theta)
        return np.array([local_x, local_y])

    def emit_multiplex_chirp(self, local_obs):
        return {
            "sender": self.name,
            "payload": local_obs,
            "signature": f"~[SONIPLEX-SURFACE] multiplex-id: {np.random.randint(100, 999)}~"
        }

    def process_ambient_multiplex(self, pulse, foreign_history, local_history):
        sender = pulse["sender"]
        payload = pulse["payload"]
        
        if sender not in self.aligned_nodes and len(local_history) >= 3:
            slow_print(f"\n[{self.name} AI] Synchronizing SoniPlex surface manifolds...")
            
            A = np.array(foreign_history)
            B = np.array(local_history)
            
            centroid_A = np.mean(A, axis=0)
            centroid_B = np.mean(B, axis=0)
            
            H = (A - centroid_A).T @ (B - centroid_B)
            U, S, Vt = np.linalg.svd(H)
            R = Vt.T @ U.T
            
            if np.linalg.det(R) < 0:
                Vt[1,:] *= -1
                R = Vt.T @ U.T
                
            t = -R @ centroid_A + centroid_B
            self.aligned_nodes[sender] = {"R": R, "t": t}
            time.sleep(0.5)
            slow_print(f"[{self.name} AI] SUCCESS: SoniPlex Surface Link established.")

        if sender in self.aligned_nodes:
            R = self.aligned_nodes[sender]["R"]
            t = self.aligned_nodes[sender]["t"]
            translated_obs = R @ payload + t
            return translated_obs
        return None

def run_soniplex_surface():
    print("="*65)
    print(" SONIPLEX AI: SURFACE EDITION - MULTIPLEXED SWARM SYNC")
    print("="*65)
    
    aerial_drone = SoniPlexNode("Aerial-Alpha", 0, 0, 0)
    ground_rover = SoniPlexNode("Rover-Beta", 10, 10, np.pi)
    
    world_landmarks = [[5, 5], [6, 2], [2, 8]]
    a_history, b_history = [], []
    
    slow_print("\n--- PHASE 1: MANIFOLD SYNCHRONIZATION ---")
    for i, obs in enumerate(world_landmarks):
        time.sleep(0.4)
        a_obs = aerial_drone.sense_obstacle(obs)
        b_obs = ground_rover.sense_obstacle(obs)
        a_history.append(a_obs)
        b_history.append(b_obs)
        
        pulse = aerial_drone.emit_multiplex_chirp(a_obs)
        slow_print(f"[Acoustic] {aerial_drone.name} pulses spatial data: {pulse['signature']}")
        ground_rover.process_ambient_multiplex(pulse, a_history, b_history)

    slow_print("\n--- PHASE 2: CROSS-PLATFORM INFERENCE ---")
    time.sleep(1)
    
    hidden_obstacle = [8, 9]
    a_new_obs = aerial_drone.sense_obstacle(hidden_obstacle)
    pulse = aerial_drone.emit_multiplex_chirp(a_new_obs)
    
    translated = ground_rover.process_ambient_multiplex(pulse, a_history, b_history)
    true_b_obs = ground_rover.sense_obstacle(hidden_obstacle)
    
    print("\n" + "="*65)
    print(" SONIPLEX RESULTS")
    print("="*65)
    print(f"Rover-Beta's SoniPlex Translation : {translated.round(2)}")
    print(f"Actual Physical Coordinate        : {true_b_obs.round(2)}")
    print("\nSoniPlex AI: Universal spatial coordination across land and air.")
    print("="*65)

if __name__ == '__main__':
    run_soniplex_surface()
