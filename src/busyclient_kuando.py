import time
import hid
import threading
import paho.mqtt.client as mqtt

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
    for device_info in hid.enumerate(VENDOR_ID, PRODUCT_ID):
        if device_info["interface_number"] == 1:
            return device_info["path"]
    return None

def set_color(color):
    """Set the color of the Kuando Busylight."""
    device_path = find_busylight()
    if not device_path:
        print("Kuando Busylight not found.")
        return

    try:
        with hid.Device(path=device_path) as busylight:
            color_bytes = SET_COLOR_COMMAND + bytes(color)
            busylight.write(color_bytes)
            print(f"Color set to {color}")
    except IOError as e:
        print(f"Error communicating with Kuando Busylight: {e}")

def turn_off():
    """Turn off the Kuando Busylight."""
    set_color((0, 0, 0))

def on_message(client, userdata, message):
    """Callback function for handling MQTT messages."""
    topic = message.topic
    payload = message.payload.decode('utf-8')

    print(f"Received message: {payload} on topic: {topic}")

    if topic == "busylight/color":
        if payload in COLORS:
            set_color(COLORS[payload])
        else:
            print("Invalid color specified.")
    elif topic == "busylight/off":
        turn_off()
    else:
        print("Unknown topic.")

def main():
    # Start MQTT client
    client = mqtt.Client()
    client.username_pw_set(username="username", password="password")
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.subscribe("busylight01/#")
    mqtt_thread = threading.Thread(target=client.loop_forever)
    mqtt_thread.start()

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
        set_color(COLORS["red"])
        time.sleep(1)
        turn_off()
        time.sleep(1)

    # Turn off the light
    print("Turning off the light...")
    turn_off()

if __name__ == "__main__":
    main()
