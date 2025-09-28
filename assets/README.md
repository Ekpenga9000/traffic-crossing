# Assets Directory

This directory contains all the game assets for the Traffic Light Logic Gate Game.

## Directory Structure

```
assets/
├── sprites/           # All sprite images and animations
│   ├── crossing_guard/    # Crossing guard character sprites
│   ├── cars/             # Vehicle sprites (different colors/types)
│   └── ui/               # User interface elements, buttons, icons
├── sounds/            # Audio files (sound effects, background music)
└── fonts/             # Custom fonts for the game
```

## Sprites

### Crossing Guard (`sprites/crossing_guard/`)
- **stop_gesture.png** - Crossing guard showing stop sign
- **go_gesture.png** - Crossing guard waving traffic through
- **idle.png** - Neutral/default pose

### Cars (`sprites/cars/`)
- **car_red.png** - Red car sprite
- **car_blue.png** - Blue car sprite  
- **car_green.png** - Green car sprite
- **car_yellow.png** - Yellow car sprite
- **truck.png** - Truck sprite (optional)

### UI (`sprites/ui/`)
- **button_normal.png** - Normal button state
- **button_hover.png** - Button hover state
- **button_pressed.png** - Button pressed state
- **icons/** - Various game icons

## Sounds

### Sound Effects (`sounds/`)
- **car_horn.wav** - Car horn sound
- **whistle.wav** - Crossing guard whistle
- **button_click.wav** - UI button click sound

## Fonts

### Custom Fonts (`fonts/`)
- **game_font.ttf** - Main game font
- **title_font.ttf** - Title/header font

## File Formats

- **Images**: PNG format with transparency support
- **Audio**: WAV format for sound effects, MP3 for background music
- **Fonts**: TTF format

## Usage

Assets should be loaded using relative paths from the project root:
```python
sprite_path = "assets/sprites/crossing_guard/stop_gesture.png"
sound_path = "assets/sounds/whistle.wav"
font_path = "assets/fonts/game_font.ttf"
```

## Notes

- All sprites should be optimized for performance
- Maintain consistent sprite sizes within categories
- Use transparent backgrounds for character sprites
- Include both normal and high-resolution versions if needed