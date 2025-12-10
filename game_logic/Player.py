# match_code.py
from typing import List, Tuple, Any
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


        self.position: Tuple[Any, ...] = (0, 0)
        self.steps_taken: int = 0

        self.has_finished: bool = False
        self.start_time = None
        self.elapsed_time = timedelta(0)


        self.base_speed: float = 1.0
        self.speed_multiplier: float = 1.0


        self.is_frozen: bool = False
        self.is_stopped: bool = False


        self.active_power_ups: dict = {}

    def move(self, new_position: Tuple[Any, ...]):
        if self.is_frozen or self.is_stopped:
            return

        if not isinstance(new_position, tuple):
            raise TypeError("new_position must be a tuple (x,y) or (x,y,z)")

        if new_position != self.position:
            self.position = new_position
            self.steps_taken += 1

    def calculate_time(self):

        if self.start_time:
            self.elapsed_time = datetime.now() - self.start_time
            return self.elapsed_time
        return timedelta(0)

    def finish(self):

        self.has_finished = True
        if self.start_time:

            self.elapsed_time = datetime.now() - self.start_time


    def apply_power_up_effect(self, power_up: str, duration_seconds: int = 5):

        now = datetime.now()

        if power_up == PowerUpType.BOOST:

            self.speed_multiplier = 2.0
            expiry = now + timedelta(seconds=duration_seconds)
            self.active_power_ups[PowerUpType.BOOST] = expiry

        elif power_up == PowerUpType.FREEZE:
            self.is_frozen = True
            expiry = now + timedelta(seconds=duration_seconds)
            self.active_power_ups[PowerUpType.FREEZE] = expiry

        elif power_up == PowerUpType.STOP:
            self.is_stopped = True
            expiry = now + timedelta(seconds=duration_seconds)
            self.active_power_ups[PowerUpType.STOP] = expiry

        elif power_up == PowerUpType.SKIP:
            # SKIP considered instant/no-expiry effect; implement per-game logic
            # no expiry stored for SKIP
            pass

    def reset_power_up_effects(self):
        now = datetime.now()
  
        expired = [p for p, exp in list(self.active_power_ups.items()) if now >= exp]

        for p in expired:

            if p == PowerUpType.BOOST:
                self.speed_multiplier = 1.0
            elif p == PowerUpType.FREEZE:
                self.is_frozen = False
            elif p == PowerUpType.STOP:
                self.is_stopped = False

            try:
                del self.active_power_ups[p]
            except KeyError:
                pass

    def clear_all_powerups(self):

        self.active_power_ups.clear()
        self.speed_multiplier = 1.0
        self.is_frozen = False
        self.is_stopped = False


class MatchManager:
    def __init__(self, mode: str):
        self.current_mode = mode
        self.participants: List[Player] = []
        self.is_running: bool = False

    def add_player(self, player: Player):
        self.participants.append(player)

    def start_match(self):
        if len(self.participants) < 2:
            print("Error: Need at least 2 participants.")
            return

        self.is_running = True
        start_time = datetime.now()
        for p in self.participants:
            p.start_time = start_time
            p.has_finished = False
            p.steps_taken = 0
            p.elapsed_time = timedelta(0)

            p.clear_all_powerups()
        print(f"Match started ({self.current_mode}) with {len(self.participants)} participants.")

    def update_match_state(self):
        if not self.is_running:
            return

        for p in self.participants:
            p.calculate_time()
            p.reset_power_up_effects()

        self.check_for_winner()

    def check_for_winner(self):
        finished = [p for p in self.participants if p.has_finished]
        if finished:
            # choose smallest elapsed_time
            winner = min(finished, key=lambda x: x.elapsed_time)
            print(f"Match Finished! Winner is {winner.id} with time {winner.elapsed_time}")
            self.is_running = False

    def apply_power_up(self, power_up: str, target_player: Player, duration_seconds: int = 5):
        if target_player is None:
            return


        target_player.apply_power_up_effect(power_up, duration_seconds)
        print(f"Applied {power_up} to {target_player.id} for {duration_seconds}s")