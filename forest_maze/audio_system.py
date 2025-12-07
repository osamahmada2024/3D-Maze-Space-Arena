"""
Audio System for Forest Scene (Enhanced)
Supports ambient, footsteps (multiple surfaces), collision, and bird sounds.
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
        self.assets_dir = assets_dir
        self.sound_zones = {}
        self.player_position = (0, 0, 0)

        # Initialize mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(16)
        print(pygame.mixer.get_init())  # لازم يطبع قيمة غير None

        self.sounds = self._load_sounds()
        print(f"[AUDIO] Audio system initialized. Loaded {len(self.sounds)} sounds.")

    # -------------------------------------------------------------------------
    # SOUND LOADING
    # -------------------------------------------------------------------------
    def _safe_load(self, filename: str):
        path = os.path.join(self.assets_dir, filename)

        if os.path.exists(path):
            try:
                print(f"[AUDIO] Loaded: {filename}")
                return pygame.mixer.Sound(path)
            except Exception as e:
                print(f"[AUDIO ERROR] Failed to load {filename}: {e}")

        print(f"[AUDIO WARNING] Missing file: {filename} -> using silent sound")
        return pygame.mixer.Sound(buffer=bytes([0] * 2000))

    def _load_sounds(self) -> Dict[str, pygame.mixer.Sound]:
        # يمكن تضيف أصوات مختلفة لكل نوع سطح لاحقًا
        return {
            "birds": self._safe_load("birds.mp3"),
            "wind": self._safe_load("wind.mp3"),
            "footstep": self._safe_load("wallking.mp3"),
            "collision": self._safe_load("bump.mp3")
        }

    # -------------------------------------------------------------------------
    # ZONE SYSTEM
    # -------------------------------------------------------------------------
    def add_sound_zone(self, name, position, sound_type, volume=0.6, radius=15.0):
        zone = SoundZone(name, position, sound_type, volume, radius)
        zone.sound = self.sounds.get(sound_type)
        self.sound_zones[name] = zone

        zone.channel = pygame.mixer.find_channel()
        if zone.channel and zone.sound:
            zone.channel.set_volume(0)
            zone.channel.play(zone.sound, loops=-1)
            zone.channel.pause()

        print(f"[AUDIO] Added zone '{name}' type={sound_type}")

    # -------------------------------------------------------------------------
    # SOUND EVENTS
    # -------------------------------------------------------------------------
    def play_footstep(self, surface_type: str = "grass"):
        """Play footstep sound depending on surface type"""
        # حاليا عندنا صوت واحد للـ footstep، ممكن توسع لاحقًا
        sound_key = "footstep"

        ch = pygame.mixer.find_channel()
        if ch and sound_key in self.sounds:
            ch.set_volume(0.5)
            ch.play(self.sounds[sound_key])

    def play_bird_chirp(self):
        ch = pygame.mixer.find_channel()
        if ch:
            ch.set_volume(random.uniform(0.3, 0.6))
            ch.play(self.sounds["birds"])

    def play_collision(self):
        ch = pygame.mixer.find_channel()
        if ch:
            ch.set_volume(0.6)
            ch.play(self.sounds["collision"])

    # -------------------------------------------------------------------------
    # POSITIONAL AUDIO
    # -------------------------------------------------------------------------
    def update_positional_audio(self, player_pos):
        self.player_position = player_pos
        px, _, pz = player_pos

        for zone in self.sound_zones.values():
            zx, _, zz = zone.position
            dx = px - zx
            dz = pz - zz
            dist = (dx * dx + dz * dz) ** 0.5

            if dist < zone.radius:
                vol = zone.volume * (1 - dist / zone.radius)
                pan = max(-1.0, min(1.0, dx / zone.radius))
                left = vol * (1.0 - pan)
                right = vol * (1.0 + pan)
                if zone.channel:
                    zone.channel.set_volume(left, right)
                    zone.channel.unpause()
                zone.active = True
            else:
                if zone.active and zone.channel:
                    zone.channel.pause()
                    zone.active = False

    # -------------------------------------------------------------------------
    # GENERAL UPDATE
    # -------------------------------------------------------------------------
    def update(self, dt):
        # Random bird chirp for ambiance
        if random.random() < 0.003:
            self.play_bird_chirp()

    def set_master_volume(self, volume: float):
        """Set master volume for all sound zones"""
        for zone in self.sound_zones.values():
            zone.volume = volume
            if zone.channel:
                # نضبط الصوت الحالي حسب الحالة
                if zone.active:
                    zone.channel.set_volume(volume, volume)


    def play_global_sound(self, sound_type: str, volume: float = 0.5):
        sound = self.sounds.get(sound_type)
        if sound:
            ch = pygame.mixer.find_channel()
            if ch:
                ch.set_volume(volume)
                ch.play(sound)


    # -------------------------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------------------------
    def cleanup(self):
        for z in self.sound_zones.values():
            if z.channel:
                z.channel.stop()
        pygame.mixer.quit()
        print("[AUDIO] Cleanup complete")
