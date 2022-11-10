from framework import Driver
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl

try:
    import frk_cc as ConsumerControlCode
except:
    from adafruit_hid.consumer_control_code import ConsumerControlCode

class USBCCDevice(Driver):
    _defaults = {'message': None,
                 'sent': False,
                 'on_sent': []}

    def _init_device(self):
        self._device = ConsumerControl(usb_hid.devices)

    def _set_message(self, v):
        self._device.send(getattr(ConsumerControlCode, v, None))
        self._handle_event('sent')
