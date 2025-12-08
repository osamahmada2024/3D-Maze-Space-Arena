import random
from enum import Enum
from typing import List, Tuple, Optional, Dict
import time

class EffectType(Enum):
    STOP_TWO_ROUNDS = "stop_two_rounds"
    BOOST = "boost"
    SKIP = "skip"
    FREEZE = "freeze"

class LuckyBlock:
    def __init__(self, position: Tuple[float, float, float], block_id: int):
        self.position = position
        self.block_id = block_id
        self.is_collected = False
        self.effect = None
        self.glow_color = (1.0, 0.8, 0.0)
        self.particle_effect = "lucky_sparkle"
        self.rotation_speed = 45
        self.scale_animation = True
        
    def collect(self) -> EffectType:
        if self.is_collected:
            return None
        self.is_collected = True
        self.effect = random.choice(list(EffectType))
        return self.effect
    
    def get_visual_data(self) -> Dict:
        return {
            'position': self.position,
            'glow_color': self.glow_color,
            'particle_effect': self.particle_effect,
            'rotation_speed': self.rotation_speed,
            'scale_animation': self.scale_animation,
            'is_collected': self.is_collected
        }

class TeleportPoint:
    def __init__(self, position: Tuple[float, float, float], teleport_id: int):
        self.position = position
        self.teleport_id = teleport_id
        self.is_active = True
        self.glow_color = (0.0, 0.8, 1.0)
        self.particle_effect = "teleport_portal"
        self.animation_type = "smooth_pulse"
        self.sound_effect = "teleport_whoosh"
        
    def get_visual_data(self) -> Dict:
        return {
            'position': self.position,
            'glow_color': self.glow_color,
            'particle_effect': self.particle_effect,
            'animation_type': self.animation_type,
            'is_active': self.is_active
        }

class ActiveEffect:
    def __init__(self, effect_type: EffectType, target_id: str, duration: int = 0):
        self.effect_type = effect_type
        self.target_id = target_id
        self.duration = duration
        self.remaining_rounds = duration
        
    def update_round(self) -> bool:
        if self.remaining_rounds > 0:
            self.remaining_rounds -= 1
        return self.remaining_rounds > 0 or self.duration == 0

class LuckyBlockTeleportSystem:
    def __init__(self, maze_bounds: Tuple[float, float, float, float], 
                 num_lucky_blocks: int = 8, num_teleports: int = 4):

        self.maze_bounds = maze_bounds
        self.num_lucky_blocks = num_lucky_blocks
        self.num_teleports = num_teleports
        
        self.lucky_blocks: List[LuckyBlock] = []
        self.teleport_points: List[TeleportPoint] = []
        self.active_effects: List[ActiveEffect] = []
        
        self.sound_effects = {
            EffectType.STOP_TWO_ROUNDS: "effect_stop",
            EffectType.BOOST: "effect_boost",
            EffectType.SKIP: "effect_skip",
            EffectType.FREEZE: "effect_freeze",
            'lucky_block_open': "lucky_block_collect",
            'teleport_use': "teleport_whoosh"
        }
        
    def initialize_distribution(self, walkable_positions: List[Tuple[float, float, float]]):
        if len(walkable_positions) < self.num_lucky_blocks + self.num_teleports:
            raise ValueError("Not enough walkable positions for all items")
        
        available_positions = walkable_positions.copy()
        random.shuffle(available_positions)
        
        self.lucky_blocks.clear()
        for i in range(self.num_lucky_blocks):
            position = available_positions.pop()
            block = LuckyBlock(position, i)
            self.lucky_blocks.append(block)
        
        self.teleport_points.clear()
        for i in range(self.num_teleports):
            position = available_positions.pop()
            teleport = TeleportPoint(position, i)
            self.teleport_points.append(teleport)
    
    def check_lucky_block_collision(self, player_position: Tuple[float, float, float], 
                                   player_id: str, collision_radius: float = 1.5) -> Optional[EffectType]:

        for block in self.lucky_blocks:
            if block.is_collected:
                continue
                
            distance = self._calculate_distance(player_position, block.position)
            if distance <= collision_radius:
                effect = block.collect()
                self._apply_effect(effect, player_id)
                return effect
        
        return None
    
    def check_teleport_proximity(self, player_position: Tuple[float, float, float], 
                                proximity_radius: float = 2.0) -> Optional[TeleportPoint]:

        for teleport in self.teleport_points:
            if not teleport.is_active:
                continue
                
            distance = self._calculate_distance(player_position, teleport.position)
            if distance <= proximity_radius:
                return teleport
        
        return None
    
    def use_teleport(self, current_position: Tuple[float, float, float], 
                    player_choice: bool) -> Optional[Tuple[float, float, float]]:

        if not player_choice:
            return None
        
        nearby_teleport = self.check_teleport_proximity(current_position, proximity_radius=1.0)
        if not nearby_teleport:
            return None
        
        available_destinations = [tp for tp in self.teleport_points 
                                 if tp.teleport_id != nearby_teleport.teleport_id 
                                 and tp.is_active]
        
        if not available_destinations:
            return None
        
        destination = random.choice(available_destinations)
        return destination.position
    
    def _apply_effect(self, effect_type: EffectType, target_id: str):
        if effect_type == EffectType.STOP_TWO_ROUNDS:
            active_effect = ActiveEffect(effect_type, target_id, duration=2)
            self.active_effects.append(active_effect)
        elif effect_type == EffectType.FREEZE:
            active_effect = ActiveEffect(effect_type, target_id, duration=1)
            self.active_effects.append(active_effect)
        elif effect_type == EffectType.BOOST:
            active_effect = ActiveEffect(effect_type, target_id, duration=0)
            self.active_effects.append(active_effect)
        elif effect_type == EffectType.SKIP:
            active_effect = ActiveEffect(effect_type, target_id, duration=0)
            self.active_effects.append(active_effect)
    
    def is_player_affected(self, player_id: str, effect_type: EffectType) -> bool:
        for effect in self.active_effects:
            if (effect.target_id == player_id and 
                effect.effect_type == effect_type and 
                effect.remaining_rounds > 0):
                return True
        return False
    
    def update_round(self):
        self.active_effects = [effect for effect in self.active_effects 
                              if effect.update_round()]
    
    def get_sound_effect(self, effect_type: EffectType) -> str:
        return self.sound_effects.get(effect_type, "")
    
    def get_lucky_block_sound(self) -> str:
        return self.sound_effects['lucky_block_open']
    
    def get_teleport_sound(self) -> str:
        return self.sound_effects['teleport_use']
    
    def _calculate_distance(self, pos1: Tuple[float, float, float], 
                          pos2: Tuple[float, float, float]) -> float:
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        return (dx**2 + dy**2 + dz**2) ** 0.5
    
    def get_all_visual_data(self) -> Dict:
        return {
            'lucky_blocks': [block.get_visual_data() for block in self.lucky_blocks],
            'teleports': [tp.get_visual_data() for tp in self.teleport_points],
            'active_effects': [
                {
                    'type': effect.effect_type.value,
                    'target': effect.target_id,
                    'remaining': effect.remaining_rounds
                }
                for effect in self.active_effects
            ]
        }
    
    def reset(self):
        self.lucky_blocks.clear()
        self.teleport_points.clear()
        self.active_effects.clear()
    
    def get_statistics(self) -> Dict:
        collected_blocks = sum(1 for block in self.lucky_blocks if block.is_collected)
        effect_counts = {}
        
        for block in self.lucky_blocks:
            if block.effect:
                effect_name = block.effect.value
                effect_counts[effect_name] = effect_counts.get(effect_name, 0) + 1
        
        return {
            'total_lucky_blocks': self.num_lucky_blocks,
            'collected_blocks': collected_blocks,
            'remaining_blocks': self.num_lucky_blocks - collected_blocks,
            'total_teleports': self.num_teleports,
            'effect_distribution': effect_counts,
            'active_effects_count': len(self.active_effects)
        }

class GameFlowIntegration:
    def __init__(self, system: LuckyBlockTeleportSystem):
        self.system = system
        
    def can_player_move(self, player_id: str) -> bool:
        return not (
            self.system.is_player_affected(player_id, EffectType.STOP_TWO_ROUNDS) or
            self.system.is_player_affected(player_id, EffectType.FREEZE)
        )
    
    def apply_movement_boost(self, player_id: str, base_speed: float) -> float:
        if self.system.is_player_affected(player_id, EffectType.BOOST):
            return base_speed * 2.0
        return base_speed
    
    def can_skip_obstacle(self, player_id: str) -> bool:
        return self.system.is_player_affected(player_id, EffectType.SKIP)
    
    def process_turn(self, player_id: str, position: Tuple[float, float, float]) -> Dict:
        results = {
            'can_move': self.can_player_move(player_id),
            'effect_received': None,
            'teleport_available': False,
            'position_changed': False,
            'new_position': position
        }
        
        if not results['can_move']:
            return results
        
        effect = self.system.check_lucky_block_collision(position, player_id)
        if effect:
            results['effect_received'] = effect.value
        
        nearby_teleport = self.system.check_teleport_proximity(position)
        if nearby_teleport:
            results['teleport_available'] = True
        
        return results

if __name__ == "__main__":
    maze_bounds = (0.0, 100.0, 0.0, 100.0)
    system = LuckyBlockTeleportSystem(maze_bounds, num_lucky_blocks=8, num_teleports=4)
    
    walkable_positions = [
        (10.0, 0.0, 10.0), (20.0, 0.0, 15.0), (30.0, 0.0, 20.0),
        (40.0, 0.0, 25.0), (50.0, 0.0, 30.0), (60.0, 0.0, 35.0),
        (70.0, 0.0, 40.0), (80.0, 0.0, 45.0), (15.0, 0.0, 50.0),
        (25.0, 0.0, 55.0), (35.0, 0.0, 60.0), (45.0, 0.0, 65.0)
    ]
    
    system.initialize_distribution(walkable_positions)
    
    game_flow = GameFlowIntegration(system)
    
    player_pos = (10.0, 0.0, 10.0)
    turn_result = game_flow.process_turn("player_1", player_pos)
    
    print("Turn Results:", turn_result)
    print("Statistics:", system.get_statistics())
    print("Visual Data:", system.get_all_visual_data())
