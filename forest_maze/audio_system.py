"""
Audio System
Manages ambient forest sounds, wind, birds, and sound zones.
"""

import random
import math
import pygame
import os

class AudioSystem:
    """
    Manages audio effects including ambient sounds and positional audio.
    Uses pygame.mixer for audio playback.
    """
    
    def __init__(self):
        """Initialize audio system"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except Exception as e:
            print(f"Warning: Audio system initialization failed: {e}")
        
        self.ambient_enabled = True
        self.sound_zones = {}  # Dictionary of sound zone audio clips
        self.ambient_sounds = []
        self.wind_volume = 0.3
        self.bird_volume = 0.2
        self.current_ambient_channel = None
        self.sound_timers = {}
    
    def add_sound_zone(self, zone_id: str, position: tuple, 
                       sound_file: str = None, sound_type: str = "wind"):
        """
        Add a sound zone to the environment.
        
        Args:
            zone_id: Unique identifier for the zone
            position: (x, y, z) position of the zone
            sound_file: Path to sound file (optional)
            sound_type: Type of sound ("wind", "birds", "ambient")
        """
        self.sound_zones[zone_id] = {
            'position': position,
            'sound_file': sound_file,
            'sound_type': sound_type,
            'volume': 0.5,
            'radius': 10.0,
        }
    
    def play_ambient_wind(self, volume: float = 0.3):
        """
        Play wind ambient sound.
        Uses sine wave modulation to simulate wind gusts.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.wind_volume = max(0.0, min(1.0, volume))
        
        try:
            # Create simple wind sound effect using pygame mixer
            # In a real implementation, you'd load wind.wav files
            if not self.current_ambient_channel:
                self.current_ambient_channel = pygame.mixer.find_channel()
            
            # Volume modulation for wind effect
            self.current_ambient_channel.set_volume(self.wind_volume)
        except Exception as e:
            pass  # Silently fail if audio not available
    
    def play_bird_sounds(self, volume: float = 0.2):
        """
        Play occasional bird chirping sounds.
        Simulated with random intervals.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.bird_volume = max(0.0, min(1.0, volume))
        # Bird sounds would be loaded from files in a full implementation
    
    def update_positional_audio(self, player_position: tuple):
        """
        Update audio based on player position relative to sound zones.
        
        Args:
            player_position: (x, y, z) player position
        """
        px, py, pz = player_position
        
        for zone_id, zone_data in self.sound_zones.items():
            zx, zy, zz = zone_data['position']
            radius = zone_data['radius']
            
            # Calculate distance to sound zone
            dx = px - zx
            dy = py - zy
            dz = pz - zz
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Calculate volume based on distance
            if distance < radius:
                volume = zone_data['volume'] * (1.0 - distance / radius)
                # Apply volume to sound
                # In full implementation: play sound with this volume
            else:
                # Sound out of range
                pass
    
    def add_wind_gust(self):
        """
        Add a sudden wind gust effect.
        """
        if self.ambient_enabled:
            self.wind_volume = min(1.0, self.wind_volume + 0.2)
            self.sound_timers['wind_gust'] = 0.5  # Gust lasts 0.5 seconds
    
    def update(self, dt: float):
        """
        Update audio system.
        
        Args:
            dt: Delta time in seconds
        """
        # Decay wind gusts
        if 'wind_gust' in self.sound_timers:
            self.sound_timers['wind_gust'] -= dt
            if self.sound_timers['wind_gust'] <= 0:
                del self.sound_timers['wind_gust']
                self.wind_volume = 0.3

    def play_footstep(self, foot_type: str = 'default'):
        """Play a footstep sound depending on surface type (e.g., 'grass', 'stone')."""
        try:
            # look for assets/footstep_<type>.wav
            fname = f"assets/footstep_{foot_type}.wav"
            if os.path.exists(fname):
                sound = pygame.mixer.Sound(fname)
                ch = pygame.mixer.find_channel()
                if ch:
                    ch.set_volume(0.6)
                    ch.play(sound)
            else:
                # fallback: small volume beep using pygame tone generation is not available; skip
                pass
        except Exception:
            pass

    def play_bird_chirp(self):
        """Play an occasional bird chirp if asset exists."""
        try:
            fname = "assets/bird_chirp.wav"
            if os.path.exists(fname):
                sound = pygame.mixer.Sound(fname)
                ch = pygame.mixer.find_channel()
                if ch:
                    ch.set_volume(self.bird_volume)
                    ch.play(sound)
        except Exception:
            pass

    def play_secret_glow(self):
        """Play a secret area glow sound if asset exists."""
        try:
            fname = "assets/secret_glow.wav"
            if os.path.exists(fname):
                sound = pygame.mixer.Sound(fname)
                ch = pygame.mixer.find_channel()
                if ch:
                    ch.set_volume(0.8)
                    ch.play(sound)
        except Exception:
            pass
    
    def set_ambient_enabled(self, enabled: bool):
        """Enable/disable ambient sounds"""
        self.ambient_enabled = enabled
    
    def cleanup(self):
        """Clean up audio resources"""
        try:
            pygame.mixer.stop()
        except:
            pass
