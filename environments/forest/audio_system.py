# forest/audio_system.py
"""
Audio System for Forest Scene - FIXED PATH VERSION
"""

import os
import random
from typing import Dict, Tuple
import pygame


class SoundZone:
    def __init__(self, name: str, position: Tuple[float, float, float],
                 sound_type: str, volume: float = 0.5, radius: float = 12.0):
        self.name = name
        self.position = position
        self.sound_type = sound_type
        self.volume = volume
        self.radius = radius
        self.active = False
        self.sound = None
        self.channel = None


class AudioSystem:
    def __init__(self, assets_dir: str = "assets/audio"):
        self.sound_zones = {}
        self.player_position = (0, 0, 0)
        self.sounds = {}
        self._initialized = False

        if not os.path.isabs(assets_dir):
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_file_dir)
            self.assets_dir = os.path.join(project_dir, assets_dir)
        else:
            self.assets_dir = assets_dir
        
        print(f"[AUDIO] Assets directory: {self.assets_dir}")
        
        if not os.path.exists(self.assets_dir):
            print(f"[AUDIO] ❌ Audio directory not found: {self.assets_dir}")
            return
        
        files = os.listdir(self.assets_dir)
        print(f"[AUDIO] Files found: {files}")

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            
            pygame.mixer.set_num_channels(16)
            
            if pygame.mixer.get_init():
                print(f"[AUDIO] ✅ Mixer initialized")
                self.sounds = self._load_sounds()
                self._initialized = True
                print(f"[AUDIO] ✅ Loaded {len(self.sounds)} sounds")
            else:
                print("[AUDIO] ❌ Mixer failed!")
                
        except Exception as e:
            print(f"[AUDIO] ❌ Error: {e}")

    def _safe_load(self, filename: str):
        """تحميل ملف صوت"""
        path = os.path.join(self.assets_dir, filename)

        if os.path.exists(path):
            try:
                sound = pygame.mixer.Sound(path)
                print(f"[AUDIO] ✅ Loaded: {filename}")
                return sound
            except Exception as e:
                print(f"[AUDIO] ❌ Error loading {filename}: {e}")
        else:
            print(f"[AUDIO] ⚠️ File not found: {path}")

        try:
            return pygame.mixer.Sound(buffer=bytes([0] * 2000))
        except:
            return None

    def _load_sounds(self) -> Dict[str, pygame.mixer.Sound]:
        return {
            "birds": self._safe_load("birds.mp3"),
            "wind": self._safe_load("wind.mp3"),
            "footstep": self._safe_load("walking.mp3"),
            "collision": self._safe_load("bump.mp3")
        }

    def add_sound_zone(self, name, position, sound_type, volume=0.6, radius=15.0):
        if not self._initialized:
            return
            
        zone = SoundZone(name, position, sound_type, volume, radius)
        zone.sound = self.sounds.get(sound_type)
        self.sound_zones[name] = zone

        if zone.sound:
            zone.channel = pygame.mixer.find_channel()
            if zone.channel:
                zone.channel.set_volume(0)
                zone.channel.play(zone.sound, loops=-1)
                zone.channel.pause()
                print(f"[AUDIO] ✅ Zone '{name}' ready")

    def play_footstep(self, surface_type: str = "grass"):
        if not self._initialized:
            return
        sound = self.sounds.get("footstep")
        if sound:
            ch = pygame.mixer.find_channel()
            if ch:
                ch.set_volume(0.4)
                ch.play(sound)

    def play_bird_chirp(self):
        if not self._initialized:
            return
        sound = self.sounds.get("birds")
        if sound:
            ch = pygame.mixer.find_channel()
            if ch:
                ch.set_volume(random.uniform(0.2, 0.5))
                ch.play(sound)

    def play_collision(self):
        if not self._initialized:
            return
        sound = self.sounds.get("collision")
        if sound:
            ch = pygame.mixer.find_channel()
            if ch:
                ch.set_volume(0.5)
                ch.play(sound)

    def update_positional_audio(self, player_pos):
        if not self._initialized:
            return
            
        self.player_position = player_pos
        px, _, pz = player_pos

        for zone in self.sound_zones.values():
            if not zone.channel:
                continue
                
            zx, _, zz = zone.position
            dist = ((px - zx)**2 + (pz - zz)**2) ** 0.5

            if dist < zone.radius:
                vol = zone.volume * (1 - dist / zone.radius)
                zone.channel.set_volume(vol, vol)
                zone.channel.unpause()
                zone.active = True
            else:
                if zone.active:
                    zone.channel.pause()
                    zone.active = False

    def update(self, dt):
        if not self._initialized:
            return
        if random.random() < 0.002:
            self.play_bird_chirp()

    def set_master_volume(self, volume: float):
        for zone in self.sound_zones.values():
            zone.volume = max(0, min(1, volume))

    def play_global_sound(self, sound_type: str, volume: float = 0.5):
        if not self._initialized:
            return
        sound = self.sounds.get(sound_type)
        if sound:
            ch = pygame.mixer.find_channel()
            if ch:
                ch.set_volume(volume)
                ch.play(sound)

    def cleanup(self):
        for z in self.sound_zones.values():
            if z.channel:
                z.channel.stop()
        try:
            pygame.mixer.quit()
        except:
            pass
        print("[AUDIO] ✅ Cleanup complete")