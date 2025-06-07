from PIL import Image
from pathlib import Path

def export_sprite_sheet(sheet_name, texture_image, mask_image, sheet_data, grid_cols, grid_rows, output_dir="data/individual_sprites"):
    """Export individual sprites from a complete sprite sheet"""
    
    # Get sheet info
    sheet_info = sheet_data.get('sheet_info', {})
    category = sheet_info.get('category', 'other')
    display_name = sheet_info.get('display_name', sheet_name)
    
    # Create output directory structure
    output_path = Path(output_dir) / category / sheet_name.lower()
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save sheet metadata
    metadata = {
        'sheet_name': sheet_name,
        'display_name': display_name,
        'category': category,
        'description': sheet_info.get('description', ''),
        'grid_size': f"{grid_cols}x{grid_rows}",
        'has_mask': mask_image is not None,
        'original_size': f"{texture_image.width}x{texture_image.height}"
    }
    
    with open(output_path / "sheet_info.json", "w") as f:
        import json
        json.dump(metadata, f, indent=2)
    
    sprite_width = texture_image.width // grid_cols
    sprite_height = texture_image.height // grid_rows
    
    exported_count = 0
    sprite_labels = sheet_data.get('sprites', {})
    
    print(f"🔄 Exporting {display_name} ({category})...")
    print(f"   Grid: {grid_cols}x{grid_rows}, Sprite size: {sprite_width}x{sprite_height}")
    
    for cell_key, sprite_data in sprite_labels.items():
        if sprite_data.get('empty', False):
            continue  # Skip empty sprites
            
        row, col = sprite_data['row'], sprite_data['col']
        
        # Extract sprite region
        left = col * sprite_width
        top = row * sprite_height
        right = left + sprite_width
        bottom = top + sprite_height
        
        texture_sprite = texture_image.crop((left, top, right, bottom))
        
        # Downscale from 6x to original size
        original_width = max(32, sprite_width // 6)
        original_height = max(32, sprite_height // 6)
        
        texture_small = texture_sprite.resize((original_width, original_height), Image.NEAREST)
        
        # Create filename based on sprite data
        sprite_name = sprite_data.get('sprite_name', '').strip()
        action = sprite_data.get('action', '').strip()
        angle = sprite_data.get('angle', '').strip()
        frame = sprite_data.get('frame', 1)
        
        # Build filename parts
        filename_parts = []
        
        if sprite_name:
            filename_parts.append(sprite_name.lower().replace(' ', '_'))
        elif action:
            filename_parts.append(action.lower())
        else:
            filename_parts.append(f"sprite_{row}_{col}")
        
        if action and action != sprite_name:
            filename_parts.append(action.lower())
        
        if angle and angle not in ['static', 'omnidirectional']:
            filename_parts.append(angle.lower())
        
        filename_parts.append(f"{frame:02d}")
        
        filename_base = "_".join(filename_parts)
        
        # Save files
        texture_path = output_path / f"{filename_base}_texture.png"
        texture_small.save(texture_path)
        
        if mask_image:
            mask_sprite = mask_image.crop((left, top, right, bottom))
            mask_small = mask_sprite.resize((original_width, original_height), Image.NEAREST)
            mask_path = output_path / f"{filename_base}_mask.png"
            mask_small.save(mask_path)
        
        exported_count += 1
    
    print(f"✅ Exported {exported_count} sprites to {output_path}")
    return exported_count