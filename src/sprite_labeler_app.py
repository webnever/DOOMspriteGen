import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import json
from pathlib import Path
import numpy as np

class SpriteLabelingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DOOM Sprite Labeler - Universal")
        self.root.geometry("1500x1000")
        
        # Data storage
        self.current_sprite_sheet = None
        self.texture_image = None
        self.mask_image = None
        self.sprite_grid = {}
        self.sprites_data = {}
        
        # Grid settings
        self.grid_cols = 8
        self.grid_rows = 6
        self.selected_cell = None
        
        # Extended categories for all sprite types
        self.sprite_types = ["creature", "weapon", "item", "effect", "interface", "environment", "projectile", "menu", "other"]
        self.actions = ["idle", "walk", "attack", "pain", "death", "special", "fire", "reload", "pickup", "explode", "activate", "static", "unused"]
        self.angles = ["front", "angle315", "right", "angle225", "back", "angle135", "left", "angle45", "omnidirectional", "static"]
        
        self.setup_ui()
        self.load_sprite_sheet_list()
    
    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls (wider for more options)
        left_panel = ttk.Frame(main_frame, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Sprite sheet selection
        ttk.Label(left_panel, text="Select Sprite Sheet:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(left_panel, textvariable=self.sheet_var, width=35)
        self.sheet_combo.pack(fill=tk.X, pady=(5, 10))
        self.sheet_combo.bind("<<ComboboxSelected>>", self.on_sheet_selected)
        
        # Sheet info display
        self.sheet_info = ttk.Label(left_panel, text="No sheet selected", foreground="gray")
        self.sheet_info.pack(anchor="w", pady=(0, 5))
        
        # Progress display
        progress_frame = ttk.Frame(left_panel)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Current sheet progress
        self.progress_label = ttk.Label(progress_frame, text="Sheet Progress: 0/0 (0%)", font=("Arial", 10, "bold"))
        self.progress_label.pack(anchor="w")
        
        # Current sheet progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(2, 0))
        
        # Current sheet detailed stats
        self.stats_label = ttk.Label(progress_frame, text="Labeled: 0 | Empty: 0 | Remaining: 0", 
                                   foreground="blue", font=("Arial", 8))
        self.stats_label.pack(anchor="w", pady=(2, 0))
        
        # Total progress across all sheets
        ttk.Separator(progress_frame, orient='horizontal').pack(fill=tk.X, pady=(5, 5))
        
        self.total_progress_label = ttk.Label(progress_frame, text="Total Progress: 0/0 sheets (0%)", 
                                            font=("Arial", 10, "bold"), foreground="purple")
        self.total_progress_label.pack(anchor="w")
        
        self.total_progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.total_progress_bar.pack(fill=tk.X, pady=(2, 0))
        
        self.total_stats_label = ttk.Label(progress_frame, text="Completed: 0 | In Progress: 0 | Not Started: 0", 
                                         foreground="purple", font=("Arial", 8))
        self.total_stats_label.pack(anchor="w", pady=(2, 0))

        # Sheet naming section
        naming_frame = ttk.LabelFrame(left_panel, text="Sheet Information", padding=10)
        naming_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(naming_frame, text="Display Name:").pack(anchor="w")
        self.display_name_var = tk.StringVar()
        display_name_entry = ttk.Entry(naming_frame, textvariable=self.display_name_var, width=30)
        display_name_entry.pack(fill=tk.X, pady=(0, 5))
        display_name_entry.bind("<KeyRelease>", self.on_sheet_info_changed)
        
        ttk.Label(naming_frame, text="Category:").pack(anchor="w")
        self.sheet_type_var = tk.StringVar()
        sheet_type_combo = ttk.Combobox(naming_frame, textvariable=self.sheet_type_var, values=self.sprite_types, width=30)
        sheet_type_combo.pack(fill=tk.X, pady=(0, 5))
        sheet_type_combo.bind("<<ComboboxSelected>>", self.on_sheet_info_changed)
        
        ttk.Label(naming_frame, text="Description:").pack(anchor="w")
        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(naming_frame, textvariable=self.description_var, width=30)
        description_entry.pack(fill=tk.X, pady=(0, 5))
        description_entry.bind("<KeyRelease>", self.on_sheet_info_changed)
        
        # Grid settings
        grid_frame = ttk.LabelFrame(left_panel, text="Grid Settings", padding=10)
        grid_frame.pack(fill=tk.X, pady=(0, 10))
        
        grid_controls = ttk.Frame(grid_frame)
        grid_controls.pack(fill=tk.X)
        
        ttk.Label(grid_controls, text="Cols:").grid(row=0, column=0, sticky="w")
        self.cols_var = tk.IntVar(value=8)
        cols_spin = tk.Spinbox(grid_controls, from_=1, to=20, textvariable=self.cols_var, width=8)
        cols_spin.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(grid_controls, text="Rows:").grid(row=0, column=2, sticky="w")
        self.rows_var = tk.IntVar(value=6)
        rows_spin = tk.Spinbox(grid_controls, from_=1, to=20, textvariable=self.rows_var, width=8)
        rows_spin.grid(row=0, column=3, padx=(5, 0))
        
        ttk.Button(grid_frame, text="Update Grid", command=self.update_grid).pack(pady=(10, 0))
        
        # Auto-detect common layouts
        layout_frame = ttk.Frame(grid_frame)
        layout_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(layout_frame, text="8x6", command=lambda: self.set_grid(8, 6), width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(layout_frame, text="8x8", command=lambda: self.set_grid(8, 8), width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(layout_frame, text="4x11", command=lambda: self.set_grid(4, 11), width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(layout_frame, text="10x6", command=lambda: self.set_grid(10, 6), width=6).pack(side=tk.LEFT, padx=2)
        
        # Selected sprite info
        sprite_frame = ttk.LabelFrame(left_panel, text="Selected Sprite", padding=10)
        sprite_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.selected_info = ttk.Label(sprite_frame, text="Click a sprite to select")
        self.selected_info.pack(anchor="w")
        
        # Sprite naming
        ttk.Label(sprite_frame, text="Sprite Name:").pack(anchor="w", pady=(10, 0))
        self.sprite_name_var = tk.StringVar()
        sprite_name_entry = ttk.Entry(sprite_frame, textvariable=self.sprite_name_var, width=30)
        sprite_name_entry.pack(fill=tk.X, pady=(0, 5))
        sprite_name_entry.bind("<KeyRelease>", self.on_label_changed)
        
        # Action dropdown
        ttk.Label(sprite_frame, text="Action:").pack(anchor="w")
        self.action_var = tk.StringVar()
        action_combo = ttk.Combobox(sprite_frame, textvariable=self.action_var, values=self.actions, width=25)
        action_combo.pack(fill=tk.X, pady=(0, 5))
        action_combo.bind("<<ComboboxSelected>>", self.on_label_changed)
        
        # Angle dropdown
        ttk.Label(sprite_frame, text="Angle/View:").pack(anchor="w")
        self.angle_var = tk.StringVar()
        angle_combo = ttk.Combobox(sprite_frame, textvariable=self.angle_var, values=self.angles, width=25)
        angle_combo.pack(fill=tk.X, pady=(0, 5))
        angle_combo.bind("<<ComboboxSelected>>", self.on_label_changed)
        
        # Frame number
        ttk.Label(sprite_frame, text="Frame:").pack(anchor="w")
        self.frame_var = tk.IntVar(value=1)
        frame_spin = tk.Spinbox(sprite_frame, from_=1, to=50, textvariable=self.frame_var, width=10)
        frame_spin.pack(anchor="w", pady=(0, 5))
        frame_spin.bind("<KeyRelease>", self.on_label_changed)
        
        # Quality/Special flags
        flags_frame = ttk.Frame(sprite_frame)
        flags_frame.pack(fill=tk.X, pady=5)
        
        self.empty_var = tk.BooleanVar()
        ttk.Checkbutton(flags_frame, text="Empty", variable=self.empty_var, command=self.on_label_changed).pack(side=tk.LEFT)
        
        self.important_var = tk.BooleanVar()
        ttk.Checkbutton(flags_frame, text="Important", variable=self.important_var, command=self.on_label_changed).pack(side=tk.LEFT, padx=(10, 0))
        
        # Batch operations
        batch_frame = ttk.LabelFrame(left_panel, text="Batch Operations", padding=10)
        batch_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(batch_frame, text="Mark Row as Empty", command=self.mark_row_empty).pack(fill=tk.X, pady=2)
        ttk.Button(batch_frame, text="Mark Column as Empty", command=self.mark_col_empty).pack(fill=tk.X, pady=2)
        ttk.Button(batch_frame, text="Auto-number Frames", command=self.auto_number_frames).pack(fill=tk.X, pady=2)
        
        # Export buttons
        export_frame = ttk.Frame(left_panel)
        export_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(export_frame, text="Export Current Sheet", command=self.export_current_sheet).pack(fill=tk.X, pady=2)
        ttk.Button(export_frame, text="Export All Sheets", command=self.export_all_sheets).pack(fill=tk.X, pady=2)
        ttk.Button(export_frame, text="Save Progress", command=self.save_progress).pack(fill=tk.X, pady=2)
        ttk.Button(export_frame, text="Load Progress", command=self.load_progress).pack(fill=tk.X, pady=2)
        
        # Right panel - Image display
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Image tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Texture tab
        self.texture_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.texture_frame, text="Texture")
        
        self.texture_canvas = tk.Canvas(self.texture_frame, bg="gray")
        self.texture_canvas.pack(fill=tk.BOTH, expand=True)
        self.texture_canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Mask tab (only shown if mask exists)
        self.mask_frame = ttk.Frame(self.notebook)
        
        self.mask_canvas = tk.Canvas(self.mask_frame, bg="gray")
        self.mask_canvas.pack(fill=tk.BOTH, expand=True)
        self.mask_canvas.bind("<Button-1>", self.on_canvas_click)
    
    def load_sprite_sheet_list(self):
        """Load list of all available 6xGigaPixel sprite sheets"""
        input_dir = Path("sprites")
        sheets = []
        
        if not input_dir.exists():
            print("❌ sprites/ directory not found!")
            return
        
        # Find all 6xGigaPixel texture files
        for texture_file in input_dir.glob("*_6xGigaPixel.png"):
            if not texture_file.name.endswith("A_6xGigaPixel.png"):  # Skip mask files
                sheet_name = texture_file.stem.replace("_6xGigaPixel", "")
                mask_file = input_dir / f"{sheet_name}A_6xGigaPixel.png"
                
                # Create display name showing if mask exists
                display_name = f"{sheet_name}" + (" [+mask]" if mask_file.exists() else " [texture only]")
                sheets.append((sheet_name, display_name))
        
        # Sort by name
        sheets.sort(key=lambda x: x[0])
        
        # Update combo box
        display_names = [display for _, display in sheets]
        self.sheet_combo['values'] = display_names
        
        # Store mapping for lookup
        self.sheet_mapping = {display: actual for actual, display in sheets}
        
        if sheets:
            self.sheet_combo.set(display_names[0])
            print(f"✅ Loaded {len(sheets)} sprite sheets")
            # Update total progress after loading sheets
            self.update_progress_display()
        else:
            print("❌ No 6xGigaPixel texture files found!")
    
    def calculate_total_progress(self):
        """Calculate progress across all available sprite sheets"""
        total_sheets = len(self.sheet_combo['values'])
        if total_sheets == 0:
            return {
                'total_sheets': 0,
                'completed_sheets': 0,
                'in_progress_sheets': 0,
                'not_started_sheets': 0,
                'total_percentage': 0,
                'total_sprites_processed': 0,
                'total_sprites_available': 0
            }
        
        completed_sheets = 0
        in_progress_sheets = 0
        not_started_sheets = 0
        total_sprites_processed = 0
        total_sprites_available = 0
        
        # Analyze each available sheet
        for display_name in self.sheet_combo['values']:
            sheet_name = self.sheet_mapping.get(display_name)
            if not sheet_name:
                continue
            
            # Calculate grid size for this sheet (use current or default)
            grid_cols = self.grid_cols if sheet_name == self.current_sprite_sheet else 8
            grid_rows = self.grid_rows if sheet_name == self.current_sprite_sheet else 6
            total_cells = grid_cols * grid_rows
            total_sprites_available += total_cells
            
            sprites_data = self.sprites_data.get(sheet_name, {}).get('sprites', {})
            
            labeled_count = 0
            empty_count = 0
            
            for row in range(grid_rows):
                for col in range(grid_cols):
                    cell_key = f"{row},{col}"
                    if cell_key in sprites_data:
                        sprite_data = sprites_data[cell_key]
                        if sprite_data.get('empty', False):
                            empty_count += 1
                        else:
                            # Check if sprite has meaningful data
                            if (sprite_data.get('sprite_name') or 
                                sprite_data.get('action') or 
                                sprite_data.get('angle')):
                                labeled_count += 1
            
            processed_count = labeled_count + empty_count
            total_sprites_processed += processed_count
            
            # Categorize sheet status
            if processed_count == 0:
                not_started_sheets += 1
            elif processed_count == total_cells:
                completed_sheets += 1
            else:
                in_progress_sheets += 1
        
        total_percentage = (total_sprites_processed / total_sprites_available * 100) if total_sprites_available > 0 else 0
        
        return {
            'total_sheets': total_sheets,
            'completed_sheets': completed_sheets,
            'in_progress_sheets': in_progress_sheets,
            'not_started_sheets': not_started_sheets,
            'total_percentage': total_percentage,
            'total_sprites_processed': total_sprites_processed,
            'total_sprites_available': total_sprites_available
        }

    def update_progress_display(self):
        """Update progress statistics and display"""
        # Current sheet progress (existing code)
        if not self.current_sprite_sheet:
            self.progress_label.config(text="Sheet Progress: 0/0 (0%)")
            self.progress_bar['value'] = 0
            self.stats_label.config(text="No sheet selected")
        else:
            total_cells = self.grid_cols * self.grid_rows
            sprites_data = self.sprites_data.get(self.current_sprite_sheet, {}).get('sprites', {})
            
            labeled_count = 0
            empty_count = 0
            
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    cell_key = f"{row},{col}"
                    if cell_key in sprites_data:
                        sprite_data = sprites_data[cell_key]
                        if sprite_data.get('empty', False):
                            empty_count += 1
                        else:
                            # Check if sprite has meaningful data
                            if (sprite_data.get('sprite_name') or 
                                sprite_data.get('action') or 
                                sprite_data.get('angle')):
                                labeled_count += 1
            
            processed_count = labeled_count + empty_count
            remaining_count = total_cells - processed_count
            
            if total_cells > 0:
                percentage = (processed_count / total_cells) * 100
            else:
                percentage = 0
            
            # Update current sheet display
            self.progress_label.config(text=f"Sheet Progress: {processed_count}/{total_cells} ({percentage:.1f}%)")
            self.progress_bar['maximum'] = total_cells
            self.progress_bar['value'] = processed_count
            self.stats_label.config(text=f"Labeled: {labeled_count} | Empty: {empty_count} | Remaining: {remaining_count}")
            
            # Change color based on progress
            if percentage == 100:
                self.progress_label.config(foreground="green")
                self.stats_label.config(foreground="green")
            elif percentage >= 50:
                self.progress_label.config(foreground="blue")
                self.stats_label.config(foreground="blue")
            else:
                self.progress_label.config(foreground="black")
                self.stats_label.config(foreground="black")
        
        # Total progress across all sheets
        total_stats = self.calculate_total_progress()
        
        # Update total progress display
        self.total_progress_label.config(
            text=f"Total Progress: {total_stats['total_sprites_processed']}/{total_stats['total_sprites_available']} sprites ({total_stats['total_percentage']:.1f}%)"
        )
        
        self.total_progress_bar['maximum'] = total_stats['total_sprites_available']
        self.total_progress_bar['value'] = total_stats['total_sprites_processed']
        
        self.total_stats_label.config(
            text=f"Completed: {total_stats['completed_sheets']} | In Progress: {total_stats['in_progress_sheets']} | Not Started: {total_stats['not_started_sheets']}"
        )
        
        # Color code total progress
        if total_stats['total_percentage'] == 100:
            self.total_progress_label.config(foreground="green")
            self.total_stats_label.config(foreground="green")
        elif total_stats['total_percentage'] >= 75:
            self.total_progress_label.config(foreground="blue")
            self.total_stats_label.config(foreground="blue")
        elif total_stats['total_percentage'] >= 25:
            self.total_progress_label.config(foreground="orange")
            self.total_stats_label.config(foreground="orange")
        else:
            self.total_progress_label.config(foreground="purple")
            self.total_stats_label.config(foreground="purple")

    def on_sheet_selected(self, event=None):
        """Load selected sprite sheet"""
        display_name = self.sheet_var.get()
        if not display_name:
            return
        
        sheet_name = self.sheet_mapping.get(display_name)
        if not sheet_name:
            return
        
        try:
            # Load images
            texture_path = Path("sprites") / f"{sheet_name}_6xGigaPixel.png"
            mask_path = Path("sprites") / f"{sheet_name}A_6xGigaPixel.png"
            
            self.texture_image = Image.open(texture_path)
            self.current_sprite_sheet = sheet_name
            
            # Load mask if exists
            if mask_path.exists():
                self.mask_image = Image.open(mask_path)
                # Show mask tab
                if not any(self.notebook.tab(i, "text") == "Mask" for i in range(self.notebook.index("end"))):
                    self.notebook.add(self.mask_frame, text="Mask")
            else:
                self.mask_image = None
                # Hide mask tab if it exists
                for i in range(self.notebook.index("end")):
                    if self.notebook.tab(i, "text") == "Mask":
                        self.notebook.forget(i)
                        break
            
            # Update info display
            img_info = f"Size: {self.texture_image.size[0]}x{self.texture_image.size[1]}"
            if self.mask_image:
                img_info += f" | Mask: ✅"
            else:
                img_info += f" | Mask: ❌"
            self.sheet_info.config(text=img_info)
            
            # Initialize sheet data if not exists
            if sheet_name not in self.sprites_data:
                self.sprites_data[sheet_name] = {
                    'sheet_info': {
                        'display_name': sheet_name,
                        'category': 'other',
                        'description': ''
                    },
                    'sprites': {}
                }
            
            # Load existing sheet info
            sheet_info = self.sprites_data[sheet_name].get('sheet_info', {})
            self.display_name_var.set(sheet_info.get('display_name', sheet_name))
            self.sheet_type_var.set(sheet_info.get('category', 'other'))
            self.description_var.set(sheet_info.get('description', ''))
            
            # Auto-detect reasonable grid size
            self.auto_detect_grid()
            
            # Display images
            self.display_images()
            
            # Update progress display
            self.update_progress_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {sheet_name}: {str(e)}")
    
    def set_grid(self, cols, rows):
        """Set specific grid dimensions"""
        self.cols_var.set(cols)
        self.rows_var.set(rows)
        self.update_grid()
    
    def on_sheet_info_changed(self, event=None):
        """Save sheet information changes"""
        if not self.current_sprite_sheet:
            return
        
        if self.current_sprite_sheet not in self.sprites_data:
            self.sprites_data[self.current_sprite_sheet] = {'sheet_info': {}, 'sprites': {}}
        
        self.sprites_data[self.current_sprite_sheet]['sheet_info'] = {
            'display_name': self.display_name_var.get(),
            'category': self.sheet_type_var.get(),
            'description': self.description_var.get()
        }
    
    def mark_row_empty(self):
        """Mark entire row as empty"""
        if not self.selected_cell:
            messagebox.showwarning("Warning", "Select a cell first")
            return
        
        row, _ = self.selected_cell
        for col in range(self.grid_cols):
            cell_key = f"{row},{col}"
            if self.current_sprite_sheet not in self.sprites_data:
                self.sprites_data[self.current_sprite_sheet] = {'sheet_info': {}, 'sprites': {}}
            self.sprites_data[self.current_sprite_sheet]['sprites'][cell_key] = {
                'sprite_name': '',
                'action': '',
                'angle': '',
                'frame': 1,
                'empty': True,
                'important': False,
                'row': row,
                'col': col
            }
        
        self.display_images()
        self.update_progress_display()  # Add progress update
        messagebox.showinfo("Info", f"Marked row {row} as empty")
    
    def mark_col_empty(self):
        """Mark entire column as empty"""
        if not self.selected_cell:
            messagebox.showwarning("Warning", "Select a cell first")
            return
        
        _, col = self.selected_cell
        for row in range(self.grid_rows):
            cell_key = f"{row},{col}"
            if self.current_sprite_sheet not in self.sprites_data:
                self.sprites_data[self.current_sprite_sheet] = {'sheet_info': {}, 'sprites': {}}
            self.sprites_data[self.current_sprite_sheet]['sprites'][cell_key] = {
                'sprite_name': '',
                'action': '',
                'angle': '',
                'frame': 1,
                'empty': True,
                'important': False,
                'row': row,
                'col': col
            }
        
        self.display_images()
        self.update_progress_display()  # Add progress update
        messagebox.showinfo("Info", f"Marked column {col} as empty")
    
    def auto_number_frames(self):
        """Auto-number frames in sequence"""
        if not self.selected_cell:
            messagebox.showwarning("Warning", "Select a starting cell first")
            return
        
        start_row, start_col = self.selected_cell
        frame_num = 1
        
        if self.current_sprite_sheet not in self.sprites_data:
            self.sprites_data[self.current_sprite_sheet] = {'sheet_info': {}, 'sprites': {}}
        
        # Number across the row first, then down
        for row in range(start_row, self.grid_rows):
            for col in range(start_col if row == start_row else 0, self.grid_cols):
                cell_key = f"{row},{col}"
                if cell_key in self.sprites_data[self.current_sprite_sheet]['sprites']:
                    sprite_data = self.sprites_data[self.current_sprite_sheet]['sprites'][cell_key]
                    if not sprite_data.get('empty', False):
                        sprite_data['frame'] = frame_num
                        frame_num += 1
        
        self.display_images()
        self.update_progress_display()  # Add progress update
        messagebox.showinfo("Info", f"Auto-numbered frames starting from ({start_row},{start_col})")

    def on_label_changed(self, event=None):
        """Save label changes"""
        if not self.selected_cell or not self.current_sprite_sheet:
            return
        
        row, col = self.selected_cell
        cell_key = f"{row},{col}"
        
        if self.current_sprite_sheet not in self.sprites_data:
            self.sprites_data[self.current_sprite_sheet] = {'sheet_info': {}, 'sprites': {}}
        
        if 'sprites' not in self.sprites_data[self.current_sprite_sheet]:
            self.sprites_data[self.current_sprite_sheet]['sprites'] = {}
        
        self.sprites_data[self.current_sprite_sheet]['sprites'][cell_key] = {
            'sprite_name': self.sprite_name_var.get(),
            'action': self.action_var.get(),
            'angle': self.angle_var.get(),
            'frame': self.frame_var.get(),
            'empty': self.empty_var.get(),
            'important': self.important_var.get(),
            'row': row,
            'col': col
        }
        
        # Redraw to show updated labels
        self.display_images()
        
        # Update progress display
        self.update_progress_display()

    def export_current_sheet(self):
        """Export current sprite sheet"""
        if not self.current_sprite_sheet:
            messagebox.showwarning("Warning", "No sprite sheet selected")
            return
        
        # Check if sheet is complete
        total_cells = self.grid_cols * self.grid_rows
        sprites_data = self.sprites_data.get(self.current_sprite_sheet, {}).get('sprites', {})
        processed_count = len(sprites_data)
        
        if processed_count < total_cells:
            remaining = total_cells - processed_count
            result = messagebox.askyesno(
                "Incomplete Sheet", 
                f"This sheet has {remaining} unlabeled cells.\n"
                f"Progress: {processed_count}/{total_cells} ({(processed_count/total_cells)*100:.1f}%)\n\n"
                f"Export anyway?"
            )
            if not result:
                return
        
        try:
            from src.sprite_exporter import export_sprite_sheet
            count = export_sprite_sheet(
                self.current_sprite_sheet,
                self.texture_image,
                self.mask_image,
                self.sprites_data[self.current_sprite_sheet],
                self.grid_cols,
                self.grid_rows
            )
            messagebox.showinfo("Success", f"Exported {count} sprites from {self.current_sprite_sheet}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_all_sheets(self):
        """Export all labeled sprite sheets with progress summary"""
        if not self.sprites_data:
            messagebox.showwarning("Warning", "No sprite data to export")
            return
        
        # Show progress summary before export
        total_stats = self.calculate_total_progress()
        
        result = messagebox.askyesno(
            "Export All Sheets",
            f"Export Summary:\n"
            f"• Total Progress: {total_stats['total_percentage']:.1f}%\n"
            f"• Completed Sheets: {total_stats['completed_sheets']}\n"
            f"• In Progress Sheets: {total_stats['in_progress_sheets']}\n"
            f"• Not Started Sheets: {total_stats['not_started_sheets']}\n"
            f"• Total Sprites: {total_stats['total_sprites_processed']}/{total_stats['total_sprites_available']}\n\n"
            f"Continue with export?"
        )
        
        if not result:
            return
        
        total_exported = 0
        sheets_exported = 0
        
        for sheet_name, sheet_data in self.sprites_data.items():
            if sheet_data.get('sprites'):
                try:
                    # Load images for this sheet
                    texture_path = Path("sprites") / f"{sheet_name}_6xGigaPixel.png"
                    mask_path = Path("sprites") / f"{sheet_name}A_6xGigaPixel.png"
                    
                    texture_img = Image.open(texture_path)
                    mask_img = Image.open(mask_path) if mask_path.exists() else None
                    
                    from src.sprite_exporter import export_sprite_sheet
                    count = export_sprite_sheet(
                        sheet_name,
                        texture_img,
                        mask_img,
                        sheet_data,
                        self.grid_cols,  # You might want to store grid size per sheet
                        self.grid_rows
                    )
                    total_exported += count
                    sheets_exported += 1
                    
                except Exception as e:
                    print(f"Failed to export {sheet_name}: {e}")
        
        messagebox.showinfo(
            "Export Complete", 
            f"Successfully exported:\n"
            f"• {total_exported} total sprites\n"
            f"• from {sheets_exported} sprite sheets\n\n"
            f"Overall Progress: {total_stats['total_percentage']:.1f}%"
        )

    def auto_detect_grid(self):
        """Try to auto-detect reasonable grid dimensions"""
        if not self.texture_image:
            return
            
        width, height = self.texture_image.size
        
        # Common DOOM layouts
        common_grids = [(8, 6), (8, 5), (4, 11), (8, 8), (10, 6)]
        
        best_grid = (8, 6)  # Default
        
        for cols, rows in common_grids:
            sprite_w = width // cols
            sprite_h = height // rows
            
            # Prefer grids that give reasonable sprite sizes
            if 60 <= sprite_w <= 400 and 60 <= sprite_h <= 400:
                best_grid = (cols, rows)
                break
        
        self.cols_var.set(best_grid[0])
        self.rows_var.set(best_grid[1])
        self.update_grid()

    def update_grid(self):
        """Update grid overlay on images"""
        self.grid_cols = self.cols_var.get()
        self.grid_rows = self.rows_var.get()
        self.display_images()
        self.update_progress_display()  # Add progress update

    def display_images(self):
        """Display images with grid overlay"""
        if not self.texture_image:
            return
        
        # Clear canvases
        self.texture_canvas.delete("all")
        if self.mask_image:
            self.mask_canvas.delete("all")
        
        # Scale images to fit canvas
        canvas_width = self.texture_canvas.winfo_width()
        canvas_height = self.texture_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready yet, try again later
            self.root.after(100, self.display_images)
            return
        
        # Calculate scale factor
        img_width, img_height = self.texture_image.size
        scale_w = (canvas_width - 20) / img_width
        scale_h = (canvas_height - 20) / img_height
        scale = min(scale_w, scale_h, 1.0)  # Don't upscale
        
        display_width = int(img_width * scale)
        display_height = int(img_height * scale)
        
        # Resize images for display
        texture_display = self.texture_image.resize((display_width, display_height), Image.NEAREST)
        self.texture_photo = ImageTk.PhotoImage(texture_display)
        
        # Display texture image
        self.texture_canvas.create_image(10, 10, anchor="nw", image=self.texture_photo)
        
        # Display mask image if exists
        if self.mask_image:
            mask_display = self.mask_image.resize((display_width, display_height), Image.NEAREST)
            self.mask_photo = ImageTk.PhotoImage(mask_display)
            self.mask_canvas.create_image(10, 10, anchor="nw", image=self.mask_photo)
        
        # Draw grid
        self.draw_grid(self.texture_canvas, display_width, display_height)
        if self.mask_image:
            self.draw_grid(self.mask_canvas, display_width, display_height)
        
        # Store scale and offset for click handling
        self.display_scale = scale
        self.display_offset = (10, 10)

    def draw_grid(self, canvas, width, height):
        """Draw grid lines on canvas"""
        cell_width = width / self.grid_cols
        cell_height = height / self.grid_rows
        
        # Draw vertical lines
        for i in range(self.grid_cols + 1):
            x = 10 + i * cell_width
            canvas.create_line(x, 10, x, 10 + height, fill="red", width=2)
        
        # Draw horizontal lines
        for i in range(self.grid_rows + 1):
            y = 10 + i * cell_height
            canvas.create_line(10, y, 10 + width, y, fill="red", width=2)
        
        # Draw cell labels and highlights
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                x = 10 + col * cell_width + cell_width/2
                y = 10 + row * cell_height + cell_height/2
                
                # Cell coordinates text
                canvas.create_text(x, y - 20, text=f"{row},{col}", fill="yellow", font=("Arial", 8))
                
                # Show current labels if any
                cell_key = f"{row},{col}"
                if self.current_sprite_sheet and cell_key in self.sprites_data.get(self.current_sprite_sheet, {}).get('sprites', {}):
                    sprite_data = self.sprites_data[self.current_sprite_sheet]['sprites'][cell_key]
                    if not sprite_data.get('empty', False):
                        sprite_name = sprite_data.get('sprite_name', '')
                        action = sprite_data.get('action', '')
                        frame = sprite_data.get('frame', '')
                        label_text = sprite_name or action or '?'
                        canvas.create_text(x, y, text=label_text[:8], fill="lime", font=("Arial", 8))
                        if frame:
                            canvas.create_text(x, y + 15, text=f"F{frame}", fill="cyan", font=("Arial", 7))
                
                # Highlight selected cell
                if self.selected_cell == (row, col):
                    canvas.create_rectangle(
                        10 + col * cell_width, 10 + row * cell_height,
                        10 + (col + 1) * cell_width, 10 + (row + 1) * cell_height,
                        outline="cyan", width=3, fill=""
                    )

    def on_canvas_click(self, event):
        """Handle clicks on the canvas"""
        if not hasattr(self, 'display_scale') or not self.texture_image:
            return
        
        # Convert click position to grid coordinates
        x = (event.x - self.display_offset[0]) / self.display_scale
        y = (event.y - self.display_offset[1]) / self.display_scale
        
        if x < 0 or y < 0:
            return
        
        img_width, img_height = self.texture_image.size
        cell_width = img_width / self.grid_cols
        cell_height = img_height / self.grid_rows
        
        col = int(x // cell_width)
        row = int(y // cell_height)
        
        if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
            self.select_cell(row, col)

    def select_cell(self, row, col):
        """Select a grid cell and load its data"""
        self.selected_cell = (row, col)
        cell_key = f"{row},{col}"
        
        self.selected_info.config(text=f"Selected: Row {row}, Col {col}")
        
        # Load existing data if any
        if self.current_sprite_sheet and cell_key in self.sprites_data.get(self.current_sprite_sheet, {}).get('sprites', {}):
            sprite_data = self.sprites_data[self.current_sprite_sheet]['sprites'][cell_key]
            self.sprite_name_var.set(sprite_data.get('sprite_name', ''))
            self.action_var.set(sprite_data.get('action', ''))
            self.angle_var.set(sprite_data.get('angle', ''))
            self.frame_var.set(sprite_data.get('frame', 1))
            self.empty_var.set(sprite_data.get('empty', False))
            self.important_var.set(sprite_data.get('important', False))
        else:
            # Clear fields for new sprite
            self.sprite_name_var.set('')
            self.action_var.set('')
            self.angle_var.set('')
            self.frame_var.set(1)
            self.empty_var.set(False)
            self.important_var.set(False)
        
        # Redraw to show selection
        self.display_images()

    def save_progress(self):
        """Save current labeling progress"""
        try:
            with open("sprite_labels.json", "w") as f:
                import json
                json.dump(self.sprites_data, f, indent=2)
            messagebox.showinfo("Success", "Progress saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")

    def load_progress(self):
        """Load saved labeling progress"""
        try:
            if Path("sprite_labels.json").exists():
                with open("sprite_labels.json", "r") as f:
                    import json
                    self.sprites_data = json.load(f)
                messagebox.showinfo("Success", "Progress loaded!")
                if self.current_sprite_sheet:
                    self.display_images()  # Refresh display
                    self.update_progress_display()  # Update progress
            else:
                messagebox.showinfo("Info", "No saved progress found")
        except Exception as e:
            messagebox.showerror("Error", f"Load failed: {str(e)}")

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SpriteLabelingApp()
    app.run()