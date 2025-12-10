import time
import board
import busio
import random
import digitalio
import neopixel
import pwmio
from rotary_encoder import RotaryEncoder
import adafruit_adxl34x

# =============================================================================
# Buzzer Class
# =============================================================================
# Used to play various game sound effects including clicks, button sounds, 
# startup music, win/lose sound effects, etc.
# =============================================================================
class Buzzer:
    # -------------------------------------------------------------------------
    # Initialize the buzzer
    # -------------------------------------------------------------------------
    # Parameter pin: The pin that the buzzer is connected to
    # 
    # Uses PWM (Pulse Width Modulation) to control the buzzer sound
    # Initial frequency set to 440Hz (standard A note), duty cycle 0 (silent)
    # -------------------------------------------------------------------------
    def __init__(self, pin):
        self.pwm = pwmio.PWMOut(pin, frequency=440, duty_cycle=0, variable_frequency=True)
    
    # -------------------------------------------------------------------------
    # Play a single tone
    # -------------------------------------------------------------------------
    # Parameter freq: Frequency in Hz, determines the pitch
    # Parameter dur: Duration in seconds
    # 
    # How it works:
    # 1. If frequency > 0, set PWM frequency and duty cycle to 50% (32768/65535)
    # 2. Wait for the specified duration
    # 3. Set duty cycle to 0 to stop the sound
    # -------------------------------------------------------------------------
    def tone(self, freq, dur):
        if freq > 0:
            self.pwm.frequency = freq      # Set frequency
            self.pwm.duty_cycle = 32768    # 50% duty cycle to produce sound
            time.sleep(dur)                # Wait for duration
        self.pwm.duty_cycle = 0            # Stop sound
    
    # -------------------------------------------------------------------------
    # Click sound effect
    # -------------------------------------------------------------------------
    # Used for feedback sound when rotating the encoder
    # High frequency, short "click" sound
    # -------------------------------------------------------------------------
    def click(self):
        self.tone(1200, 0.015)  # 1200Hz, 15 milliseconds
    
    # -------------------------------------------------------------------------
    # Button press sound effect
    # -------------------------------------------------------------------------
    # Used for confirmation sound when pressing a button
    # Two consecutive tones, low to high, gives a "confirmation" feeling
    # -------------------------------------------------------------------------
    def btn(self):
        self.tone(800, 0.03)   # First low tone
        self.tone(1200, 0.03)  # Then high tone
    
    # -------------------------------------------------------------------------
    # Startup sound effect
    # -------------------------------------------------------------------------
    # Welcome music played when the game starts
    # Three ascending tones: C5(523Hz) -> E5(659Hz) -> G5(784Hz)
    # Forms a pleasant major triad arpeggio
    # -------------------------------------------------------------------------
    def startup(self):
        for f in [523, 659, 784]:
            self.tone(f, 0.1)  # Each note 100 milliseconds
    
    # -------------------------------------------------------------------------
    # Victory sound effect
    # -------------------------------------------------------------------------
    # Celebration music played when player wins
    # Four ascending tones, one octave higher C than startup
    # C5 -> E5 -> G5 -> C6(1047Hz)
    # -------------------------------------------------------------------------
    def win(self):
        for f in [523, 659, 784, 1047]:
            self.tone(f, 0.15)  # Each note 150ms, longer than startup
    
    # -------------------------------------------------------------------------
    # Lose sound effect
    # -------------------------------------------------------------------------
    # Sad/low sound effect played when game is over
    # Three descending tones: E4(330Hz) -> D4(294Hz) -> C4(262Hz)
    # Gives a feeling of disappointment and loss
    # -------------------------------------------------------------------------
    def lose(self):
        for f in [330, 294, 262]:
            self.tone(f, 0.25)  # Each note 250ms, slow and low
    
    # -------------------------------------------------------------------------
    # Treasure found sound effect
    # -------------------------------------------------------------------------
    # Happy notification sound when digging up treasure
    # Two quick ascending tones, indicating something good was found
    # -------------------------------------------------------------------------
    def found(self):
        self.tone(659, 0.08)  # E5 note, 80ms
        self.tone(784, 0.1)   # G5 note, 100ms
    
    # -------------------------------------------------------------------------
    # Bomb explosion sound effect
    # -------------------------------------------------------------------------
    # Warning sound effect when digging up a bomb
    # Three quick descending low-frequency tones, simulating explosion
    # -------------------------------------------------------------------------
    def bomb(self):
        for f in [400, 300, 200]:
            self.tone(f, 0.1)  # Each note 100ms
    
    # -------------------------------------------------------------------------
    # Time warning sound effect
    # -------------------------------------------------------------------------
    # Reminder sound when time is running out
    # Single medium-frequency short tone
    # -------------------------------------------------------------------------
    def warn(self):
        self.tone(800, 0.1)  # 800Hz, 100ms
    
    # -------------------------------------------------------------------------
    # Disarm success sound effect
    # -------------------------------------------------------------------------
    # Played when bomb is successfully disarmed
    # Quick ascending chirp indicating success
    # -------------------------------------------------------------------------
    def disarm_success(self):
        for f in [600, 800, 1000]:
            self.tone(f, 0.06)
    
    # -------------------------------------------------------------------------
    # Ticking sound effect
    # -------------------------------------------------------------------------
    # Played during bomb disarm sequence
    # Short tick sound
    # -------------------------------------------------------------------------
    def tick(self):
        self.tone(1000, 0.03)


# =============================================================================
# OLED Display Driver Class (SSD1306)
# =============================================================================
# This is a simplified SSD1306 OLED display driver
# Resolution: 128x64 pixels, using I2C communication protocol
# 
# Display principle:
# - Screen is divided into 8 "pages", each page has 8 rows of pixels
# - Each byte controls 8 pixels in a column (vertical direction)
# - Buffer size = 128 columns × 8 pages = 1024 bytes
# =============================================================================
class SSD1306:
    # -------------------------------------------------------------------------
    # Initialize the display
    # -------------------------------------------------------------------------
    # Parameter i2c: I2C bus object
    # 
    # Initialization steps:
    # 1. Save I2C reference and device address (0x3C is SSD1306 default)
    # 2. Create 1024-byte display buffer
    # 3. Send series of initialization commands to configure display
    # 4. Clear the screen
    # -------------------------------------------------------------------------
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = 0x3C           # I2C address
        self.buf = bytearray(1024) # Display buffer
        time.sleep(0.1)            # Wait for display ready
        
        # Initialization command sequence
        # These commands configure various display parameters
        for c in [
            0xAE,  # Display OFF
            0xD5,  # Set display clock divide ratio
            0x80,  # Clock divide value
            0xA8,  # Set multiplex ratio
            0x3F,  # 64 rows (64-1=63=0x3F)
            0xD3,  # Set display offset
            0x00,  # No offset
            0x40,  # Set start line
            0x8D,  # Charge pump setting
            0x14,  # Enable charge pump
            0x20,  # Set memory addressing mode
            0x00,  # Horizontal addressing mode
            0xA1,  # Segment re-map
            0xC8,  # COM output scan direction
            0xDA,  # COM pins configuration
            0x12,  # Alternate COM configuration
            0x81,  # Set contrast
            0xCF,  # Contrast value
            0xD9,  # Set pre-charge period
            0xF1,  # Pre-charge value
            0xDB,  # Set VCOMH voltage
            0x40,  # VCOMH value
            0xA4,  # Display follows RAM content
            0xA6,  # Normal display (not inverted)
            0xAF   # Display ON
        ]:
            self._cmd(c)
        self.clear()  # Clear buffer
    
    # -------------------------------------------------------------------------
    # Send command to display
    # -------------------------------------------------------------------------
    # Parameter c: Command byte to send
    # 
    # Sends command via I2C with retry mechanism for communication errors
    # Command format: [0x00 (command identifier), command byte]
    # -------------------------------------------------------------------------
    def _cmd(self, c):
        for _ in range(3):  # Retry up to 3 times
            try:
                while not self.i2c.try_lock():  # Acquire I2C bus lock
                    pass
                try:
                    # Send command: 0x00 indicates command, c is the actual command
                    self.i2c.writeto(self.addr, bytes([0, c]))
                    return
                finally:
                    self.i2c.unlock()  # Release I2C bus lock
            except OSError:
                time.sleep(0.01)  # Wait briefly before retry on error
    
    # -------------------------------------------------------------------------
    # Clear display buffer
    # -------------------------------------------------------------------------
    # Sets all pixels to 0 (black/off)
    # -------------------------------------------------------------------------
    def clear(self):
        for i in range(1024):
            self.buf[i] = 0
    
    # -------------------------------------------------------------------------
    # Fill entire screen
    # -------------------------------------------------------------------------
    # Parameter c: Color value, 0=black, non-zero=white
    # -------------------------------------------------------------------------
    def fill(self, c):
        v = 255 if c else 0  # If c is true, fill with 255
        for i in range(1024):
            self.buf[i] = v
    
    # -------------------------------------------------------------------------
    # Set a single pixel
    # -------------------------------------------------------------------------
    # Parameter x: X coordinate (0-127)
    # Parameter y: Y coordinate (0-63)
    # Parameter c: Color, 0=off, non-zero=on
    # 
    # Calculation principle:
    # - Buffer index = x + (y // 8) * 128
    #   (y // 8 gives page number, 128 bytes per page)
    # - Bit position = y % 8 (position within byte)
    # -------------------------------------------------------------------------
    def px(self, x, y, c):
        if 0 <= x < 128 and 0 <= y < 64:  # Boundary check
            i = x + (y // 8) * 128        # Calculate buffer index
            if c:
                self.buf[i] |= 1 << (y % 8)   # Set bit (turn on pixel)
            else:
                self.buf[i] &= ~(1 << (y % 8)) # Clear bit (turn off pixel)
    
    # -------------------------------------------------------------------------
    # Draw hollow rectangle
    # -------------------------------------------------------------------------
    # Parameter x, y: Top-left corner coordinates
    # Parameter w, h: Width and height
    # Parameter c: Color
    # 
    # Only draws the four edges of the rectangle
    # -------------------------------------------------------------------------
    def rect(self, x, y, w, h, c):
        # Draw top and bottom horizontal edges
        for i in range(w):
            self.px(x + i, y, c)         # Top edge
            self.px(x + i, y + h - 1, c) # Bottom edge
        # Draw left and right vertical edges
        for i in range(h):
            self.px(x, y + i, c)         # Left edge
            self.px(x + w - 1, y + i, c) # Right edge
    
    # -------------------------------------------------------------------------
    # Draw filled rectangle
    # -------------------------------------------------------------------------
    # Parameter x, y: Top-left corner coordinates
    # Parameter w, h: Width and height
    # Parameter c: Color
    # 
    # Fills the entire rectangular area
    # -------------------------------------------------------------------------
    def frect(self, x, y, w, h, c):
        for j in range(h):        # Iterate through each row
            for i in range(w):    # Iterate through each column
                self.px(x + i, y + j, c)
    
    # -------------------------------------------------------------------------
    # Draw horizontal line
    # -------------------------------------------------------------------------
    # Parameter x, y: Starting point coordinates
    # Parameter w: Line length
    # Parameter c: Color
    # -------------------------------------------------------------------------
    def hline(self, x, y, w, c):
        for i in range(w):
            self.px(x + i, y, c)
    
    # -------------------------------------------------------------------------
    # Draw text
    # -------------------------------------------------------------------------
    # Parameter s: String to display
    # Parameter x, y: Starting coordinates
    # Parameter c: Color
    # 
    # Uses built-in 5x8 pixel font
    # Each character uses 5 pixel columns, with 1 pixel spacing between characters
    # 
    # Font data format: Each character is 5 bytes, each byte is 8 pixels in a column
    # -------------------------------------------------------------------------
    def txt(self, s, x, y, c):
        # Font definition: 5 columns per character, 8 bits per column (8 pixels high)
        F = {
            '0':[0x3E,0x51,0x49,0x45,0x3E], '1':[0,0x42,0x7F,0x40,0],
            '2':[0x42,0x61,0x51,0x49,0x46], '3':[0x21,0x41,0x45,0x4B,0x31],
            '4':[0x18,0x14,0x12,0x7F,0x10], '5':[0x27,0x45,0x45,0x45,0x39],
            '6':[0x3C,0x4A,0x49,0x49,0x30], '7':[1,0x71,9,5,3],
            '8':[0x36,0x49,0x49,0x49,0x36], '9':[6,0x49,0x49,0x29,0x1E],
            'A':[0x7E,0x11,0x11,0x11,0x7E], 'B':[0x7F,0x49,0x49,0x49,0x36],
            'C':[0x3E,0x41,0x41,0x41,0x22], 'D':[0x7F,0x41,0x41,0x22,0x1C],
            'E':[0x7F,0x49,0x49,0x49,0x41], 'F':[0x7F,9,9,9,1],
            'G':[0x3E,0x41,0x49,0x49,0x7A], 'H':[0x7F,8,8,8,0x7F],
            'I':[0,0x41,0x7F,0x41,0],       'K':[0x7F,8,0x14,0x22,0x41],
            'L':[0x7F,0x40,0x40,0x40,0x40], 'M':[0x7F,2,0xC,2,0x7F],
            'N':[0x7F,4,8,0x10,0x7F],       'O':[0x3E,0x41,0x41,0x41,0x3E],
            'P':[0x7F,9,9,9,6],             'R':[0x7F,9,0x19,0x29,0x46],
            'S':[0x46,0x49,0x49,0x49,0x31], 'T':[1,1,0x7F,1,1],
            'U':[0x3F,0x40,0x40,0x40,0x3F], 'V':[0x1F,0x20,0x40,0x20,0x1F],
            'W':[0x3F,0x40,0x38,0x40,0x3F], 'X':[0x63,0x14,8,0x14,0x63],
            'Y':[7,8,0x70,8,7],             ' ':[0,0,0,0,0],
            '!':[0,0,0x5F,0,0],             '?':[2,1,0x51,9,6],
            ':':[0,0x36,0x36,0,0],          '-':[8,8,8,8,8],
            '>':[8,0x14,0x22,0x41,0],       '/':[0x20,0x10,8,4,2],
            '+':[8,8,0x3E,8,8],             '.':[0,0x60,0x60,0,0]
        }
        cx = x  # Current drawing position
        for ch in s:
            uc = ch.upper()  # Convert to uppercase
            if uc in F:
                for col in F[uc]:      # Iterate through each column
                    for r in range(8): # Iterate through each pixel in column
                        if col & (1 << r):  # Check if bit is set
                            self.px(cx, y + r, c)
                    cx += 1
                cx += 1  # Character spacing
    
    # -------------------------------------------------------------------------
    # Draw treasure chest icon
    # -------------------------------------------------------------------------
    # Parameter x, y: Top-left corner coordinates
    # Parameter op: Whether open, True=open, False=closed
    # 
    # Chest consists of body and lock, open state also shows sparkles
    # -------------------------------------------------------------------------
    def chest(self, x, y, op=False):
        # Draw chest body (bottom part)
        self.rect(x, y + 4, 16, 8, 1)      # Main body outline
        self.hline(x + 4, y + 8, 8, 1)     # Bottom decoration line
        self.frect(x + 6, y + 6, 4, 3, 1)  # Lock clasp
        
        if op:  # Open state
            # Draw open lid
            self.hline(x + 2, y, 12, 1)        # Lid top
            self.hline(x + 1, y + 1, 14, 1)    # Lid second row
            self.rect(x, y + 2, 16, 3, 1)      # Lid bottom
            # Draw treasure sparkles
            for i in range(3):
                self.px(x + 8, y - 2 - i, 1)   # Center sparkle
            self.px(x + 6, y - 1, 1)           # Left sparkle
            self.px(x + 10, y - 1, 1)          # Right sparkle
        else:  # Closed state
            self.rect(x, y, 16, 5, 1)          # Lid
            self.hline(x + 4, y + 2, 8, 1)     # Lid center line
    
    # -------------------------------------------------------------------------
    # Draw bomb icon
    # -------------------------------------------------------------------------
    # Parameter x, y: Top-left corner coordinates
    # 
    # Bomb consists of circular body and fuse
    # -------------------------------------------------------------------------
    def bomb(self, x, y):
        # Draw circular bomb body (using circle equation)
        for dy in range(8):
            for dx in range(8):
                # Check if point is inside circle: (x-cx)² + (y-cy)² <= r²
                if (dx - 4) ** 2 + (dy - 4) ** 2 <= 16:
                    self.px(x + dx + 2, y + dy + 6, 1)
        
        # Draw fuse
        self.frect(x + 4, y + 3, 4, 4, 1)  # Fuse base
        self.px(x + 6, y + 2, 1)            # Fuse
        self.px(x + 7, y + 1, 1)            # Fuse bent part
        self.px(x + 8, y, 1)                # Fuse bent part
        self.px(x + 9, y, 1)                # Spark
        self.px(x + 8, y - 1, 1)            # Spark
    
    # -------------------------------------------------------------------------
    # Display buffer contents to screen
    # -------------------------------------------------------------------------
    # This is the function that actually updates the display
    # 
    # Steps:
    # 1. Set column address range (0-127)
    # 2. Set page address range (0-7)
    # 3. Send buffer data (16 bytes at a time)
    # -------------------------------------------------------------------------
    def show(self):
        for retry in range(3):  # Retry mechanism
            try:
                # Set display area
                self._cmd(0x21)  # Set column address
                self._cmd(0)     # Start column
                self._cmd(127)   # End column
                self._cmd(0x22)  # Set page address
                self._cmd(0)     # Start page
                self._cmd(7)     # End page
                
                # Send display data
                while not self.i2c.try_lock():
                    pass
                try:
                    # Send buffer in chunks (16 bytes each)
                    for i in range(0, 1024, 16):
                        # 0x40 indicates data (not command)
                        self.i2c.writeto(self.addr, b'\x40' + self.buf[i:i + 16])
                    return
                finally:
                    self.i2c.unlock()
            except OSError:
                time.sleep(0.02)


# =============================================================================
# Main Game Class
# =============================================================================
# This is the core game control class, managing all game logic, state and user interaction
# 
# Game flow:
# 1. MENU: Select difficulty
# 2. PLAY: 9 levels of treasure hunting
# 3. LV10: Final level - pick one of two chests
# 4. WIN (victory) or OVER (game over)
# =============================================================================
class Game:
    # Global Y offset, moves all content down 4 pixels to avoid top being cut off
    OFS = 4
    
    # -------------------------------------------------------------------------
    # Initialize the game
    # -------------------------------------------------------------------------
    # Sets up all hardware and initial game state
    # -------------------------------------------------------------------------
    def __init__(self):
        # ===================== Hardware Initialization =====================
        
        # Initialize I2C bus (for OLED display and accelerometer)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        time.sleep(0.1)  # Wait for I2C to stabilize
        
        # OLED Display
        self.dsp = SSD1306(self.i2c)
        
        # Accelerometer (ADXL345)
        self.accel = adafruit_adxl34x.ADXL345(self.i2c)
        
        # Rotary encoder (for cursor movement)
        # D0, D1: Encoder signal pins
        # debounce_ms: Debounce delay
        # pulses_per_detent: Pulses per detent
        self.enc = RotaryEncoder(board.D0, board.D1, debounce_ms=1, pulses_per_detent=2)
        
        # Encoder button (D2 pin)
        # Using pull-up resistor, low when pressed
        self.ebtn = digitalio.DigitalInOut(board.D2)
        self.ebtn.direction = digitalio.Direction.INPUT
        self.ebtn.pull = digitalio.Pull.UP
        self.ebl = True  # Last button state
        
        # Separate button (D7 pin)
        self.btn = digitalio.DigitalInOut(board.D7)
        self.btn.direction = digitalio.Direction.INPUT
        self.btn.pull = digitalio.Pull.UP
        self.bl = True  # Last button state
        
        # RGB LED (D8 pin)
        # Used to display game state (HP, treasure found, etc.)
        self.led = neopixel.NeoPixel(board.D8, 1, brightness=0.3)
        
        # Buzzer (D9 pin)
        self.buz = Buzzer(board.D9)
        
        # ===================== Game State Variables =====================
        
        self.lbt = 0       # Last button time (for debounce)
        self.st = 'MENU'   # Current game state
        self.df = 0        # Currently selected difficulty
        self.lv = 1        # Current level
        self.hp = 6        # Current health points
        self.sc = 0        # Current score
        
        # ===================== Shake Event Variables =====================
        
        self.shake_event_available = False  # One event per level in easy mode
        self.bomb_disarm_active = False     # Whether player is currently disarming
        self.shake_threshold = 2.0          # Acceleration threshold for shake (m/s²)
        self.shake_start_time = 0           # When disarm started
        self.shake_duration = 3.0           # 3 seconds to shake and disarm
        self.last_tick_time = 0             # For ticking sound effect
        
        # ===================== Difficulty Configuration =====================
        # n: Difficulty name
        # hp: Initial HP
        # t: Time limit per level (seconds)
        # h10: Final level HP
        # t10: Final level time limit
        self.cfg = {
            0: {'n': 'EASY', 'hp': 6, 't': 60, 'h10': 2, 't10': 30},  # Easy
            1: {'n': 'MED', 'hp': 4, 't': 30, 'h10': 2, 't10': 15},   # Medium
            2: {'n': 'HARD', 'hp': 2, 't': 15, 'h10': 1, 't10': 15}   # Hard
        }
        
        # ===================== Level Configuration =====================
        # Format: (rows, columns, treasures, bombs, treasures needed to clear)
        self.lvl = {
            1: (2, 2, 2, 1, 1),  # Level 1: 2x2 grid, 2 treasures, 1 bomb, find 1 to clear
            2: (2, 3, 3, 2, 2),  # Level 2: 2x3 grid, 3 treasures, 2 bombs, find 2 to clear
            3: (2, 3, 3, 2, 2),
            4: (3, 3, 4, 3, 2),
            5: (3, 3, 4, 3, 3),
            6: (3, 4, 5, 4, 3),
            7: (3, 4, 5, 5, 3),
            8: (4, 4, 6, 5, 4),
            9: (4, 4, 6, 6, 4)   # Hardest level: 4x4 grid
        }
        
        # ===================== In-game State =====================
        
        self.grd = []      # Game grid (stores treasure T and bomb B positions)
        self.rev = []      # Revealed cells
        self.pos = [0, 0]  # Current cursor position [row, col]
        self.fnd = 0       # Treasures found
        self.stm = 0       # Level start time
        self.tlm = 60      # Current time limit
        self.fch = 0       # Final level choice (0 or 1)
        self.fhp = 2       # Final level HP
    
    # -------------------------------------------------------------------------
    # Check if device is being shaken
    # -------------------------------------------------------------------------
    # Returns: True if shake detected, False otherwise
    # 
    # Calculates magnitude of acceleration and compares to threshold
    # -------------------------------------------------------------------------
    def check_shake(self):
        try:
            x, y, z = self.accel.acceleration
            # Calculate total acceleration magnitude
            magnitude = (x**2 + y**2 + z**2)**0.5
            
            # Check if magnitude significantly exceeds gravity (9.8 m/s²)
            # This indicates shaking motion
            if magnitude > (9.8 + self.shake_threshold):
                return True
        except:
            pass  # Ignore sensor errors
        return False
    
    # -------------------------------------------------------------------------
    # Display disarm prompt
    # -------------------------------------------------------------------------
    # Shows shake instruction and countdown timer
    # -------------------------------------------------------------------------
    def display_disarm_prompt(self):
        self.dsp.clear()
        
        # Show bomb icon
        self.dsp.bomb(52, 8)
        
        # Show instruction
        self.dsp.txt("SHAKE TO", 32, 30, 1)
        self.dsp.txt("DISARM!", 38, 42, 1)
        
        # Show countdown
        elapsed = time.monotonic() - self.shake_start_time
        time_left = self.shake_duration - elapsed
        self.dsp.txt("{:.1f}S".format(max(0, time_left)), 50, 54, 1)
        
        self.dsp.show()
    
    # -------------------------------------------------------------------------
    # Check button press
    # -------------------------------------------------------------------------
    # Returns: True if either button was pressed, False otherwise
    # 
    # Uses edge detection: only triggers when button changes from not pressed to pressed
    # Includes 200ms debounce delay
    # -------------------------------------------------------------------------
    def cbtn(self):
        now = time.monotonic()
        
        # Debounce: ignore if less than 200ms since last press
        if now - self.lbt < 0.2:
            return False
        
        pr = False  # Whether press detected
        
        # Check encoder button
        e = self.ebtn.value  # Current state
        if self.ebl and not e:  # High to low (pressed)
            pr = True
        self.ebl = e  # Save current state
        
        # Check separate button
        b = self.btn.value
        if self.bl and not b:
            pr = True
        self.bl = b
        
        # If press detected, update time and play sound
        if pr:
            self.lbt = now
            self.buz.btn()
        
        return pr
    
    # -------------------------------------------------------------------------
    # Read rotary encoder
    # -------------------------------------------------------------------------
    # Returns: 1=clockwise, -1=counter-clockwise, 0=no change
    # -------------------------------------------------------------------------
    def renc(self):
        self.enc.update()        # Update encoder state
        d = self.enc.get_delta() # Get change amount
        
        if d > 0:               # Clockwise
            self.buz.click()
            return 1
        if d < 0:               # Counter-clockwise
            self.buz.click()
            return -1
        return 0                # No change
    
    # -------------------------------------------------------------------------
    # Main game loop
    # -------------------------------------------------------------------------
    # Entry point of the game, calls appropriate handler based on current state
    # -------------------------------------------------------------------------
    def run(self):
        self.welcome()  # Show welcome screen
        
        while True:
            if self.st == 'MENU':    # Main menu
                self.menu()
            elif self.st == 'PLAY':  # Game in progress
                self.play()
            elif self.st == 'LV10':  # Final level
                self.lv10()
            elif self.st == 'OVER':  # Game over
                self.over()
            elif self.st == 'WIN':   # Game won
                self.win()
    
    # -------------------------------------------------------------------------
    # Welcome screen
    # -------------------------------------------------------------------------
    # Displays animated game title and icons, waits for player to press button to start
    # -------------------------------------------------------------------------
    def welcome(self):
        # ===== Animation Phase 1: Title fade in =====
        for brightness in range(0, 2):  # Two brightness levels
            self.dsp.clear()
            
            # Display game title
            self.dsp.txt("TREASURE", 25, 10 + self.OFS, 1)
            self.dsp.txt("HUNT", 45, 22 + self.OFS, 1)
            
            self.dsp.show()
            time.sleep(0.2)
        
        # ===== Animation Phase 2: Chest opening animation =====
        self.led.fill((255, 215, 0))  # Gold LED
        self.buz.startup()            # Play startup music
        
        # Animate chest opening
        for frame in range(3):
            self.dsp.clear()
            
            # Title stays
            self.dsp.txt("TREASURE", 25, 10 + self.OFS, 1)
            self.dsp.txt("HUNT", 45, 22 + self.OFS, 1)
            
            # Chest animation: closed -> partially open -> fully open
            if frame == 0:
                self.dsp.chest(25, 38, False)  # Closed
            elif frame == 1:
                # Draw partially open chest (custom)
                self.dsp.rect(25, 38 + 4, 16, 8, 1)      # Body
                self.dsp.hline(25 + 4, 38 + 8, 8, 1)     # Bottom line
                self.dsp.frect(25 + 6, 38 + 6, 4, 3, 1)  # Lock
                self.dsp.hline(25 + 2, 38 + 1, 12, 1)    # Lid partially open
                self.dsp.rect(25, 38 + 2, 16, 3, 1)
                self.dsp.px(25 + 8, 38 - 1, 1)           # Small sparkle
            else:
                self.dsp.chest(25, 38, True)   # Fully open
            
            # Bomb icon (static for now)
            self.dsp.bomb(85, 36)
            
            self.dsp.show()
            time.sleep(0.4)
        
        # ===== Animation Phase 3: Sparkle and bomb fuse animation =====
        for frame in range(5):
            self.dsp.clear()
            
            # Title
            self.dsp.txt("TREASURE", 25, 10 + self.OFS, 1)
            self.dsp.txt("HUNT", 45, 22 + self.OFS, 1)
            
            # Open chest with sparkles
            self.dsp.chest(25, 38, True)
            
            # Animated bomb fuse (alternating spark positions)
            bomb_x, bomb_y = 85, 36
            
            # Draw bomb body
            for dy in range(8):
                for dx in range(8):
                    if (dx - 4) ** 2 + (dy - 4) ** 2 <= 16:
                        self.dsp.px(bomb_x + dx + 2, bomb_y + dy + 6, 1)
            
            # Draw fuse base
            self.dsp.frect(bomb_x + 4, bomb_y + 3, 4, 4, 1)
            self.dsp.px(bomb_x + 6, bomb_y + 2, 1)
            self.dsp.px(bomb_x + 7, bomb_y + 1, 1)
            self.dsp.px(bomb_x + 8, bomb_y, 1)
            
            # Animated spark (blinks on and off)
            if frame % 2 == 0:
                self.dsp.px(bomb_x + 9, bomb_y, 1)
                self.dsp.px(bomb_x + 8, bomb_y - 1, 1)
                self.dsp.px(bomb_x + 10, bomb_y - 1, 1)  # Extra spark
            else:
                self.dsp.px(bomb_x + 9, bomb_y, 1)
                self.dsp.px(bomb_x + 8, bomb_y - 1, 1)
            
            self.dsp.show()
            
            # Pulse LED color between gold and orange
            if frame % 2 == 0:
                self.led.fill((255, 215, 0))  # Gold
            else:
                self.led.fill((255, 140, 0))  # Orange
            
            time.sleep(0.15)
        
        # ===== Final state: Show press button prompt =====
        self.dsp.clear()
        self.dsp.txt("TREASURE", 25, 10 + self.OFS, 1)
        self.dsp.txt("HUNT", 45, 22 + self.OFS, 1)
        self.dsp.chest(25, 38, True)   # Open chest
        self.dsp.bomb(85, 36)           # Bomb
        self.dsp.txt("PRESS BTN", 28, 54, 1)
        self.dsp.show()
        
        self.led.fill((0, 255, 0))  # Green LED to indicate ready
        
        # Clear encoder buffer (avoid accumulated rotation affecting)
        for _ in range(10):
            self.enc.update()
            self.enc.get_delta()
            self.ebl = self.ebtn.value
            self.bl = self.btn.value
            time.sleep(0.05)
        
        # ===== Wait for player to press button with pulsing LED =====
        start_wait = time.monotonic()
        while not self.cbtn():
            self.enc.update()
            
            # Pulsing green LED effect while waiting
            elapsed = time.monotonic() - start_wait
            pulse = int(50 + 205 * abs((elapsed % 1.0) - 0.5) * 2)
            self.led.fill((0, pulse, 0))
            
            time.sleep(0.01)
        
        self.led.fill((0, 0, 0))  # Turn off LED
        self.st = 'MENU'  # Enter menu state
    
    # -------------------------------------------------------------------------
    # Main menu
    # -------------------------------------------------------------------------
    # Lets player select game difficulty
    # -------------------------------------------------------------------------
    def menu(self):
        rd = True  # Whether redraw is needed
        col = [(0, 255, 0), (255, 255, 0), (255, 0, 0)]  # LED colors for each difficulty
        le = 0     # Last encoder change time
        
        while self.st == 'MENU':
            now = time.monotonic()
            
            # Read encoder and update selection
            d = self.renc()
            if d and now - le > 0.15:  # 150ms debounce
                self.df = (self.df + d) % 3  # Cycle between 0-2
                rd = True
                le = now
            
            # Redraw menu if needed
            if rd:
                self.dsp.clear()
                self.dsp.txt("SELECT MODE", 20, 2 + self.OFS, 1)
                self.dsp.hline(5, 11 + self.OFS, 118, 1)  # Separator line
                
                # Difficulty options
                nm = ["EASY 6HP", "MED 4HP", "HARD 2HP"]  # Display name and HP
                tm = ["60S", "30S", "15S"]                # Time limits
                
                for i in range(3):
                    y = 16 + i * 14 + self.OFS
                    if i == self.df:  # Currently selected item
                        self.dsp.txt(">", 5, y, 1)        # Selection indicator
                        self.dsp.txt(nm[i], 15, y, 1)
                        self.dsp.txt(tm[i], 95, y, 1)
                    else:
                        self.dsp.txt(nm[i], 15, y, 1)
                
                self.dsp.txt("BTN START", 30, 56, 1)  # Start prompt
                self.dsp.show()
                self.led.fill(col[self.df])  # Set LED color based on difficulty
                rd = False
            
            # Check button press to start game
            if self.cbtn():
                self.start()
                break
            
            time.sleep(0.01)
    
    # -------------------------------------------------------------------------
    # Start new game
    # -------------------------------------------------------------------------
    # Initializes game state and shows ready screen
    # -------------------------------------------------------------------------
    def start(self):
        c = self.cfg[self.df]  # Get current difficulty config
        
        # Initialize game state
        self.hp = c['hp']      # Set HP
        self.tlm = c['t']      # Set time limit
        self.lv = 1            # Reset level
        self.sc = 0            # Reset score
        
        # Show ready screen
        self.dsp.clear()
        self.dsp.txt(c['n'], 50, 22 + self.OFS, 1)      # Difficulty name
        self.dsp.txt("GET READY", 28, 35 + self.OFS, 1) # Ready prompt
        self.dsp.show()
        time.sleep(1)
        
        self.st = 'PLAY'  # Enter play state
    
    # -------------------------------------------------------------------------
    # Shuffle algorithm (Fisher-Yates)
    # -------------------------------------------------------------------------
    # Parameter l: List to shuffle
    # Returns: Shuffled list
    # 
    # Uses Fisher-Yates algorithm for in-place shuffle
    # -------------------------------------------------------------------------
    def shuf(self, l):
        for i in range(len(l) - 1, 0, -1):  # Iterate backwards
            j = random.randint(0, i)        # Random position 0 to i
            l[i], l[j] = l[j], l[i]         # Swap
        return l
    
    # -------------------------------------------------------------------------
    # Initialize current level
    # -------------------------------------------------------------------------
    # Generates game grid based on level config, randomly places treasures and bombs
    # -------------------------------------------------------------------------
    def ilvl(self):
        c = self.cfg[self.df]
        self.hp = c['hp']     # Reset HP
        self.tlm = c['t']     # Reset time limit
        
        # Reset shake event for easy mode
        if self.df == 0:  # Easy mode
            self.shake_event_available = True
        else:
            self.shake_event_available = False
        
        # Get level configuration
        r, co, tr, bm, _ = self.lvl[self.lv]  # rows, cols, treasures, bombs, needed
        
        # Create empty grid
        self.grd = [[' '] * co for _ in range(r)]    # Game grid
        self.rev = [[False] * co for _ in range(r)]  # Revealed state
        
        # Generate all positions and shuffle
        ps = [(i, j) for i in range(r) for j in range(co)]
        ps = self.shuf(ps)
        
        # Place treasures
        for i in range(tr):
            self.grd[ps[i][0]][ps[i][1]] = 'T'
        
        # Place bombs
        for i in range(tr, tr + bm):
            self.grd[ps[i][0]][ps[i][1]] = 'B'
        
        # Reset game state
        self.pos = [0, 0]              # Reset cursor
        self.fnd = 0                   # Reset treasures found
        self.stm = time.monotonic()    # Record start time
        self.bomb_disarm_active = False  # Reset disarm state
    
    # -------------------------------------------------------------------------
    # Main game logic
    # -------------------------------------------------------------------------
    # Handles game logic for levels 1-9
    # -------------------------------------------------------------------------
    def play(self):
        # Show level start screen
        self.dsp.clear()
        self.dsp.txt("LEVEL {}".format(self.lv), 38, 28, 1)
        self.dsp.show()
        time.sleep(0.8)
        
        # Initialize level
        self.ilvl()
        self.uled()   # Update LED
        self.draw()   # Draw game screen
        
        ld = time.monotonic()  # Last draw time
        le = 0                 # Last encoder change time
        lw = -1                # Last warning remaining time
        
        while self.st == 'PLAY':
            now = time.monotonic()
            
            # ===== Handle Bomb Disarm Sequence =====
            if self.bomb_disarm_active:
                elapsed = now - self.shake_start_time
                
                # Play ticking sound every 0.5 seconds
                if now - self.last_tick_time > 0.5:
                    self.buz.tick()
                    self.last_tick_time = now
                
                # Pulsing red LED during disarm
                pulse = int(128 + 127 * abs((now % 0.5) / 0.5 - 0.5))
                self.led.fill((pulse, 0, 0))
                
                if elapsed >= self.shake_duration:
                    # Time's up - bomb explodes
                    self.bomb_disarm_active = False
                    self.dsp.clear()
                    self.dsp.txt("FAILED!", 40, 28, 1)
                    self.dsp.show()
                    self.buz.bomb()
                    self.hp -= 1
                    
                    # Flash red
                    for _ in range(3):
                        self.led.fill((255, 0, 0))
                        time.sleep(0.1)
                        self.led.fill((0, 0, 0))
                        time.sleep(0.1)
                    
                    self.uled()
                    
                    if self.hp <= 0:
                        self.st = 'OVER'
                    else:
                        time.sleep(0.5)
                        self.draw()
                        ld = now
                    
                elif self.check_shake():
                    # Successfully disarmed!
                    self.bomb_disarm_active = False
                    self.dsp.clear()
                    self.dsp.txt("DISARMED!", 30, 22, 1)
                    self.dsp.txt("+100 PTS", 32, 36, 1)
                    self.dsp.show()
                    self.buz.disarm_success()
                    
                    # Flash green
                    self.led.fill((0, 255, 0))
                    time.sleep(1)
                    
                    # Award bonus points
                    self.sc += 100
                    
                    self.uled()
                    self.draw()
                    ld = now
                
                else:
                    # Continue disarm sequence - update display
                    self.display_disarm_prompt()
                
                time.sleep(0.01)
                continue
            
            # ===== Normal Game Logic =====
            
            # Calculate remaining time
            el = int(now - self.stm)           # Elapsed time
            rm = max(0, self.tlm - el)         # Remaining time
            
            # Time warning (warn every second in last 5 seconds)
            if rm <= 5 and rm > 0 and rm != lw:
                self.buz.warn()
                lw = rm
            
            # Time's up
            if rm <= 0:
                self.msg("TIME UP!")
                self.buz.bomb()
                self.hp -= 1       # Lose HP
                self.uled()
                
                if self.hp <= 0:   # HP depleted
                    self.st = 'OVER'
                else:              # Restart current level
                    self.ilvl()
                    self.uled()
                    self.draw()
                    ld = now
                continue
            
            # Handle encoder input (move cursor)
            d = self.renc()
            if d and now - le > 0.08:  # 80ms debounce
                self.move(d)
                self.draw()
                ld = now
                le = now
            
            # Periodic display refresh (update time, etc.)
            if now - ld > 0.5:
                self.draw()
                ld = now
            
            # Handle button press (dig)
            if self.cbtn():
                self.dig()
                self.draw()
                if self.hp <= 0:
                    self.st = 'OVER'
                    break
            
            # Check if level cleared
            _, _, _, _, nd = self.lvl[self.lv]  # Required treasures
            if self.fnd >= nd:
                self.buz.win()
                self.sc += 100 + rm * 2  # Base score + time bonus
                
                # Show level clear screen
                self.dsp.clear()
                self.dsp.txt("LEVEL {}".format(self.lv), 35, 22, 1)
                self.dsp.txt("CLEAR!", 42, 36, 1)
                self.dsp.show()
                self.led.fill((0, 255, 0))  # Green for success
                time.sleep(1.5)
                
                # Enter next level or final level
                self.lv += 1
                if self.lv > 9:
                    self.dsp.clear()
                    self.dsp.show()
                    time.sleep(0.2)
                    self.st = 'LV10'  # Enter final level
                break
            
            time.sleep(0.01)
    
    # -------------------------------------------------------------------------
    # Final level (Level 10)
    # -------------------------------------------------------------------------
    # Player needs to choose one of two chests
    # Correct choice gives big score bonus, wrong choice loses HP
    # -------------------------------------------------------------------------
    def lv10(self):
        c = self.cfg[self.df]
        self.fhp = c['h10']    # Final level HP
        tl = c['t10']          # Final level time limit
        
        # Clear screen transition
        self.dsp.clear()
        self.dsp.show()
        time.sleep(0.1)
        
        # Show final level introduction
        self.dsp.clear()
        self.dsp.txt("FINAL!", 42, 8, 1)
        self.dsp.chest(25, 26)   # Left chest
        self.dsp.chest(85, 26)   # Right chest
        self.dsp.txt("PICK ONE", 32, 52, 1)
        self.dsp.show()
        self.led.fill((255, 0, 255))  # Purple
        time.sleep(2)
        
        # Initialize game state
        self.fch = 0                   # Current choice
        self.stm = time.monotonic()    # Start time
        rd = True                      # Need redraw
        le = 0                         # Last encoder change time
        ls = -1                        # Last displayed second
        cor = random.randint(0, 1)     # Correct answer (random)
        
        while True:
            now = time.monotonic()
            el = int(now - self.stm)
            rm = max(0, tl - el)
            
            # Auto-fail when time runs out
            if rm == 0:
                self.buz.lose()
                self.st = 'OVER'
                break
            
            # Handle encoder input (switch choice)
            d = self.renc()
            if d and now - le > 0.15:
                self.fch = 1 - self.fch  # Toggle between 0 and 1
                rd = True
                le = now
            
            # Update display
            if rd or el != ls:
                self.dsp.clear()
                self.dsp.txt("PICK!", 48, self.OFS, 1)
                self.dsp.txt("HP:{}".format(self.fhp), 52, 10 + self.OFS, 1)
                
                # Draw two chests
                self.dsp.chest(20, 26)
                self.dsp.chest(90, 26)
                
                # Highlight current selection
                if self.fch == 0:
                    self.dsp.rect(15, 23, 26, 22, 1)  # Selection box
                    self.dsp.txt("1", 25, 50, 1)
                else:
                    self.dsp.rect(85, 23, 26, 22, 1)
                    self.dsp.txt("2", 95, 50, 1)
                
                self.dsp.txt("{}S".format(rm), 55, 56, 1)  # Remaining time
                self.dsp.show()
                rd = False
                ls = el
            
            # LED breathing effect (purple pulse)
            b = int(128 + 127 * abs((now % 1) - 0.5))
            self.led.fill((b, 0, b))
            
            # Handle button press (confirm choice)
            if self.cbtn():
                if self.fch == cor:  # Correct choice
                    self.dsp.clear()
                    self.dsp.txt("CORRECT!", 32, 8, 1)
                    self.dsp.chest(50, 24, True)  # Open chest
                    self.dsp.show()
                    self.buz.win()
                    self.led.fill((255, 215, 0))  # Gold
                    time.sleep(2)
                    self.sc += 500  # Big score bonus
                    self.st = 'WIN'
                else:  # Wrong choice
                    self.dsp.clear()
                    self.dsp.txt("WRONG!", 40, 8, 1)
                    self.dsp.bomb(52, 24)
                    self.dsp.show()
                    self.buz.bomb()
                    self.led.fill((255, 0, 0))  # Red
                    time.sleep(1)
                    
                    self.fhp -= 1  # Lose HP
                    if self.fhp <= 0:  # HP depleted
                        self.st = 'OVER'
                    else:  # Try again
                        self.dsp.clear()
                        self.dsp.txt("TRY AGAIN", 30, 22, 1)
                        self.dsp.txt("{} LEFT".format(self.fhp), 40, 36, 1)
                        self.dsp.show()
                        time.sleep(1.5)
                        
                        # Reset state, re-randomize correct answer
                        self.stm = time.monotonic()
                        cor = random.randint(0, 1)
                        rd = True
                        continue
                break
            
            time.sleep(0.01)
    
    # -------------------------------------------------------------------------
    # Victory screen
    # -------------------------------------------------------------------------
    # Displays victory message and final score, LED rainbow effect
    # -------------------------------------------------------------------------
    def win(self):
        self.dsp.clear()
        self.dsp.txt("YOU WIN!", 32, 8, 1)
        self.dsp.chest(50, 22, True)  # Open chest
        self.dsp.txt("SC:{}".format(self.sc), 42, 52, 1)  # Final score
        self.dsp.show()
        
        # LED rainbow effect
        for _ in range(3):  # Loop 3 times
            for c in [(255,0,0), (255,255,0), (0,255,0), (0,0,255), (255,0,255)]:
                self.led.fill(c)
                time.sleep(0.1)
        
        self.led.fill((255, 255, 255))  # Finally white
        time.sleep(1)
        
        # Wait for button to return to menu
        while not self.cbtn():
            self.enc.update()
            time.sleep(0.01)
        self.st = 'MENU'
    
    # -------------------------------------------------------------------------
    # Game over screen
    # -------------------------------------------------------------------------
    # Displays game over message, level reached, and score
    # -------------------------------------------------------------------------
    def over(self):
        self.dsp.clear()
        self.dsp.txt("GAME OVER", 28, 8, 1)
        self.dsp.bomb(52, 22)  # Bomb icon
        self.dsp.txt("LV:{}".format(self.lv), 48, 48, 1)   # Level reached
        self.dsp.txt("SC:{}".format(self.sc), 45, 56, 1)   # Score
        self.dsp.show()
        
        # Lose sound and LED fade effect
        self.buz.lose()
        for i in range(255, 0, -25):  # Red fade out
            self.led.fill((i, 0, 0))
            time.sleep(0.05)
        self.led.fill((0, 0, 0))  # Turn off LED
        time.sleep(1)
        
        # Wait for button to return to menu
        while not self.cbtn():
            self.enc.update()
            time.sleep(0.01)
        self.st = 'MENU'
    
    # -------------------------------------------------------------------------
    # Draw game screen
    # -------------------------------------------------------------------------
    # Draws complete game interface: status bar, grid, cursor
    # -------------------------------------------------------------------------
    def draw(self):
        self.dsp.clear()
        
        # Calculate remaining time
        el = int(time.monotonic() - self.stm)
        rm = max(0, self.tlm - el)
        _, _, _, _, nd = self.lvl[self.lv]  # Required treasures
        
        # ===== Top status bar =====
        ty = self.OFS  # Top Y coordinate
        self.dsp.txt("L{}".format(self.lv), 0, ty, 1)       # Level
        self.dsp.txt("{}S".format(rm), 22, ty, 1)           # Remaining time
        self.dsp.txt("H:{}".format(self.hp), 52, ty, 1)     # HP
        self.dsp.txt("{}/{}".format(self.fnd, nd), 90, ty, 1)  # Treasure progress
        
        # Show shake event indicator if available (easy mode only)
        if self.shake_event_available:
            self.dsp.txt("*", 120, ty, 1)  # Star indicator
        
        self.dsp.hline(0, ty + 9, 128, 1)                   # Separator
        
        # ===== Calculate grid size and position =====
        rows = len(self.grd)
        cols = len(self.grd[0])
        
        # Dynamically calculate cell size based on rows/cols
        sz = min(12, 46 // rows, 120 // cols)  # Max 12 pixels, limited by height and width
        
        sy = ty + 12  # Grid start Y
        sx = (128 - cols * sz) // 2  # Center horizontally
        
        # ===== Draw grid =====
        for r in range(rows):
            for c in range(cols):
                x = sx + c * sz
                y = sy + r * sz
                
                # Draw cell border
                self.dsp.rect(x, y, sz, sz, 1)
                
                if r == self.pos[0] and c == self.pos[1]:
                    # Current cursor: filled highlight
                    self.dsp.frect(x + 2, y + 2, sz - 4, sz - 4, 1)
                elif self.rev[r][c]:
                    # Revealed: show content
                    ch = "T" if self.grd[r][c] == 'T' else "X"  # T=treasure, X=bomb
                    self.dsp.txt(ch, x + 3, y + 2, 1)
                else:
                    # Not revealed: show question mark
                    self.dsp.txt("?", x + 3, y + 2, 1)
        
        self.dsp.show()
    
    # -------------------------------------------------------------------------
    # Move cursor
    # -------------------------------------------------------------------------
    # Parameter d: Direction, positive=right/down, negative=left/up
    # 
    # Implements auto-wrap: automatically moves to next row at end of row
    # -------------------------------------------------------------------------
    def move(self, d):
        rows = len(self.grd)
        cols = len(self.grd[0])
        r, c = self.pos
        
        if d > 0:  # Move right
            c += 1
            if c >= cols:  # Exceeded right boundary
                c = 0
                r = (r + 1) % rows  # Move to next row
        else:  # Move left
            c -= 1
            if c < 0:  # Exceeded left boundary
                c = cols - 1
                r = (r - 1) % rows  # Move to previous row
        
        self.pos = [r, c]
    
    # -------------------------------------------------------------------------
    # Dig at current position
    # -------------------------------------------------------------------------
    # Reveals content at current cursor position
    # Treasure=add score, Bomb=lose HP (or trigger disarm event in easy mode)
    # -------------------------------------------------------------------------
    def dig(self):
        r, c = self.pos
        
        # Can't dig already revealed cell
        if self.rev[r][c]:
            return
        
        self.rev[r][c] = True  # Mark as revealed
        
        if self.grd[r][c] == 'T':  # Found treasure
            self.fnd += 1         # Increment treasures found
            self.sc += 50         # Add 50 points
            self.buz.found()      # Play found sound
            
            # Flash cyan LED
            self.led.fill((0, 255, 255))
            time.sleep(0.2)
            self.uled()
            
        elif self.grd[r][c] == 'B':  # Hit bomb
            # Check if shake event is available (easy mode only)
            if self.shake_event_available:
                # Trigger disarm sequence
                self.bomb_disarm_active = True
                self.shake_start_time = time.monotonic()
                self.last_tick_time = time.monotonic()
                self.shake_event_available = False  # Use up the event
                self.display_disarm_prompt()
            else:
                # Normal bomb behavior - lose HP
                self.hp -= 1          # Lose HP
                self.buz.bomb()       # Play explosion sound
                
                # Flash red LED rapidly
                for _ in range(3):
                    self.led.fill((255, 0, 0))
                    time.sleep(0.1)
                    self.led.fill((0, 0, 0))
                    time.sleep(0.1)
                self.uled()
    
    # -------------------------------------------------------------------------
    # Update LED color (based on HP)
    # -------------------------------------------------------------------------
    # Green=full HP, Yellow=half HP, Red=low HP, Off=no HP
    # -------------------------------------------------------------------------
    def uled(self):
        mhp = self.cfg[self.df]['hp']  # Max HP for current difficulty
        
        if self.hp >= mhp:
            self.led.fill((0, 255, 0))    # Full HP: green
        elif self.hp >= mhp // 2:
            self.led.fill((255, 255, 0))  # Half HP or more: yellow
        elif self.hp >= 1:
            self.led.fill((255, 0, 0))    # Low HP: red
        else:
            self.led.fill((0, 0, 0))      # No HP: off
    
    # -------------------------------------------------------------------------
    # Display message
    # -------------------------------------------------------------------------
    # Parameter m: Message string to display
    # 
    # Displays message in center of screen for 1.2 seconds
    # -------------------------------------------------------------------------
    def msg(self, m):
        self.dsp.clear()
        # Calculate horizontal center position
        # Each character is about 6 pixels wide
        self.dsp.txt(m, (128 - len(m) * 6) // 2, 28, 1)
        self.dsp.show()
        time.sleep(1.2)


# =============================================================================
# Program Entry Point
# =============================================================================
# Creates game instance and starts running
# =============================================================================
print("Starting...")  # Debug output
Game().run()          # Create and run game
