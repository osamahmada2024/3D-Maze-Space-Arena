from typing import List
from datetime import datetime, timedelta

class GameMode:
    PLAYER_VS_AI = "PlayerVsAI"
    PLAYER_VS_PLAYER = "PlayerVsPlayer"

class PowerUpType:
    BOOST = "Boost"     
    FREEZE = "Freeze"   
    STOP = "Stop"      
    SKIP = "Skip"       

class Player:
    def __init__(self, player_id: str, is_ai: bool = False):
        self.id = player_id
        self.is_ai = is_ai
        self.position = (0, 0) 
        self.steps_taken = 0   
        self.has_finished = False
        self.start_time = None
        self.elapsed_time = timedelta(0)
        
        self.speed_multiplier = 1.0  
        self.is_frozen = False      
        self.is_stopped = False      
    def move(self, new_position):
        if not self.is_frozen and not self.is_stopped:
            self.position = new_position
            self.steps_taken += 1
            # if self.position == self.goal:
            #     self.has_finished = True
    
    def calculate_time(self):
        if self.start_time:
            self.elapsed_time = datetime.now() - self.start_time
            return self.elapsed_time
        return timedelta(0)


class MatchManager:
    def __init__(self, mode: str):
        self.current_mode = mode
        self.participants: List[Player] = []
        self.is_running = False

    def add_player(self, player: Player):
        self.participants.append(player)

    def start_match(self):
        if len(self.participants) < 2:
            print("Error: Need at least 2 participants.")
            return

        print(f"Starting match in mode: {self.current_mode}")
        self.is_running = True
        start_time = datetime.now()
        for player in self.participants:
            player.start_time = start_time
            player.has_finished = False
            player.steps_taken = 0

    def update_match_state(self):
        if not self.is_running:
            return

        for player in self.participants:
            player.calculate_time()
        
        self.check_for_winner()

    def check_for_winner(self):
        finished_players = [p for p in self.participants if p.has_finished]

        if finished_players:
            winner = min(finished_players, key=lambda p: p.elapsed_time)
            print(f"Match Finished! Winner is {winner.id} with time {winner.elapsed_time}")
            self.is_running = False

    def apply_power_up(self, power_up: str, target_player: Player, duration_seconds: int = 5):
        print(f"Applying {power_up} to {target_player.id}...")
        
        if power_up == PowerUpType.BOOST:
            target_player.speed_multiplier = 2.0   
        
        elif power_up == PowerUpType.FREEZE:
            target_player.is_frozen = True 

        elif power_up == PowerUpType.STOP:
            target_player.is_stopped = True  

        elif power_up == PowerUpType.SKIP:
            print(f"{target_player.id} can now skip a path obstacle.")