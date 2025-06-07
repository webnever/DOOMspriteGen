import os
from pathlib import Path
from collections import defaultdict

def check_sprites_directory():
    """Check the sprites directory for 6xGigaPixel textures and masks"""
    
    sprites_dir = Path("sprites")
    
    if not sprites_dir.exists():
        print("❌ sprites/ directory not found!")
        print("Make sure the sprites folder exists in the project root.")
        return
    
    print("🔍 Scanning sprites/ directory for 6xGigaPixel files...")
    print("=" * 60)
    
    # Find all 6xGigaPixel files
    gigapixel_files = list(sprites_dir.glob("*6xGigaPixel*"))
    
    if not gigapixel_files:
        print("❌ No 6xGigaPixel files found!")
        all_files = list(sprites_dir.glob("*"))
        print(f"Found {len(all_files)} total files in sprites/")
        if all_files:
            print("Sample files:")
            for f in all_files[:5]:
                print(f"  - {f.name}")
        return
    
    # Separate textures and masks
    creatures = defaultdict(dict)
    
    for file_path in gigapixel_files:
        filename = file_path.name
        
        # Extract creature name and type
        if filename.endswith("A_6xGigaPixel.png"):
            # This is a mask file
            creature_name = filename.replace("A_6xGigaPixel.png", "")
            creatures[creature_name]['mask'] = filename
        elif filename.endswith("_6xGigaPixel.png"):
            # This is a texture file
            creature_name = filename.replace("_6xGigaPixel.png", "")
            creatures[creature_name]['texture'] = filename
    
    print(f"📊 Found {len(gigapixel_files)} 6xGigaPixel files")
    print(f"🐉 Identified {len(creatures)} unique entities")
    print()
    
    # Categorize sprites
    categories = categorize_sprites(creatures)
    
    # Display results by category
    for category, sprite_list in categories.items():
        if sprite_list:
            print(f"{category.upper()}:")
            print("-" * 40)
            
            for creature_name in sorted(sprite_list):
                creature_data = creatures[creature_name]
                has_texture = 'texture' in creature_data
                has_mask = 'mask' in creature_data
                
                status = "✅ READY" if (has_texture and has_mask) else "⚠️  INCOMPLETE"
                print(f"  {creature_name:<25} {status}")
            print()
    
    # Summary
    complete_creatures = sum(1 for c in creatures.values() if 'texture' in c and 'mask' in c)
    ready_for_training = len([c for c in categories['🐲 CREATURES'] if 'texture' in creatures[c] and 'mask' in creatures[c]])
    
    print("SUMMARY:")
    print("-" * 60)
    print(f"✅ Complete pairs (texture + mask): {complete_creatures}")
    print(f"🎮 Creatures ready for labeling: {ready_for_training}")
    print(f"📁 Total files found: {len(gigapixel_files)}")
    
    return creatures

def categorize_sprites(creatures):
    """Categorize sprites into different types"""
    categories = {
        '🐲 CREATURES': [],
        '🎮 GAME ASSETS': [],
        '⚠️  INCOMPLETE': []
    }
    
    # Define categories
    game_assets = {
        'Effects', 'Interface', 'Items', 'Weapons', 'MenusDoom1_01', 
        'MenusDoom1_02', 'MenusDoom2', 'MissingAndAdditionals',
        'EndBossBox', 'BOSSBACK', 'MancubusBallExplode', 'BSPIJ0', 'SPIDS0'
    }
    
    for creature_name, data in creatures.items():
        has_both = 'texture' in data and 'mask' in data
        
        if not has_both:
            categories['⚠️  INCOMPLETE'].append(creature_name)
        elif creature_name in game_assets:
            categories['🎮 GAME ASSETS'].append(creature_name)
        else:
            categories['🐲 CREATURES'].append(creature_name)
    
    return categories

def show_labeling_recommendations():
    """Show which creatures to start labeling first"""
    print("\n🎯 LABELING RECOMMENDATIONS:")
    print("-" * 60)
    
    # Recommended order for labeling (easier to harder)
    labeling_order = [
        ("BEGINNER - Start Here:", ['CacoDemon', 'PinkyA', 'LostSoul']),
        ("INTERMEDIATE:", ['Arachnotron', 'HellKnight', 'SoldierChainGun', 'Revenant']),
        ("ADVANCED - Complex Sprites:", ['Mancubus', 'ArchVile1', 'ArchVile2']),
        ("BOSS LEVEL:", ['CyberDemon2', 'SpiderMasterMind1', 'SpiderMasterMind2', 'SpiderMasterMind3']),
        ("SPECIAL:", ['Player'])
    ]
    
    for category, creatures_list in labeling_order:
        print(f"{category}")
        for creature in creatures_list:
            print(f"  • {creature} - Good for learning sprite patterns")
        print()
    
    print("💡 TIPS:")
    print("  • Start with CacoDemon - it has clear, distinct sprites")
    print("  • Player sprites show all 8 angles clearly")  
    print("  • Boss sprites have the most animation frames")
    print("  • Save complex multi-form creatures for last")

if __name__ == "__main__":
    creatures = check_sprites_directory()
    show_labeling_recommendations()
