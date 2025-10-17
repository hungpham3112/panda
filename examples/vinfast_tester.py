from panda import Panda
import time
from opendbc.car.structs import CarParams
import threading


def heartbeat_thread(panda_device):
    """Dedicated thread for sending heartbeats at exactly 100Hz"""
    while True:
        try:
            panda_device.send_heartbeat(engaged=True)
            time.sleep(0.011)  # Precise 100Hz timing
        except:
            break


def test_vinfast_mode():
    try:
        print("Connecting to Panda...")
        p = Panda()

        # Start dedicated heartbeat thread
        print("Starting heartbeat thread...")
        hb_thread = threading.Thread(target=heartbeat_thread, args=(p,), daemon=True)
        hb_thread.start()

        print("Setting VinFast safety mode...")
        p.set_safety_mode(CarParams.SafetyModel.vinfast)

        # Main loop for CAN messages and debug output
        while True:
            # Send test CAN message every 2 seconds
            test_msg = bytearray([0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8])
            p.can_send(0x1, test_msg, 0)

            # Read debug messages
            debug_msg = p.serial_read(0)
            if debug_msg:
                try:
                    print(f"Debug: {debug_msg.decode('utf-8')}")
                except UnicodeDecodeError:
                    print(f"Debug (hex): {debug_msg.hex()}")

            # Read CAN messages
            can_msgs = p.can_recv()
            for msg in can_msgs:
                address, _, data, bus = msg
                print(
                    f"Received CAN - ID: 0x{address:x}, Bus: {bus}, Data: {bytes(data).hex()}"
                )

            time.sleep(2.1)  # Main loop runs every 2 seconds

    except KeyboardInterrupt:
        print("\nTest terminated by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if "p" in locals():
            print("Resetting to SILENT mode...")
            p.set_safety_mode(CarParams.SafetyModel.silent)


if __name__ == "__main__":
    test_vinfast_mode()
