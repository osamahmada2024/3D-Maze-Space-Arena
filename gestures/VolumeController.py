import os
import platform

SYSTEM = platform.system()

class VolumeController:
    def __init__(self):
        if SYSTEM == "Windows":
            from comtypes import CLSCTX_ALL
            from ctypes import cast, POINTER
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        elif SYSTEM == "Linux":
            try:
                import pulsectl
                self.PULSE_AVAILABLE = True
            except:
                self.PULSE_AVAILABLE = False

        self.system = SYSTEM
        self.is_muted = False

        if self.system == "Windows":
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            self.is_muted = bool(self.volume.GetMute())

        elif self.system == "Linux":
            if self.PULSE_AVAILABLE:
                self.pulse = pulsectl.Pulse("gesture-volume")
                self.sink = self.pulse.sink_list()[0]

    def mute(self):
        if self.system == "Windows":
            self.volume.SetMute(1, None)
        elif self.system == "Linux":
            if self.PULSE_AVAILABLE:
                self.pulse.sink_mute(self.sink.index, True)
            else:
                os.system("amixer -D pulse sset Master mute")
        self.is_muted = True

    def unmute(self):
        if self.system == "Windows":
            self.volume.SetMute(0, None)
        elif self.system == "Linux":
            if self.PULSE_AVAILABLE:
                self.pulse.sink_mute(self.sink.index, False)
            else:
                os.system("amixer -D pulse sset Master unmute")
        self.is_muted = False