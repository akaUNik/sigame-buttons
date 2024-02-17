#!/usr/bin/python3
from zigpy.config import CONF_DEVICE
import zigpy.config as conf
from zigpy.types.named import EUI64
import zigpy.device
import asyncio
from asyncio import create_task
from time import sleep


# Config
buttons = [
    ('00:15:8d:00:08:4e:57:6a', 'button1'),
    ('00:15:8d:00:08:4e:5e:0f', 'button2'),
    ('00:15:8d:00:08:4e:5f:42', 'button3'),
]
mode = 'LISTEN'

"""
Replace 'zigpy_xbee' with the radio that you are using, you can download it using pip.
https://github.com/zigpy/zigpy-xbee
https://github.com/zigpy/zigpy-deconz
https://github.com/zigpy/zigpy-zigate
"""
from zigpy_znp.zigbee.application import ControllerApplication
from zigpy.zcl.clusters.general import OnOff

device_config = {
    #Change to your device
    conf.CONF_DEVICE_PATH: "/dev/serial/by-id/usb-Texas_Instruments_TI_CC2531_USB_CDC___0X00124B001CD500E0-if00",
}

zigpy_config = {
    conf.CONF_DATABASE: "zigpy.db",
    conf.CONF_DEVICE: device_config,
    conf.CONF_NWK_CHANNEL: 20
}

class YourListenerClass:
    def __init__(self,za,ext_callback):
        self.za=za
        self.ext_callback=ext_callback
    """
    These are called by the ControllerApplication using call like this: 
    self.listener_event("raw_device_initialized", device)
    """
    def handle_message(
        self,
        device: zigpy.device.Device,
        profile: int,
        cluster: int,
        src_ep: int,
        dst_ep: int,
        message: bytes,
    ) -> None:
        if(self.ext_callback):
            self.ext_callback(ieee=device.ieee,message=message,cluster=cluster)
        else:
            print(f"Handle_message {device.ieee} profile {profile}, cluster {cluster}, src_ep {src_ep}, dst_ep {dst_ep},\tmessage {message} ")
            global mode
            print(f'mode = {mode}')
            for button in buttons:
                if str(device.ieee) == button[0] and mode == 'LISTEN':
                    print(button[1])
                    mode = 'SLEEP'
                    sleep(3)

def get_za():
    global za
    return za

async def start_zigbee(ext_callback):
    try:
        global za
        za = await ControllerApplication.new(
            config=ControllerApplication.SCHEMA(zigpy_config),
            auto_form=True,
            start_radio=True,
        )

        listener = YourListenerClass( za,ext_callback )

        za.add_listener(listener)
        za.groups.add_listener(listener)
        print("ZigPy started!")

    except Exception:
        import traceback
        traceback.print_exc()

running=True
async def run_application(ext_callback=None):
    await start_zigbee(ext_callback)
    # Run forever
    await asyncio.get_running_loop().create_future()
    if za:
        await za.shutdown()
    running=False

async def stop_application():
    print("Stopping application...")
    global running
    running=False
    await za.shutdown()


if __name__ =="__main__":
    asyncio.run(run_application())