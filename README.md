# Treasure Hunt Game

## Project Overview

Treasure Hunt is an embedded game project built with MicroPython/CircuitPython, where players dig for treasures while avoiding bombs under time pressure. The game combines hardware interaction (rotary encoder, buttons, buzzer, RGB LED, and OLED display) with classic minesweeper-like gameplay elements, delivering an exciting treasure-hunting experience.

## Features

- **Multiple Game Modes**: Easy, Medium, and Hard difficulties
- **Progressive Level Design**: Grids expand from 2x2 to 4x4 over 9 levels
- **Final Choice Level**: Level 10 requires picking between two treasure chests
- **Rich Audio-Visual Feedback**:
  - Multiple sound effects (clicks, buttons, victory, failure)
  - Colorful LED status indicators
  - Clear OLED graphical interface
- **Real-time Scoring System**: Base score + time bonus

## Hardware Requirements

| Component | Specification | Connection Pin |
|-----------|---------------|----------------|
| OLED Display | SSD1306, 128x64, I2C | SCL, SDA |
| Rotary Encoder | Rotary encoder with push button | D0, D1, D2 |
| Independent Button | Regular push button | D7 |
| RGB LED | NeoPixel/WS2812 | D8 |
| Buzzer | Passive buzzer | D9 |
| Microcontroller | CircuitPython/MicroPython compatible board | - |

## How to Play

### 1. Starting the Game
1. System displays welcome screen on startup
2. Press any button to enter main menu
3. Use rotary encoder to select difficulty:
   - **EASY**: 6 HP, 60 seconds per level
   - **MEDIUM**: 2 HP, 30 seconds per level
   - **HARD**: 2 HP, 15 seconds per level
4. Press button to confirm selection

### 2. Game Interface

**Top Status Bar Shows:**
- `L{level}`: Current level
- `{time remaining}S`: Remaining seconds
- `H:{health}`: Current health points
- `{treasures found}/{required}`: Treasure progress

**Game Grid:**
- Each cell initially shows `?`
- Current cursor position highlighted with filled square
- Revealed cells show:
  - `T`: Treasure (adds points)
  - `X`: Bomb (loses health)

### 3. Controls
- **Rotary Encoder**: Move cursor left/right (wraps around edges)
- **Any Button**: Dig at current cursor position

### 4. Game Mechanics

#### Grid Levels (1-9)
- Each level has a fixed grid size (from 2x2 to 4x4)
- Grid contains specific number of treasures and bombs
- Goal: Find required number of treasures
- Hitting bomb: Lose 1 HP
- Time runs out: Lose 1 HP
- Game over when HP reaches 0
- Level cleared reward: `100 + remaining time × 2 points`

#### Final Level (Level 10)
- Screen shows two treasure chests
- Use rotary encoder to select one
- Press button to confirm choice
- One chest contains treasure, the other a bomb
- Correct choice: Gain 500 points and win the game
- Wrong choice: Lose 1 HP, can retry (limited HP)

### 5. Status Indicators

#### LED Color Indicators:
- **Menu**: Green (Easy) / Yellow (Medium) / Red (Hard)
- **Gameplay**:
  - Green: Full HP
  - Yellow: Moderate HP
  - Red: Low HP
  - Flashing cyan: Found treasure
  - Fast flashing red: Hit bomb
- **Final Level**: Purple breathing effect
- **Victory**: Rainbow cycle
- **Game Over**: Red fade-out effect

#### Sound Effects:
- `click()`: Rotary encoder rotation
- `btn()`: Button press
- `startup()`: Game startup
- `win()`: Level cleared
- `lose()`: Game over
- `found()`: Treasure found
- `bomb()`: Bomb hit
- `warn()`: Time running low (last 5 seconds)

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
   - Final level correct choice: +500 points

## Code Architecture

```
Treasure Hunt Game
├── Buzzer Class (Buzzer Control)
│   ├── Play various sound effects
│   └── Frequency and duration control
├── SSD1306 Class (OLED Display Driver)
│   ├── Graphics drawing functions
│   ├── Text display
│   ├── Special icons (chest, bomb)
│   └── Display buffer management
└── Game Class (Main Game Logic)
    ├── Hardware initialization
    ├── Game state management
    │   ├── MENU: Difficulty selection
    │   ├── PLAY: Grid levels
    │   ├── LV10: Final level
    │   ├── WIN: Victory screen
    │   └── OVER: Game over screen
    ├── Input handling
    │   ├── Rotary encoder
    │   └── Button detection
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

### 2. Software Requirements
- Install CircuitPython or MicroPython on your microcontroller
- Upload code files to the microcontroller
- Ensure these library files are available:
  - `board.py`
  - `busio.py`
  - `digitalio.py`
  - `neopixel.py`
  - `pwmio.py`
  - `rotary_encoder.py` (must be provided separately)

### 3. Running the Game
- Reset microcontroller to start the game
- Follow on-screen instructions

## Customization & Extension

### Adjusting Game Parameters
Modify in Game class `__init__` method:
- `cfg`: Difficulty parameters (HP, time limits)
- `lvl`: Level configurations (grid size, treasure/bomb counts)

### Adding New Sound Effects
Add new sound effect functions in Buzzer class using the `tone(freq, dur)` method.

### Modifying Graphics
The `chest()` and `bomb()` methods in SSD1306 class define icons. Modify these to change appearance.

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| No display | Wrong I2C address | Check if OLED address is 0x3C |
| Encoder not responding | Incorrect pin connections | Verify D0, D1, D2 connections |
| No sound | Buzzer polarity reversed | Swap buzzer pins |
| LED not lighting | Insufficient power | Check voltage, may need external power supply |

## Project Files

```
treasure_hunt.py    # Main program file
README.md           # This documentation file
rotary_encoder.py   # Rotary encoder driver library
```

