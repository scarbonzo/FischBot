import pyautogui
import time
import random
import cv2
import numpy as np
from PIL import ImageGrab
import keyboard
import os
import pydirectinput

# Safety settings for pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class FischBot:
    def __init__(self):
        self.running = False
        self.casting = False
        self.hooked = False
        self.last_click_time = 0
        self.space_held = False  # Track if space is currently held down
        # Load the template images
        self.shake_template = cv2.imread('Shake.png')
        self.hooked_template = cv2.imread('Hooked.png')
        self.fish_template = cv2.imread('Fish1.png')
        if self.shake_template is None:
            raise FileNotFoundError("Shake.png not found. Please make sure the image is in the same directory as the script.")
        if self.hooked_template is None:
            raise FileNotFoundError("Hooked.png not found. Please make sure the image is in the same directory as the script.")
        if self.fish_template is None:
            raise FileNotFoundError("Fish1.png not found. Please make sure the image is in the same directory as the script.")
        
    def start(self):
        """Start the bot"""
        self.running = True
        
        while self.running:
            if keyboard.is_pressed('q'):
                self.running = False
                break
                
            if not self.casting:
                self.cast_line()
            elif not self.hooked:
                self.wait_for_shake_or_hook()
            else:
                self.catch_fish()
                
    def cast_line(self):
        """Cast the fishing line by holding left click for 0.5 seconds"""
        # Get current mouse position
        current_x, current_y = pyautogui.position()
        
        # Move to the middle of the left half of the screen
        screen_width, screen_height = pyautogui.size()
        cast_x = screen_width // 2  # Middle horizontally
        cast_y = screen_height // 2  # Middle vertically
        pyautogui.moveTo(cast_x, cast_y)
        
        # Click to focus game
        pyautogui.click()
        time.sleep(0.5)  # Wait for game to focus

        # Press and hold left click
        pyautogui.mouseDown()
        
        # Hold for 0.5 seconds
        time.sleep(0.5)
        
        # Release left click
        pyautogui.mouseUp()
        
        # Press the \ key
        keyboard.press_and_release('\\')
        
        self.casting = True
        
    def wait_for_shake_or_hook(self):
        """Wait for either a shake icon or the hooked state"""
        # First check if fish is hooked
        if self.detect_hooked():
            self.hooked = True
            return
            
        # Then check for shake icon
        screen = np.array(ImageGrab.grab())
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        
        # Perform template matching
        result = cv2.matchTemplate(screen, self.shake_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # If we found a good match (threshold of 0.5)
        if max_val > 0.3:
            pydirectinput.press('down')
            time.sleep(0.2)
            pydirectinput.press('enter')
        else:
            time.sleep(0.5)  # Wait a bit before checking again
                
    def detect_hooked(self):
        """Detect if the fish is hooked using template matching"""
        screen = np.array(ImageGrab.grab())
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        
        # Perform template matching
        result = cv2.matchTemplate(screen, self.hooked_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # If we found a good match (threshold of 0.5)
        is_hooked = max_val > 0.9
        return is_hooked
        
    def catch_fish(self):
        """Handle the fish catching minigame"""
        screen = np.array(ImageGrab.grab())
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        
        # Get the bottom region where the catching game is
        bottom_region = screen[-300:, :]
        
        # Perform template matching for fish
        result = cv2.matchTemplate(bottom_region, self.fish_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.5:  # If we found the fish
            # Get the center position of the fish
            fish_x = max_loc[0] + self.fish_template.shape[1] // 2
            screen_width = bottom_region.shape[1]
            screen_center = screen_width // 2
            
            # Calculate position relative to center
            relative_x = fish_x - screen_center
            print(f"Fish position relative to center: {relative_x}px")
            
            # If fish is more than 200px from the right of center, hold space
            if relative_x >= 0:
                print("Fish is at or right of center, holding space...")
                pydirectinput.keyDown('space')
                self.space_held = True
            else:
                if self.space_held:
                    print("Fish is left of center, releasing space...")
                    pydirectinput.keyUp('space')
                    self.space_held = False
        else:
            if self.space_held:
                print("No fish detected, releasing space...")
                pydirectinput.keyUp('space')  # Make sure to release space
                self.space_held = False
            self.reset_state()
                    
    def reset_state(self):
        """Reset the bot state after catching a fish"""
        self.casting = False
        self.hooked = False
        time.sleep(1)

if __name__ == "__main__":
    bot = FischBot()
    bot.start()
