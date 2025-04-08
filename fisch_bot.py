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
        self.last_space_press = 0  # Track last time space was pressed for pulsing
        self.space_state = False  # Track whether we're in the hold or release phase
        self.hold_duration = 1.0  # Duration to hold space
        self.release_duration = 0.35  # Duration to release space
        
        self.last_state_change_time = time.time() # Initialize state change timer
        # Load the template images
        self.shake_template = cv2.imread('Shake.png')
        self.hooked_template = cv2.imread('Hooked.png')
        self.hooked2_template = cv2.imread('Hooked2.png')
        self.fish1_template = cv2.imread('Fish1.png')
        self.fish2_template = cv2.imread('Fish2.png')
        self.fish3_template = cv2.imread('Fish3.png')
        self.fish4_template = cv2.imread('Fish4.png')
        self.fish5_template = cv2.imread('Fish5.png')
        self.bar_bad_template = cv2.imread('BarBad.png')
        self.bar_good_template = cv2.imread('BarGood.png')
        
        # Error checking for all templates
        templates = {
            'Shake.png': self.shake_template,
            'Hooked.png': self.hooked_template,
            'Hooked2.png': self.hooked2_template,
            'Fish1.png': self.fish1_template,
            'Fish2.png': self.fish2_template,
            'Fish3.png': self.fish3_template,
            'Fish4.png': self.fish4_template,
            'Fish5.png': self.fish5_template,
            'BarBad.png': self.bar_bad_template,
            'BarGood.png': self.bar_good_template
        }
        for name, template in templates.items():
            if template is None:
                raise FileNotFoundError(f"{name} not found. Please make sure the image is in the same directory as the script.")
        
        # Store fish templates and their names for easier iteration
        self.fish_templates = {
            "Fish1": self.fish1_template,
            "Fish2": self.fish2_template,
            "Fish3": self.fish3_template,
            "Fish4": self.fish4_template,
            "Fish5": self.fish5_template
        }
        
    def start(self):
        """Start the bot"""
        self.running = True
        self.last_state_change_time = time.time() # Initialize timer on start
        
        while self.running:
            # --- Inactivity Timeout Check ---
            current_time = time.time()
            if current_time - self.last_state_change_time > 30:
                print("Inactivity timer triggered (30 seconds). Resetting state.")
                self.reset_state()
                # Optional: add a small delay before next action
                time.sleep(1)
            # --- End Timeout Check ---
                
            if keyboard.is_pressed('q'):
                self.running = False
                break
                
            if not self.casting:
                self.cast_line()
            elif not self.hooked:
                self.wait_for_shake_or_hook()
            else:
                self.catch_fish()
                # Check if the hooked state has ended *after* trying to catch
                if self.hooked and not self.detect_hooked():
                    print("Hooked state ended, resetting...")
                    self.reset_state()
                
    def cast_line(self):
        """Cast the fishing line by holding left click for 0.5 seconds"""
        self.last_state_change_time = time.time() # Update timer: Starting cast
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
            self.last_state_change_time = time.time() # Update timer: Fish hooked
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
            time.sleep(0.125)
            pydirectinput.press('enter')
        else:
            time.sleep(0.125)  # Wait a bit before checking again
                
    def detect_hooked(self):
        """Detect if the fish is hooked using template matching for two templates."""
        screen = np.array(ImageGrab.grab())
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        
        # Perform template matching for the first hooked template
        result1 = cv2.matchTemplate(screen, self.hooked_template, cv2.TM_CCOEFF_NORMED)
        min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(result1)
        
        # Perform template matching for the second hooked template
        result2 = cv2.matchTemplate(screen, self.hooked2_template, cv2.TM_CCOEFF_NORMED)
        min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(result2)
        
        # If either template found a good match (threshold of 0.9)
        is_hooked = max_val1 > 0.9 or max_val2 > 0.9
        # Optional: Print confidence for debugging
        # print(f"Hooked detection confidence: Hooked1={max_val1:.3f}, Hooked2={max_val2:.3f}")
        return is_hooked
        
    def catch_fish(self):
        """Handle the fish catching minigame using absolute coordinates for search area."""
        screen_full = np.array(ImageGrab.grab())
        screen_full = cv2.cvtColor(screen_full, cv2.COLOR_RGB2BGR)
        screen_height, screen_width = screen_full.shape[:2]
        
        # Define the absolute coordinates for the fish/bar search area on the full screen
        crop_x1_abs = 1025
        crop_y1_abs = 1140
        crop_x2_abs = 2400
        crop_y2_abs = 1285

        # Ensure coordinates are within screen bounds
        crop_x1 = max(0, crop_x1_abs)
        crop_y1 = max(0, crop_y1_abs)
        crop_x2 = min(screen_width, crop_x2_abs)
        crop_y2 = min(screen_height, crop_y2_abs)

        # Ensure the crop dimensions are valid
        if crop_y1 >= crop_y2 or crop_x1 >= crop_x2:
            print(f"Invalid crop dimensions specified: ({crop_x1},{crop_y1}) to ({crop_x2},{crop_y2}).")
            if self.space_held:
                pydirectinput.keyUp('space')
                self.space_held = False
            self.reset_state()
            return
            
        # Crop the search area directly from the full screen
        search_area = screen_full[crop_y1:crop_y2, crop_x1:crop_x2]
        search_h, search_w = search_area.shape[:2]
        
        # Check if search area is large enough for all fish templates
        templates_too_large = []
        for name, template in self.fish_templates.items():
            template_h, template_w = template.shape[:2]
            if template_h > search_h or template_w > search_w:
                templates_too_large.append(name)
        
        if templates_too_large:
            #print(f"Search area ({search_h}x{search_w}) too small for templates: {", ".join(templates_too_large)}")
            if self.space_held:
                pydirectinput.keyUp('space')
                self.space_held = False
            self.reset_state()
            return

        # Perform template matching for all fish templates
        best_match_val = -1
        best_match_loc = None
        best_match_template_name = None
        best_match_template_dims = None

        for name, template in self.fish_templates.items():
            result = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            #print(f"  Checking {name}: Confidence={max_val:.3f}") # Debug print for each template
            if max_val > best_match_val:
                best_match_val = max_val
                best_match_loc = max_loc
                best_match_template_name = name
                best_match_template_dims = template.shape[:2] # (height, width)
        
        print(f"Best fish match: {best_match_template_name} with confidence {best_match_val:.3f}")

        if best_match_val > 0.75:  # If the best match is good enough
            template_h, template_w = best_match_template_dims
            # Calculate the absolute center position of the found fish on the screen
            # best_match_loc is relative to search_area, so add crop_x1
            fish_center_x_abs = crop_x1 + best_match_loc[0] + template_w // 2
            
            # Debug: Move mouse to detected fish center X (using a fixed Y for visualization)
            pyautogui.moveTo(fish_center_x_abs, 1225) 

            # Calculate position relative to the screen's horizontal center
            screen_center_x = screen_width // 2
            relative_x = fish_center_x_abs - screen_center_x
            #print(f"Fish absolute center: {fish_center_x_abs}, Relative to screen center: {relative_x}px")
            print(f"Fish relative to screen center: {relative_x}px")

            # --- Keep the existing spacebar control logic based on relative_x ---
            if relative_x >= 0:
                if not self.space_held:
                    pydirectinput.keyDown('space')
                    self.space_held = True
            elif -200 <= relative_x < 0:
                current_time = time.time()
                interval = self.hold_duration if self.space_state else self.release_duration
                if current_time - self.last_space_press >= interval:
                    if self.space_state:
                        pydirectinput.keyUp('space')
                        self.space_held = False
                    else:
                        pydirectinput.keyDown('space')
                        self.space_held = True
                    self.space_state = not self.space_state
                    self.last_space_press = current_time
            else:
                if self.space_held:
                    pydirectinput.keyUp('space')
                    self.space_held = False
            # --- End of spacebar control logic ---
                    
        else: # No fish detected in search area this frame
            # Release space if held, but don't reset state immediately
            #print(f"Fish detection confidence: {best_match_val:.3f}")
            if self.space_held:
                pydirectinput.keyUp('space')
                self.space_held = False
                    
    def reset_state(self):
        """Reset the bot state after catching a fish or timeout"""
        self.last_state_change_time = time.time() # Update timer: State reset
        pydirectinput.keyUp('space')
        self.casting = False
        self.hooked = False
        time.sleep(.25)

if __name__ == "__main__":
    bot = FischBot()
    bot.start()
