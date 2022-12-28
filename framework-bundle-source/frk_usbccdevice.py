import usb_hid
import time
import struct

class USBCCDevice:
    message = ""
    raw_code = None
    sent = False
    on_sent = []
    
    def _init_device(self):
        if hasattr(self, "_register"):
            self._codes.update(self._register)
        self._device = self._find_device(usb_hid.devices, usage_page=0x0C, usage=0x01)
        self._report = bytearray(2)
        try:
            self._send(0x0)
        except OSError:
            time.sleep(1)
            self._send(0x0)
    
    def _find_device(self, devices, *, usage_page, usage):
        if hasattr(devices, "send_report"):
            devices = [devices]
        for device in devices:
            if device.usage_page == usage_page and device.usage == usage and hasattr(device, "send_report"):
                return device
    
    def _send(self, code):
        self._press(code)
        self._release
    
    def _press(self, code):
        struct.pack_into("<H", self._report, 0, code)
        self._device.send_report(self._report)
    
    def _release(self):
        self._report[0] = self._report[1] = 0x0
        self._device.send_report(self._report)
    
    def _set_message(self, v):
        self._send(self._codes[v])
        self._handle_event("sent", v)
    
    def _set_raw_code(self, v):
        self._send(v)
        self._handle_event("sent", v)
    
    def _deinit(self):
        pass
    
    def register_code(self, message, code):
        self._codes.update({message: code})
    
    _codes = {
        "PLAY": 0xB0,
        "PAUSE": 0xB1,
        "RECORD": 0xB2,
        "FAST_FORWARD": 0xB3,
        "REWIND": 0xB4,
        "SCAN_NEXT_TRACK": 0xB5,
        "SCAN_PREVIOUS_TRACK": 0xB6,
        "STOP": 0xB7,
        "EJECT": 0xB8,
        "RANDOM_PLAY": 0xB9,
        "SELECT_DISC": 0xBA,
        "ENTER_DISC": 0xBB,
        "REPEAT": 0xBC,
        "TRACKING": 0xBD,
        "TRACK_NORMAL": 0xBE,
        "SLOW_TRACKING": 0xBF,
        "FRAME_FORWARD": 0xC0,
        "FRAME_BACK": 0xC1,
        "MARK": 0xC2,
        "CLEAR_MARK": 0xC3,
        "REPEAT_FROM_MARK": 0xC4,
        "RETURN_TO_MARK": 0xC5,
        "SEARCH_MARK_FORWARD": 0xC6,
        "SEARCH_MARK_BACKWARDS": 0xC7,
        "COUNTER_RESET": 0xC8,
        "SHOW_COUNTER": 0xC9,
        "TRACKING_INCREMENT": 0xCA,
        "TRACKING_DECREMENT": 0xCB,
        "VOLUME": 0xE0,
        "BALANCE": 0xE1,
        "MUTE": 0xE2,
        "BASS": 0xE3,
        "TREBLE": 0xE4,
        "BASS_BOOST": 0xE5,
        "SURROUND_MODE": 0xE6,
        "LOUDNESS": 0xE7,
        "MPX": 0xE8,
        "VOLUME_UP": 0xE9,
        "VOLUME_DOWN": 0xEA,
        "SPEED_SELECT": 0xF0,
        "PLAYBACK_SPEED": 0xF1,
        "STANDARD_PLAY": 0xF2,
        "LONG_PLAY": 0xF3,
        "EXTENDED_PLAY": 0xF4,
        "SLOW": 0xF5,
        "BALANCE_RIGHT": 0x150,
        "BALANCE_LEFT": 0x151,
        "BASS_INCREMENT": 0x152,
        "BASS_DECREMENT": 0x153,
        "TREBLE_INCREMENT": 0x154,
        "TREBLE_DECREMENT": 0x155,
        "SPEAKER_SYSTEM": 0x160,
        "CHANNEL_LEFT": 0x161,
        "CHANNEL_RIGHT": 0x162,
        "CHANNEL_CENTER": 0x163,
        "CHANNEL_FRONT": 0x164,
        "CHANNEL_CENTER_FRONT": 0x165,
        "CHANNEL_SIDE": 0x166,
        "CHANNEL_SURROUND": 0x167,
        "CHANNEL_LOW_FREQUENCY_ENHANCEMENT": 0x168,
        "CHANNEL_TOP": 0x169,
        "CHANNEL_UNKNOWN": 0x16A,
        "SUB_CHANNEL": 0x170,
        "SUB_CHANNEL_INCREMENT": 0x171,
        "SUB_CHANNEL_DECREMENT": 0x172,
        "ALTERNATE_AUDIO_INCREMENT": 0x173,
        "ALTERNATE_AUDIO_DECREMENT": 0x174
    }