#!/usr/bin/python3
from zigpy.config import CONF_DEVICE
import zigpy.config as conf
from zigpy.types.named import EUI64
import zigpy.device
import asyncio
import signal
from asyncio import create_task
from time import sleep
import board
import neopixel


# Config
buttons = [
    ('a4:c1:38:24:fe:65:09:1f', 'master', (0, 0, 0)),
    ('00:15:8d:00:08:4e:57:6a', 'player1', (255, 0, 0)),
    ('00:15:8d:00:08:4e:5e:0f', 'player2', (0, 255, 0)),
    ('00:15:8d:00:08:4e:5f:42', 'player3', (0, 0, 255)),
    ('00:15:8d:00:0a:ca:1d:2a', 'player4', (255, 255, 0)),
]
mode = 'LISTEN'

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18
# The number of NeoPixels
num_pixels = 64
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)

def show_rainbow(wait):
    for j in range(25):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j * 10
            pixels[i] = wheel(pixel_index & 255)
        # pixels.show()
        sleep(wait)
    pixels.fill((0, 0, 0))

"""
Replace 'zigpy_xbee' with the radio that you are using, you can download it using pip.
https://github.com/zigpy/zigpy-xbee
https://github.com/zigpy/zigpy-deconz
https://github.com/zigpy/zigpy-zigate
"""
from zigpy_znp.zigbee.application import ControllerApplication

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
    def __init__(self, za, ext_callback):
        self.za = za
        self.ext_callback = ext_callback
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
            self.ext_callback(ieee=device.ieee, message=message, cluster=cluster)
        else:
            print(f"Handle_message {device.ieee} profile {profile}, cluster {cluster}, src_ep {src_ep}, dst_ep {dst_ep},\tmessage {message} ")
            global mode
            print(f'mode = {mode}')
            for button in buttons:
                ieee = button[0]
                name = button[1]
                color = button[2]

                if str(device.ieee) == ieee and mode == 'LISTEN' and 'player' in name:
                    print(f'Player: {name}')
                    mode = 'SLEEP'
                    pixels.fill(color)
                    sleep(3)
                    pixels.fill((0, 0, 0))
                    pixels[0] = (255, 0, 0)
                elif str(device.ieee) == ieee and mode == 'SLEEP' and 'master' in name:
                    print(f'Master: {name}')
                    mode = 'LISTEN'
                    pixels.fill(color)
                    pixels[0] = (0, 255, 0)

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

        listener = YourListenerClass(za, ext_callback)

        za.add_listener(listener)
        za.groups.add_listener(listener)
        print("ZigPy started!")
        show_rainbow(0.005)

    except Exception:
        import traceback
        traceback.print_exc()

running = True
async def run_application(ext_callback=None):
    await start_zigbee(ext_callback)

    loop = asyncio.get_running_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(stop_application(s, loop)))

    # Run forever
    try:
        await loop.create_future()
    except asyncio.exceptions.CancelledError:
        pass

    if za:
        await za.shutdown()
    running = False

async def stop_application(signal, loop):
    print("Stopping application...")
    global running
    running = False

    tasks = [t for t in asyncio.all_tasks() if t is not
              asyncio.current_task()]
    # await asyncio.sleep(0)
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    await loop.stop()

    if za:
        await za.shutdown()

if __name__ == "__main__":
    asyncio.run(run_application())