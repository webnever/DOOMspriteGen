# DOOM Sprite Labeling Guide

## Overview
This guide explains how to properly label sprites in the Sprite Labeler App to create a consistent training dataset for your AI model.

## Naming Convention
Follow this pattern: `{creature}_{action}_{angle}_{variant}_{frame}.png`

## Field Descriptions

### 1. **Sheet Information** (Top Section)
Fill this out once per sprite sheet:

- **Display Name**: Human-readable name
  - Examples: "Spider Mastermind", "Cacodemon", "Plasma Rifle"
  
- **Category**: Type of sprite sheet
  - `creature` - Monsters, demons, enemies
  - `weapon` - Player weapons (shotgun, plasma rifle, etc.)
  - `item` - Pickups (health, armor, ammo, keys)
  - `effect` - Explosions, muzzle flashes, blood
  - `interface` - HUD elements, menus
  - `environment` - Decorative objects, corpses
  - `projectile` - Bullets, rockets, plasma balls
  - `menu` - Title screens, intermission graphics
  - `other` - Anything else

- **Description**: Brief description of the sheet's contents

### 2. **Individual Sprite Fields** (Per Grid Cell)

#### **Sprite Name** 
The base creature/object name (lowercase, underscores for spaces):
- `spider_mastermind`
- `cacodemon` 
- `imp`
- `shotgun`
- `health_potion`
- `plasma_ball`
- `blood_splat`

#### **Action**
What the sprite is doing:

**For Creatures:**
- `idle` - Standing still, breathing
- `walk` - Moving animation
- `attack` - Attacking/shooting
- `pain` - Taking damage
- `death` - Dying animation
- `special` - Unique actions (archvile resurrect, etc.)

**For Weapons:**
- `idle` - Ready position
- `fire` - Shooting/attacking
- `reload` - Reloading animation
- `pickup` - Being picked up

**For Items:**
- `static` - Not animated
- `pickup` - Being collected
- `activate` - Switch/door activation

**For Effects:**
- `explode` - Explosion sequence
- `impact` - Bullet/projectile impact
- `activate` - Magical/energy effects

#### **Angle/View**
The viewing angle (DOOM uses 8 directions):
- `front` - Facing camera (0°)
- `angle315` - 315° (front-right)
- `right` - Facing right (270°)
- `angle225` - 225° (back-right) 
- `back` - Facing away (180°)
- `angle135` - 135° (back-left)
- `left` - Facing left (90°)
- `angle45` - 45° (front-left)

**Special angles:**
- `omnidirectional` - Same from all angles (explosions, items)
- `static` - No rotation (UI elements)

#### **Frame**
Animation frame number (1, 2, 3, etc.)
- Start with 1 for first frame
- Use "Auto-number Frames" button for sequences

#### **Flags**
- ☑️ **Empty** - Mark cells with no sprite
- ☑️ **Important** - Mark key frames for training priority

## Quick Start Examples

### Example 1: Cacodemon Idle Animation
```
Sheet: "Cacodemon" (creature)
Grid cells showing floating animation:

Row 0, Col 0-3: Cacodemon idle frames
- Sprite Name: "cacodemon"
- Action: "idle" 
- Angle: "front"
- Frames: 1, 2, 3, 4
```

### Example 2: Player Shotgun
```
Sheet: "Weapons" (weapon)
Grid showing shotgun firing:

Row 2, Col 0-4: Shotgun fire sequence
- Sprite Name: "shotgun"
- Action: "fire"
- Angle: "front" 
- Frames: 1, 2, 3, 4, 5
```

### Example 3: Spider Mastermind Walking
```
Sheet: "SpiderMasterMind1" (creature)
8-directional walking animation:

Row 1: Walking frames for each angle
- Sprite Name: "spider_mastermind"
- Action: "walk"
- Angles: front, angle315, right, angle225, back, angle135, left, angle45
- Frame: 1 (for all)

Row 2: Second walking frame
- Same as above but Frame: 2
```

## Workflow Tips

### 1. **Start with Easy Sheets**
Begin with simple, clear sprites:
- Single creatures (Cacodemon, Imp)
- Static items (health packs, keys)
- Simple weapons

### 2. **Use Batch Operations**
- **Mark Row as Empty**: For unused grid rows
- **Mark Column as Empty**: For unused grid columns  
- **Auto-number Frames**: Select starting cell, then auto-increment

### 3. **Grid Layout Patterns**
Common DOOM sprite sheet layouts:
- **8x6**: Standard creature sheets (8 angles × 6 frames)
- **8x8**: Complex creatures with multiple actions
- **4x11**: Some weapon/item sheets
- **10x6**: Boss creatures with extra frames

### 4. **Quality Control**
- Mark important sprites (key animation frames)
- Check that frame numbers are sequential
- Ensure angle consistency across actions
- Verify sprite names match between related sheets

### 5. **Save Frequently**
Use "Save Progress" to preserve your work. The app saves to `sprite_labels.json`.

## Common Mistakes to Avoid

❌ **Inconsistent naming**: "Spider_Mastermind" vs "spider_mastermind"
✅ **Use lowercase with underscores**

❌ **Wrong angles**: Using "northeast" instead of "angle45"
✅ **Use DOOM's 8-direction system**

❌ **Skipping empty cells**: Leaving blanks unlabeled
✅ **Mark empty cells to speed up training**

❌ **Frame gaps**: 1, 2, 4, 5 (missing 3)
✅ **Sequential frames**: 1, 2, 3, 4, 5

## Export Results

After labeling, use:
- **Export Current Sheet**: Save one sprite sheet
- **Export All Sheets**: Process everything you've labeled

Exported sprites will be organized in:
```
data/individual_sprites/
├── creature/
│   ├── cacodemon/
│   │   ├── cacodemon_idle_front_01_texture.png
│   │   ├── cacodemon_idle_front_01_mask.png
│   │   └── sheet_info.json
│   └── spider_mastermind/
├── weapon/
│   └── shotgun/
└── effect/
    └── explosion/
```

This organized structure will be perfect for training your AI model!
