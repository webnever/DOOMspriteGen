import os
from PIL import Image
import json
import numpy as np
from pathlib import Path

class DoomDataProcessor:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.training_dir = self.data_dir / "training"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.training_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_sprite_pair(self, mask_path, texture_path):
        """Analyze a mask-texture pair to understand DOOM characteristics"""
        mask = Image.open(mask_path).convert('L')
        texture = Image.open(texture_path).convert('RGB')
        
        # Basic analysis
        mask_array = np.array(mask)
        texture_array = np.array(texture)
        
        # Get sprite dimensions
        width, height = mask.size
        
        # Count non-transparent pixels (assuming black is background)
        sprite_pixels = np.sum(mask_array > 0)
        fill_ratio = sprite_pixels / (width * height)
        
        # Analyze colors in texture
        texture_flat = texture_array.reshape(-1, 3)
        unique_colors = len(np.unique(texture_flat.view(np.dtype((np.void, texture_flat.dtype.itemsize * 3)))))
        
        return {
            'dimensions': (width, height),
            'fill_ratio': fill_ratio,
            'unique_colors': unique_colors,
            'sprite_pixels': sprite_pixels
        }
    
    def create_text_descriptions(self, sprite_name, analysis):
        """Generate text descriptions for sprites based on analysis"""
        # This is where you'll manually create descriptions
        # For now, let's make a template system
        
        base_descriptions = [
            f"DOOM sprite of {sprite_name}, pixel art style, retro gaming",
            f"{sprite_name} monster, 8-bit graphics, dark fantasy",
            f"demonic {sprite_name}, classic FPS game sprite, detailed pixel art"
        ]
        
        # Add characteristics based on analysis
        if analysis['fill_ratio'] > 0.3:
            base_descriptions.append(f"large {sprite_name} creature, imposing sprite")
        if analysis['unique_colors'] < 20:
            base_descriptions.append(f"simple colored {sprite_name}, limited palette")
            
        return base_descriptions
    
    def process_sprite_folder(self, folder_path):
        """Process a folder containing mask and texture files"""
        folder = Path(folder_path)
        sprite_data = []
        
        # Find all mask-texture pairs
        mask_files = list(folder.glob("*mask*.png")) + list(folder.glob("*_m.png"))
        
        for mask_file in mask_files:
            # Find corresponding texture file
            texture_file = self.find_texture_pair(mask_file)
            
            if texture_file and texture_file.exists():
                print(f"Processing: {mask_file.name} + {texture_file.name}")
                
                # Analyze the sprite
                analysis = self.analyze_sprite_pair(mask_file, texture_file)
                
                # Create descriptions (you'll improve this later)
                sprite_name = mask_file.stem.replace('_mask', '').replace('_m', '')
                descriptions = self.create_text_descriptions(sprite_name, analysis)
                
                sprite_info = {
                    'mask_path': str(mask_file),
                    'texture_path': str(texture_file),
                    'sprite_name': sprite_name,
                    'analysis': analysis,
                    'descriptions': descriptions
                }
                
                sprite_data.append(sprite_info)
        
        return sprite_data
    
    def find_texture_pair(self, mask_file):
        """Find the texture file that pairs with a mask file"""
        # Common naming patterns
        texture_patterns = [
            mask_file.name.replace('mask', 'texture'),
            mask_file.name.replace('_m.', '_t.'),
            mask_file.name.replace('_mask', '_texture'),
            mask_file.name.replace('mask', ''),  # Sometimes texture has no suffix
        ]
        
        for pattern in texture_patterns:
            texture_path = mask_file.parent / pattern
            if texture_path.exists():
                return texture_path
        
        return None

# Test your data processor
if __name__ == "__main__":
    processor = DoomDataProcessor()
    
    # Point this to where your sprite images are
    sprite_folder = "path/to/your/sprites"  # Update this path
    sprite_data = processor.process_sprite_folder(sprite_folder)
    
    print(f"Found {len(sprite_data)} sprite pairs!")
    for sprite in sprite_data[:3]:  # Show first 3
        print(f"- {sprite['sprite_name']}: {sprite['analysis']['dimensions']}")