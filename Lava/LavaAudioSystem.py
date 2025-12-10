"""
Audio System for Lava Maze
Bubbling lava, rumbling, footsteps on rock.
"""

import os
import pygame

class LavaAudioSystem:
    def __init__(self, assets_dir: str = "assets/audio"):
        self.assets_dir = assets_dir
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(16)
        
        self.sounds = self._load_sounds()
        self.ambient_channel = None
        print(f"[LAVA AUDIO] Initialized with {len(self.sounds)} sounds")
    
    def _safe_load(self, filename: str):
        path = os.path.join(self.assets_dir, filename)
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except:
                pass
        # Silent fallback
        return pygame.mixer.Sound(buffer=bytes([0] * 2000))
    
    def _load_sounds(self):
        return {
            "lava_bubble": self._safe_load("lava_bubble.mp3"),
            "rumble": self._safe_load("rumble.mp3"),
            "footstep": self._safe_load("rock_step.mp3"),
            "burn": self._safe_load("fire.mp3")
        }
    
    def start_ambient(self):
        """Start continuous lava bubbling ambient"""
        if "lava_bubble" in self.sounds:
            self.ambient_channel = pygame.mixer.find_channel()
            if self.ambient_channel:
                self.ambient_channel.set_volume(0.4)
                self.ambient_channel.play(self.sounds["lava_bubble"], loops=-1)
    
    def play_footstep(self):
        ch = pygame.mixer.find_channel()
        if ch and "footstep" in self.sounds:
            ch.set_volume(0.3)
            ch.play(self.sounds["footstep"])
    
    def play_burn_damage(self):
        ch = pygame.mixer.find_channel()
        if ch and "burn" in self.sounds:
            ch.set_volume(0.6)
            ch.play(self.sounds["burn"])
    
    def update(self, dt: float):
        # Random rumble
        if random.random() < 0.005:
            ch = pygame.mixer.find_channel()
            if ch and "rumble" in self.sounds:
                ch.set_volume(random.uniform(0.2, 0.4))
                ch.play(self.sounds["rumble"])
    
    def cleanup(self):
        if self.ambient_channel:
            self.ambient_channel.stop()
        pygame.mixer.quit()

