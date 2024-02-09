# Busylight MQTT client for Kuando busylights
# <tec att sixtopia.net>

import time
import hid
import threading

# Kuando Busylight Vendor ID and Product ID
VENDOR_ID = 0x27BB
PRODUCT_ID = 0x3BCD

# Command bytes for setting the color and turning off the light
SET_COLOR_COMMAND = bytes([0x01, 0x4D, 0x08])
OFF_COMMAND = bytes([0x01, 0x4D, 0x00])

# Color codes
COLORS = {
    "off": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "white": (255, 255, 255),
}


def find_busylight():
    """Find the Kuando Busylight device."""
    devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
    if devices:
        return devices[0]['path']
    return None


def set_color(color):
    """Set the color of the Kuando Busylight."""
    device_path = find_busylight()
    if not device_path:
        print("Kuando Busylight not found.")
        return

    try:
        with hid.device() as busylight:
            busylight.open_path(device_path)
            color_bytes = bytes([0x01, 0x4D, 0x08]) + bytes(color)
            busylight.write(color_bytes)
            print(f"Color set to {color}")
    except IOError as e:
        print(f"Error communicating with Kuando Busylight: {e}")


def turn_off():
    """Turn off the Kuando Busylight."""
    set_color((0, 0, 0))


def blink(color, duration=1):
    """Blink the Kuando Busylight with the specified color."""
    set_color(color)
    time.sleep(duration)
    turn_off()


def usb_event_handler(added, device):
    """Handle USB device events."""
    if added:
        print(f"Device added: {device.product_name}")
    else:
        print(f"Device removed: {device.product_name}")


def monitor_usb_events():
    """Monitor USB events to detect addition or removal of Busylight."""
    import pywinusb.hid as hid

    filter = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID)
    filter.register(on_hid_events=usb_event_handler)
    while True:
        hid.HidThread.run()


def main():
    # Start USB event monitoring in a separate thread
    usb_thread = threading.Thread(target=monitor_usb_events, daemon=True)
    usb_thread.start()

    # Test all colors
    print("Testing all colors...")
    for color_name, color_value in COLORS.items():
        print(f"Setting color to {color_name}...")
        set_color(color_value)
        time.sleep(1)

    # Test blink
    print("Testing blink...")
    for _ in range(3):
        print("Blinking...")
        blink(COLORS["red"], duration=1)
        time.sleep(2)

    # Turn off the light
    print("Turning off the light...")
    turn_off()


if __name__ == "__main__":
    main()
