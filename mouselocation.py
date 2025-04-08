import pyautogui
import time

def print_mouse_position():
    try:
        while True:
            x, y = pyautogui.position()  # Get the current mouse position
            print(f"Mouse Position: X={x}, Y={y}")
            time.sleep(1)  # Update every second
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    print("Press Ctrl+C to stop.")
    print_mouse_position()
