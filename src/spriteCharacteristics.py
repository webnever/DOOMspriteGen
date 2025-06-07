# DOOM Sprite Characteristics Analyzer
# This helps us understand what makes DOOM sprites unique

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from collections import Counter

class DoomSpriteAnalyzer:
    """Analyzes characteristics of DOOM-style sprites"""
    
    def __init__(self):
        self.sprite_characteristics = {
            'typical_width': [32, 64, 128],
            'typical_height': [32, 64, 128], 
            'color_palette_size': [16, 32, 64],  # Limited colors
            'common_colors': [
                '#000000',  # Black (shadows)
                '#FF0000',  # Red (blood, demons)
                '#00FF00',  # Green (armor, slime)
                '#0000FF',  # Blue (armor, energy)
                '#FFFF00',  # Yellow (lights)
                '#FF8000',  # Orange (fire)
                '#800000',  # Dark red
                '#808080',  # Gray (metal)
            ]
        }
    
    def analyze_image(self, image_path):
        """Analyze a single image for DOOM-like characteristics"""
        try:
            img = Image.open(image_path)
            
            # Basic properties
            width, height = img.size
            
            # Color analysis
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get unique colors
            colors = img.getcolors(maxcolors=256*256*256)
            unique_colors = len(colors) if colors else "Too many colors"
            
            # Check if it's pixelated (low resolution upscaled)
            is_pixelated = self.is_pixelated(img)
            
            analysis = {
                'dimensions': (width, height),
                'unique_colors': unique_colors,
                'is_pixelated': is_pixelated,
                'doom_score': self.calculate_doom_score(width, height, unique_colors, is_pixelated)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def is_pixelated(self, img):
        """Check if image has pixelated/low-res characteristics"""
        # Convert to numpy array
        img_array = np.array(img)
        
        # Check for sharp edges (indication of pixel art)
        # This is a simplified check
        gray = np.mean(img_array, axis=2)
        
        # If image is small or has few gradients, likely pixelated
        return img.size[0] <= 128 or img.size[1] <= 128
    
    def calculate_doom_score(self, width, height, colors, is_pixelated):
        """Calculate how 'DOOM-like' an image is (0-100)"""
        score = 0
        
        # Size score (DOOM sprites are typically small)
        if 32 <= width <= 128 and 32 <= height <= 128:
            score += 30
        
        # Color score (limited palette)
        if isinstance(colors, int) and colors <= 64:
            score += 25
        elif isinstance(colors, int) and colors <= 128:
            score += 15
        
        # Pixelation score
        if is_pixelated:
            score += 25
        
        # Aspect ratio (DOOM sprites are often square-ish)
        aspect_ratio = width / height
        if 0.5 <= aspect_ratio <= 2.0:
            score += 20
        
        return min(score, 100)
    
    def create_sample_sprite_template(self):
        """Create a template showing DOOM sprite characteristics"""
        
        # Create a simple example sprite
        sprite = np.zeros((64, 64, 3), dtype=np.uint8)
        
        # Add some basic shapes with DOOM-style colors
        # Red demon-like figure
        sprite[20:45, 25:40] = [139, 0, 0]  # Dark red body
        sprite[15:25, 28:37] = [255, 0, 0]  # Bright red head
        sprite[18:22, 30:35] = [255, 255, 0]  # Yellow eyes
        
        # Black outline (very important in DOOM sprites)
        sprite[14:15, 28:37] = [0, 0, 0]    # Top of head
        sprite[25:26, 28:37] = [0, 0, 0]    # Bottom of head
        sprite[15:25, 27:28] = [0, 0, 0]    # Left side
        sprite[15:25, 36:37] = [0, 0, 0]    # Right side
        
        return Image.fromarray(sprite)

# Example usage and teaching moment
def demonstrate_analysis():
    """Demonstrate how to analyze sprite characteristics"""
    
    analyzer = DoomSpriteAnalyzer()
    
    print("=== DOOM Sprite Characteristics ===")
    print("What makes a good DOOM sprite:")
    print("1. Small dimensions (32x32 to 128x128 pixels)")
    print("2. Limited color palette (16-64 colors)")
    print("3. Pixelated appearance")
    print("4. Strong black outlines")
    print("5. High contrast colors")
    print("6. Clear, readable silhouette")
    
    # Create and show example
    sample_sprite = analyzer.create_sample_sprite_template()
    
    print("\n🎮 Sample DOOM-style template created!")
    print("This demonstrates the key visual elements we want our AI to learn.")
    
    return sample_sprite

if __name__ == "__main__":
    sample = demonstrate_analysis()
    # sample.show()  # Uncomment to display the sample sprite