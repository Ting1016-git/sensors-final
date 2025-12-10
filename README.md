# Treasure Hunt Game
 
## Project Overview
 
Treasure Hunt is an embedded game project built with MicroPython/CircuitPython, where players dig for treasures while avoiding bombs under time pressure. The game combines hardware interaction (rotary encoder, buttons, buzzer, RGB LED, OLED display, and accelerometer) with classic minesweeper-like gameplay elements, delivering an exciting treasure-hunting experience.
 
## Features
 
- **Multiple Game Modes**: Easy, Medium, and Hard difficulties
- **Progressive Level Design**: Grids expand from 2x2 to 4x4 over 9 levels
- **Shake-to-Disarm Mechanic** (Easy Mode Only): Use accelerometer to disarm bombs by shaking the device
- **Final Choice Level**: Level 10 requires picking between two treasure chests
- **Rich Audio-Visual Feedback**:
  - Multiple sound effects (clicks, buttons, victory, failure, disarm ticking)
  - Colorful LED status indicators
  - Clear OLED graphical interface
  - Animated splash screen
- **Real-time Scoring System**: Base score + time bonus + disarm bonuses
 
## Hardware Requirements
 
| Component | Specification | Connection Pin |
|-----------|---------------|----------------|
| OLED Display | SSD1306, 128x64, I2C | SCL, SDA |
| Accelerometer | ADXL345, I2C (optional) | SCL, SDA |
| Rotary Encoder | Rotary encoder with push button | D0, D1, D2 |
| Independent Button | Regular push button | D7 |
| RGB LED | NeoPixel/WS2812 | D8 |
| Buzzer | Passive buzzer | D9 |
| Microcontroller | CircuitPython/MicroPython compatible board | - |

**Note:** The accelerometer is optional. If not connected, the game will run normally without the shake-to-disarm feature.
 
## How to Play
 
### 1. Starting the Game
1. System displays animated welcome screen on startup with chest opening and bomb fuse sparkling
2. Press any button to enter main menu
3. Use rotary encoder to select difficulty:
   - **EASY**: 6 HP, 60 seconds per level, shake-to-disarm available
   - **MEDIUM**: 4 HP, 30 seconds per level
   - **HARD**: 2 HP, 15 seconds per level
4. Press button to confirm selection
 
### 2. Game Interface
 
**Top Status Bar Shows:**
- `L{level}`: Current level
- `{time remaining}S`: Remaining seconds
- `H:{health}`: Current health points
- `{treasures found}/{required}`: Treasure progress
- `*`: Shake event indicator (Easy mode only, when available)
 
**Game Grid:**
- Each cell initially shows `?`
- Current cursor position highlighted with filled square
- Revealed cells show:
  - `T`: Treasure (adds points)
  - `X`: Bomb (loses health or triggers disarm in Easy mode)
 
### 3. Controls
- **Rotary Encoder**: Move cursor left/right (wraps around edges)
- **Any Button**: Dig at current cursor position
- **Shake Device** (Easy mode only): Disarm bomb during disarm sequence
 
### 4. Game Mechanics
 
#### Grid Levels (1-9)
- Each level has a fixed grid size (from 2x2 to 4x4)
- Grid contains specific number of treasures and bombs
- Goal: Find required number of treasures
- Hitting bomb: 
  - **Easy Mode (first bomb per level)**: Triggers shake-to-disarm sequence
  - **Other difficulties or after event used**: Lose 1 HP
- Time runs out: Lose 1 HP
- Game over when HP reaches 0
- Level cleared reward: `100 + remaining time × 2 points`

#### Shake-to-Disarm Feature (Easy Mode Only)
When you hit your first bomb in each level in Easy mode:
1. **Disarm sequence activates** - Screen shows "SHAKE TO DISARM!"
2. **You have 3 seconds** - Countdown timer displayed
3. **Shake the device** - Move it vigorously to trigger accelerometer
4. **LED pulses red** - Visual indicator during disarm attempt
5. **Ticking sound** - Audio feedback every 0.5 seconds
6. **Outcomes**:
   - **Success**: Bomb disarmed! +100 bonus points, no HP loss
   - **Failure**: Time expires, bomb explodes, -1 HP
7. **Event refreshes** - Each new level gives you one new shake event

**Visual Indicators:**
- `*` appears in top-right corner when shake event is available
- Disappears after use (success or failure)
- Reappears at the start of next level
 
#### Final Level (Level 10)
- Screen shows two treasure chests
- Use rotary encoder to select one
- Press button to confirm choice
- One chest contains treasure, the other a bomb
- Correct choice: Gain 500 points and win the game
- Wrong choice: Lose 1 HP, can retry (limited HP)
 
### 5. Status Indicators
 
#### LED Color Indicators:
- **Welcome Screen**: 
  - Gold/Orange pulsing during animation
  - Green breathing while waiting for button press
- **Menu**: Green (Easy) / Yellow (Medium) / Red (Hard)
- **Gameplay**:
  - Green: Full HP
  - Yellow: Moderate HP
  - Red: Low HP
  - Flashing cyan: Found treasure
  - Fast flashing red: Hit bomb
  - Pulsing red: Disarm sequence active
  - Solid green: Successful disarm
- **Final Level**: Purple breathing effect
- **Victory**: Rainbow cycle
- **Game Over**: Red fade-out effect
 
#### Sound Effects:
- `click()`: Rotary encoder rotation
- `btn()`: Button press
- `startup()`: Game startup (3-note arpeggio)
- `win()`: Level cleared
- `lose()`: Game over
- `found()`: Treasure found
- `bomb()`: Bomb hit/explosion
- `warn()`: Time running low (last 5 seconds)
- `tick()`: Disarm sequence countdown
- `disarm_success()`: Successful bomb disarm (3-note ascending)
 
## Game Rules Summary
 
1. **Objective**: Find all required treasures within time limit
2. **Failure Conditions**:
   - HP reaches 0
   - Wrong final choice with no HP remaining
3. **Victory Conditions**:
   - Complete all 9 grid levels
   - Choose correct chest in Level 10
4. **Scoring**:
   - Each treasure found: +50 points
   - Each level cleared: +100 points + (remaining time × 2)
   - Successful bomb disarm: +100 points
   - Final level correct choice: +500 points
 
## Code Architecture
 
```
Treasure Hunt Game
├── Buzzer Class (Buzzer Control)
│   ├── Play various sound effects
│   ├── Frequency and duration control
│   └── Disarm sequence sounds
├── SSD1306 Class (OLED Display Driver)
│   ├── Graphics drawing functions
│   ├── Text display
│   ├── Special icons (chest, bomb)
│   └── Display buffer management
└── Game Class (Main Game Logic)
    ├── Hardware initialization
    │   └── Optional accelerometer detection
    ├── Game state management
    │   ├── MENU: Difficulty selection
    │   ├── PLAY: Grid levels
    │   ├── LV10: Final level
    │   ├── WIN: Victory screen
    │   └── OVER: Game over screen
    ├── Input handling
    │   ├── Rotary encoder
    │   ├── Button detection
    │   └── Shake detection (accelerometer)
    ├── Shake-to-disarm system
    │   ├── Event tracking (one per level)
    │   ├── Countdown timer
    │   └── Acceleration threshold detection
    └── Game logic
        ├── Grid generation algorithm
        ├── Collision detection
        ├── Score calculation
        └── Time management
```
 
## Installation & Setup
 
### 1. Hardware Connections
```
OLED:    SCL → Microcontroller SCL
         SDA → Microcontroller SDA
         VCC → 3.3V
         GND → GND

ADXL345: SCL → Microcontroller SCL (shared with OLED)
         SDA → Microcontroller SDA (shared with OLED)
         VCC → 3.3V
         GND → GND
         (Optional - game works without it)
 
Encoder: CLK → D0
         DT  → D1
         SW  → D2
         VCC → 3.3V
         GND → GND
 
Button:  One end → D7
         Other end → GND (with pull-up)
 
RGB LED: DI → D8
         VCC → 3.3V/5V
         GND → GND
 
Buzzer:  Positive → D9
         Negative → GND
```

**I2C Addresses:**
- OLED (SSD1306): 0x3C
- Accelerometer (ADXL345): 0x53 (or 0x1D if SDO pin is grounded)
 
### 2. Software Requirements
- Install CircuitPython 10.0.3 (or compatible version) on your microcontroller
- Upload code files to the microcontroller
- Ensure these library files are available:
  - `adafruit_bus_device` folder
  - `adafruit_display_text` folder
  - `adafruit_adxl34x.mpy` (for accelerometer support)
  - `neopixel.mpy`
  - `adafruit_displayio_ssd1306.mpy`
  - `rotary_encoder.py` (included in project)
 
### 3. Running the Game
- Reset microcontroller to start the game
- Console will display: "Accelerometer found!" or "WARNING: Accelerometer not found - shake feature disabled"
- Follow on-screen instructions
 
## Customization & Extension
 
### Adjusting Game Parameters
Modify in Game class `__init__` method:
- `cfg`: Difficulty parameters (HP, time limits)
- `lvl`: Level configurations (grid size, treasure/bomb counts)
- `shake_threshold`: Adjust shake sensitivity (default: 2.0 m/s²)
- `shake_duration`: Time allowed for disarm attempt (default: 3.0 seconds)
 
### Adding New Sound Effects
Add new sound effect functions in Buzzer class using the `tone(freq, dur)` method.
 
### Modifying Graphics
The `chest()` and `bomb()` methods in SSD1306 class define icons. Modify these to change appearance.

### Adjusting Shake Sensitivity
If shake detection is too sensitive or not sensitive enough:
```python
self.shake_threshold = 2.0  # Increase for less sensitive, decrease for more sensitive
```
Higher values require more vigorous shaking. Typical range: 1.5 - 3.0 m/s²
 
## Troubleshooting
 
| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| No display | Wrong I2C address | Check if OLED address is 0x3C |
| Accelerometer not found | Loose connection or wrong address | Check wiring, verify address is 0x53, try I2C scan |
| Shake not detecting | Threshold too high or sensor not working | Lower shake_threshold value, verify accelerometer connection |
| Shake too sensitive | Threshold too low | Increase shake_threshold value |
| Encoder not responding | Incorrect pin connections | Verify D0, D1, D2 connections |
| No sound | Buzzer polarity reversed | Swap buzzer pins |
| LED not lighting | Insufficient power | Check voltage, may need external power supply |
| Game crashes on startup | Missing library | Ensure all required .mpy files are in /lib folder |

### Testing Accelerometer Connection
Run this I2C scan code to verify devices:
```python
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
while not i2c.try_lock():
    pass
devices = i2c.scan()
print(f"I2C devices found: {[hex(d) for d in devices]}")
i2c.unlock()
```
Expected output: `['0x3c', '0x53']` (OLED and accelerometer)
 
## Project Files
 
```
treasure_hunt.py       # Main program file with shake-to-disarm feature
treasure_hunt_animated.py  # Version with animated splash screen
README.md              # This documentation file
rotary_encoder.py      # Rotary encoder driver library
test_accelerometer.py  # Accelerometer testing utility
```

## Tips for Best Experience

1. **Shake Technique**: Use quick, vigorous shaking motions for best detection
2. **Mounting**: Secure all components to prevent loose connections during shaking
3. **Power**: Ensure stable power supply, especially when shaking the device
4. **Practice**: Try the accelerometer test script to get a feel for shake detection before playing
5. **Strategy**: In Easy mode, save your shake event for later bombs when HP is lower

## Credits

This project demonstrates embedded system programming with:
- Real-time sensor integration (accelerometer)
- Multi-threaded event handling
- Hardware abstraction and graceful degradation
- User experience design with audio-visual feedback
