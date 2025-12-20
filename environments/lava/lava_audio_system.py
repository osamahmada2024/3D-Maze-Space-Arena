# Lava/lava_audio_system.py
"""
Audio System for Lava Maze - SEPARATE AUDIO FOLDER
"""

import os
import random
import pygame
from typing import Dict


class LavaAudioSystem:
    """نظام الصوت للمتاهة البركانية - مجلد صوت منفصل"""
    
    def __init__(self, assets_dir: str = "assets/lava_audio"):  # ✅ تغيير المسار
        self.sound_zones = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.ambient_channel = None
        self._initialized = False
        
        # إصلاح المسار
        if not os.path.isabs(assets_dir):
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_file_dir)
            self.assets_dir = os.path.join(project_dir, assets_dir)
        else:
            self.assets_dir = assets_dir
        
        print(f"[LAVA AUDIO] Assets directory: {self.assets_dir}")
        
        # ✅ إنشاء المجلد إذا لم يكن موجوداً
        if not os.path.exists(self.assets_dir):
            print(f"[LAVA AUDIO] ⚠️ Creating audio folder: {self.assets_dir}")
            os.makedirs(self.assets_dir, exist_ok=True)
        
        # عرض الملفات الموجودة
        if os.path.exists(self.assets_dir):
            files = os.listdir(self.assets_dir)
            print(f"[LAVA AUDIO] Available files: {files}")
        
        # تهيئة Mixer
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            
            pygame.mixer.set_num_channels(16)
            
            if pygame.mixer.get_init():
                self.sounds = self._load_sounds()
                self._initialized = True
                loaded_count = len([s for s in self.sounds.values() if s and self._is_valid_sound(s)])
                print(f"[LAVA AUDIO] ✅ Loaded {loaded_count} valid sounds")
            else:
                print("[LAVA AUDIO] ❌ Mixer failed!")
        except Exception as e:
            print(f"[LAVA AUDIO] ❌ Error: {e}")
    
    def _safe_load(self, filename: str, fallback_names: list = None):
        """تحميل ملف صوت مع دعم أسماء بديلة"""
        names_to_try = [filename]
        if fallback_names:
            names_to_try.extend(fallback_names)
        
        for name in names_to_try:
            path = os.path.join(self.assets_dir, name)
            
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    print(f"[LAVA AUDIO] ✅ Loaded: {name}")
                    return sound
                except Exception as e:
                    print(f"[LAVA AUDIO] ⚠️ Error loading {name}: {e}")
                    continue
        
        print(f"[LAVA AUDIO] ⚠️ Missing: {filename}")
        return None  # ✅ إرجاع None بدلاً من صوت صامت
    
    def _load_sounds(self) -> Dict[str, pygame.mixer.Sound]:
        """تحميل أصوات الحمم"""
        return {
            "lava_bubble": self._safe_load("bubble.mp3", ["lava_bubble.mp3", "lava.mp3"]),
            "rumble": self._safe_load("rumble.mp3", ["rumble.wav", "rumble.ogg"]),
            "footstep": self._safe_load("rock_step.mp3", ["footstep.mp3", "walking.mp3"]),
            "burn": self._safe_load("fire.mp3", ["burn.mp3", "fire.wav"]),
        }
    
    def _is_valid_sound(self, sound) -> bool:
        """التحقق من أن الصوت صالح"""
        if sound is None:
            return False
        try:
            return sound.get_length() > 0.1
        except:
            return False
    
    def start_ambient(self):
        """Start continuous lava bubbling ambient"""
        if not self._initialized:
            return
        
        sound = self.sounds.get("lava_bubble")
        if sound and self._is_valid_sound(sound):
            self.ambient_channel = pygame.mixer.find_channel()
            if self.ambient_channel:
                self.ambient_channel.set_volume(0.4)
                self.ambient_channel.play(sound, loops=-1)
                print("[LAVA AUDIO] ✅ Ambient started (bubble)")
        else:
            print("[LAVA AUDIO] ⚠️ No ambient sound - add bubble.mp3 to assets/lava_audio/")
    
    def play_footstep(self):
        """تشغيل صوت الخطوات على الصخور"""
        if not self._initialized:
            return
        sound = self.sounds.get("footstep")
        if sound and self._is_valid_sound(sound):
            ch = pygame.mixer.find_channel()
            if ch:
                ch.set_volume(0.3)
                ch.play(sound)
    
    def play_burn_damage(self):
        """تشغيل صوت الحرق"""
        if not self._initialized:
            return
        
        sound = self.sounds.get("burn")
        if sound and self._is_valid_sound(sound):
            self.ambient_channel = pygame.mixer.find_channel()
            if self.ambient_channel:
                self.ambient_channel.set_volume(0.4)
                self.ambient_channel.play(sound, loops=-1)
    
    def play_rumble(self):
        """تشغيل صوت الهدير البركاني"""
        if not self._initialized:
            return
        sound = self.sounds.get("rumble")
        if sound and self._is_valid_sound(sound):
            ch = pygame.mixer.find_channel()
            if ch:
                ch.set_volume(random.uniform(0.3, 0.5))
                ch.play(sound)
    
    def update(self, dt: float):
        """تحديث النظام الصوتي"""
        if not self._initialized:
            return
        
        # Random rumble للجو البركاني
        if random.random() < 0.005:
            self.play_rumble()
    
    def cleanup(self):
        """تنظيف الموارد"""
        if self.ambient_channel:
            self.ambient_channel.stop()
        print("[LAVA AUDIO] ✅ Cleanup complete")