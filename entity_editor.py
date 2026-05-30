# =============================================================================
# IMPORTS
# =============================================================================
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import os
import operator
import random

# =============================================================================
# MOD SYSTEM CONFIGURATION
# =============================================================================
# Global set to track which attributes have been modified
modified_attributes = {'entityId'}

# Rounding configurations for specific attributes (0 = integer, 2 = 2 decimal places)
rounding = {
    'cost': 0, 'productionDuration': 0, 'maxCapacity': 0, 'maxHealth': 0,
    'maxShield': 0, 'maxMana': 0, 'skillManaCost': 0, 'armorProtection': 0,
    'moveSpeed': 0, 'sightRadius': 0, 'damage1': 2, 'attackCooldown': 2,
    'damage2': 0, 'attack2Cooldown': 2, 'weaponRange': 2, 'effectRadius1': 2,
    'skillRange': 0, 'healAmount1': 0, 'healAmount2': 0, 'duration1': 0, 'duration2': 0,
}

# =============================================================================
# MOD CLASS DEFINITION
# =============================================================================
class Mod:
    """Represents a modification that can be applied to an entity."""
    OPERATORS = {
        '==': operator.eq, '!=': operator.ne, '>': operator.gt,
        '<': operator.lt, '>=': operator.ge, '<=': operator.le,
    }

    mod_descriptions = {
        'Prebuilt': 'Significantly reduces production duration (x0.1 duration). Excellent for quick structures.',
        'Ablative': 'Doubles the unit\'s maximum health (x2 Max Health). Provides massive durability.',
        'Up-armored': 'Boosts survivability with a 1.25x health increase and a flat +2 armor boost.',
        'Hardened': 'Heavy defense kit: Increases health by 1.5x and adds minor armor (+1) for resilience.',
        'Cheap': 'Massively reduces the cost (x0.6 cost), making the unit highly affordable.',
        'Numerous': 'Economy booster: Lowers cost by 1, speeds up production (x0.75 duration), and increases capacity (+2).',
        'Armored': 'Standard defensive upgrade: Grants 1.2x health and a minor armor boost (+1).',
        'Shielded': 'Adds a reliable shield capacity and a flat +3 shield points.',
        'Scout': 'Enhances reconnaissance capability: Increases movement speed and sight radius by +3.',
        'Sentry': 'Highly optimized for fixed positions: Provides a large +5 increase to sight radius.',
        'Destructive': 'Boosts offensive power: Increases primary damage (damage1) by 1.25x.',
        'Rapidfire': 'Accelerates combat: Decreases attack cooldown (x0.8), allowing for faster attack cycles.',
        'Ranged': 'Increases combat reach: Increases the effective weapon range by 1.5x.',
        'Splashy': 'Adds splash damage capability: Increases the primary effect radius by +0.25.',
        'Charged': 'Optimizes for magic: Reduces both max mana and skill mana cost (x0.6) for efficiency.',
        'Expensive': 'A luxury/rare mod: Significantly increases the cost (x1.25 cost). (Negative quality mod).',
        'Frail': 'Damaging defect: Reduces maximum health and shield capacity significantly (x0.6). (Negative quality mod).',
        'Slow': 'Immobility modification: Severely reduces move speed (-3) and slows down attacks (x0.8 cooldown). (Negative quality mod).',
    }

    def __init__(self, name, quality, frequency, conditions, effects):
        self.name = name
        self.quality = quality
        self.frequency = frequency
        self.conditions = conditions
        self.effects = effects

    def get_description(self):
        return self.mod_descriptions.get(self.name, "No description available.")

    def get_effects_text(self):
        effects_text = []
        for effect in self.effects:
            attribute, multiplier, adder = effect
            effect_str = f"{attribute}: "
            if multiplier != 1:
                effect_str += f"x{multiplier}"
            else:
                effect_str += f"+{adder}"
            if adder != 0:
                effect_str += f" ({adder:+d})"
            effects_text.append(effect_str)
        return " | ".join(effects_text)
    
    def get_conditions_text(self):
        if not self.conditions:
            return "None (applies to all)"
        
        conditions_text = []
        for condition in self.conditions:
            if condition == 'or':
                conditions_text.append("OR")
            else:
                attr, op, val = condition
                conditions_text.append(f"{attr} {op} {val}")
        return " ".join(conditions_text)

    def valid_entity(self, entity):
        """Checks if the entity meets the conditions for this mod to be applied."""
        if not self.conditions:
            return True
        
        one_condition_good_enough = (self.conditions[0] == 'or')
        
        for condition in self.conditions:
            if condition == 'or':
                continue
            
            if condition[1] == 'in':
                passes_condition = (condition[0] in entity.get(condition[2], ""))
            else:
                op = self.OPERATORS[condition[1]]
                try:
                    passes_condition = op(float(entity.get(condition[0], 0)), float(condition[2]))
                except (ValueError, TypeError):
                    passes_condition = False
            
            if passes_condition and one_condition_good_enough:
                return True
            if not passes_condition and not one_condition_good_enough:
                return False
        
        return not one_condition_good_enough

    def apply(self, entity):
        """Applies the mod effects to the entity."""
        global modified_attributes
        
        if not self.valid_entity(entity):
            return entity
        
        for effect in self.effects:
            attribute, multiplier, adder = effect
            try:
                current_val = float(entity.get(attribute, 0))
                modified_amount = current_val * multiplier + adder
                
                rounding_precision = rounding.get(attribute, 2)
                if rounding_precision == 0:
                    modified_amount = int(modified_amount)
                else:
                    modified_amount = round(modified_amount, rounding_precision)
                
                entity[attribute] = modified_amount
                modified_attributes.add(attribute)
            except (ValueError, TypeError):
                continue
        
        return entity


# =============================================================================
# MOD DEFINITIONS
# =============================================================================
# Define your mods here
mods = [
    Mod('Prebuilt', 2, 1, [['cost', '>', 0]], [['productionDuration', 0.1, 0]]), 
    Mod('Ablative', 2, 1, [], [['maxHealth', 2, 0]]),
    Mod('Up-armored', 2, 1, [['armorProtection', '<', 3]], [['maxHealth', 1.25, 0], ['armorProtection', 1, 2]]),     
    Mod('Hardened', 2, 1, [['armorProtection', '>=', 3]], [['maxHealth', 1.5, 0], ['armorProtection', 1, 1]]),    
    Mod('Cheap', 1, 1, [['cost', '>', 0]], [['cost', 0.6, 0]]),
    Mod('Numerous', 1, 1, [['cost', '>', 0]], [['cost', 1, -1], ['productionDuration', 0.75, 0], ['maxCapacity', 2, 0]]),
    Mod('Armored', 1, 1, [], [['maxHealth', 1.2, 0], ['armorProtection', 1, 1]]),
    Mod('Shielded', 1, 1, [], [['maxShield', 1, 3]]),
    Mod('Scout', 1, 1, [['moveSpeed', '>', 0]], [['moveSpeed', 1, 3], ['sightRadius', 1, 3]]),
    Mod('Sentry', 1, 1, [['moveSpeed', '<=', 0]], [['sightRadius', 1, 5]]),
    Mod('Destructive', 1, 1, [['damage1', '>', 0]], [['damage1', 1.25, 0]]),
    Mod('Rapidfire', 1, 1, [['attackCooldown', '>', 0]], [['attackCooldown', 0.8, 0]]),
    Mod('Ranged', 1, 1, [['weaponRange', '>', 0]], [['weaponRange', 1, 1.5]]),
    Mod('Splashy', 1, 1, [['damage1', '>', 0]], [['effectRadius1', 1, 0.25]]),
    Mod('Charged', 1, 1, [['maxMana', '>', 0]], [['maxMana', 0.6, 0], ['skillManaCost', 0.6, 0]]),
    Mod('Expensive', -1, 1, [['cost', '>', 0]], [['cost', 1.25, 0]]),
    Mod('Frail', -1, 1, [], [['maxHealth', 0.6, 0], ['maxShield', 0.6, 0]]),
    Mod('Slow', -1, 1, [['moveSpeed', '>', 0], ['attackCooldown', '>', 0]], [['moveSpeed', 1, -3], ['attackCooldown', 0.8, 0]]),
]

mod_dict = {mod.name: mod for mod in mods}


# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================
class EntityEditor:
    # -------------------------------------------------------------------------
    # INITIALIZATION
    # -------------------------------------------------------------------------
    def __init__(self, root):
        self.root = root
        self.root.title("Entity Balancing Editor")
        self.root.geometry("1250x900")

        # Dark Theme Colors
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.frame_bg = "#3c3f41"
        self.entry_bg = "#3c3f41"

        self.root.configure(bg=self.bg_color)

        # Configure ttk style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # General Frames
        style.configure("TFrame", background=self.bg_color)
        
        # LabelFrames - Remove borders
        style.configure("TLabelFrame", 
                        background=self.frame_bg, 
                        foreground=self.fg_color, 
                        borderwidth=0)
        
        style.configure("TLabelFrame.Label", 
                        background=self.frame_bg, 
                        foreground=self.fg_color,
                        padding=5)
        
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        style.configure("TCheckbutton", 
                        background=self.bg_color, 
                        foreground=self.fg_color)
        
        style.configure("TButton", 
                        background=self.frame_bg, 
                        foreground=self.fg_color)
        
        style.map("TButton", 
                  background=[("active", "#555555")], 
                  foreground=[("active", self.fg_color)])
        
        # Entry
        style.configure("TEntry", 
                        fieldbackground=self.entry_bg, 
                        foreground=self.fg_color,
                        insertcolor=self.fg_color)
        
        # Combobox (Dropdown)
        style.configure("TCombobox", 
                        fieldbackground=self.entry_bg, 
                        background=self.entry_bg, 
                        foreground=self.fg_color,
                        selectbackground=self.entry_bg,
                        insertcolor=self.fg_color)
        
        style.map("TCombobox", 
                  background=[("active", self.entry_bg)],
                  fieldbackground=[("readonly", self.entry_bg)],
                  selectbackground=[("focus", "#4a6d8c")],
                  foreground=[("focus", self.fg_color)])

        # Treeview
        style.configure("Treeview", 
                        background=self.entry_bg, 
                        foreground=self.fg_color, 
                        fieldbackground=self.entry_bg)
        
        style.configure("Treeview.Heading", 
                        background=self.frame_bg, 
                        foreground=self.fg_color, 
                        relief=tk.FLAT,
                        borderwidth=0)
        
        style.map("Treeview", background=[("selected", "#4a6d8c")])

        # Separator
        style.configure("TSeparator", background=self.frame_bg)

        # Data variables
        self.data = []
        self.filtered_data = []
        self.headers = []
        self.file_path = None
        self.modified = False
        self.pre_paste_data = None
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Add global key bindings (Ctrl+Z for undo)
        self.root.bind("<Control-z>", self.undo_paste)
        self.root.bind("<Control-Z>", self.undo_paste)

    # -------------------------------------------------------------------------
    # UI SETUP
    # -------------------------------------------------------------------------
    def setup_ui(self):
        self._setup_file_controls()
        self._setup_control_panel()
        self._setup_tree_view()
        self._setup_status_bar()

    # File Controls (Top Bar)
    def _setup_file_controls(self):
        top_frame = tk.Frame(self.root, bg=self.bg_color, borderwidth=0)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="Open File", command=self.open_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Save File", command=self.save_file).pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(top_frame, text="No file loaded")
        self.file_label.pack(side=tk.LEFT, padx=20)

    # Control Panel (Filters, Mods, Bulk Edit)
    def _setup_control_panel(self):
        # Text colors
        self.desc_grey = "#aaaaaa" # Light grey for descriptions
        
        # --- Main Control Frame ---
        control_panel_frame = tk.LabelFrame(self.root, text="Filtering & Mod Controls", 
                                            bg=self.frame_bg, fg=self.fg_color, 
                                            borderwidth=0, relief=tk.FLAT, padx=10, pady=10)
        control_panel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        control_inner_frame = tk.Frame(control_panel_frame, bg=self.bg_color, borderwidth=0)
        control_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # --- Left Side: Search & Filters ---
        left_panel = tk.Frame(control_inner_frame, bg=self.bg_color, borderwidth=0)
        left_panel.pack(side=tk.LEFT, padx=10, fill='both', expand=True)

        # Global Search
        global_search_frame = tk.LabelFrame(left_panel, text="Global Search", 
                                            bg=self.frame_bg, fg=self.fg_color, 
                                            borderwidth=0, relief=tk.FLAT, padx=5, pady=5)
        global_search_frame.pack(fill=tk.X, pady=(0, 10))

        global_inner = tk.Frame(global_search_frame, bg=self.frame_bg, borderwidth=0)
        global_inner.pack(fill=tk.X, pady=5)

        ttk.Label(global_inner, text="Find:").pack(side=tk.LEFT, padx=2)
        self.global_search_var = tk.StringVar()
        self.global_search_entry = ttk.Entry(global_inner, textvariable=self.global_search_var, width=20)
        self.global_search_entry.pack(side=tk.LEFT, padx=2)
        self.global_search_entry.bind('<Return>', lambda e: self.apply_global_search())

        ttk.Button(global_inner, text="Search", command=self.apply_global_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(global_inner, text="Clear", command=self.clear_global_search).pack(side=tk.LEFT, padx=2)

        # Filters
        filter_frame = tk.LabelFrame(left_panel, text="Filters (Per Column)", 
                                     bg=self.frame_bg, fg=self.fg_color, 
                                     borderwidth=0, relief=tk.FLAT, padx=5, pady=5)
        filter_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # === Filter 1 ===
        filter1_frame = tk.Frame(filter_frame, bg=self.frame_bg, borderwidth=0)
        filter1_frame.pack(fill=tk.X, pady=2)
        self.filter1_column = ttk.Combobox(filter1_frame, width=12, state="readonly")
        self.filter1_column.pack(side=tk.LEFT, padx=2)
        ttk.Label(filter1_frame, text="Contains:").pack(side=tk.LEFT, padx=2)
        self.filter1_value = ttk.Entry(filter1_frame, width=12)
        self.filter1_value.pack(side=tk.LEFT, padx=2)
        self.filter1_exclude = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter1_frame, text="Exclude", variable=self.filter1_exclude).pack(side=tk.LEFT, padx=2)

        # === Filter 2 ===
        filter2_frame = tk.Frame(filter_frame, bg=self.frame_bg, borderwidth=0)
        filter2_frame.pack(fill=tk.X, pady=2)
        self.filter2_column = ttk.Combobox(filter2_frame, width=12, state="readonly")
        self.filter2_column.pack(side=tk.LEFT, padx=2)
        ttk.Label(filter2_frame, text="Contains:").pack(side=tk.LEFT, padx=2)
        self.filter2_min = ttk.Entry(filter2_frame, width=12)
        self.filter2_min.pack(side=tk.LEFT, padx=2)
        self.filter2_exclude = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter2_frame, text="Exclude", variable=self.filter2_exclude).pack(side=tk.LEFT, padx=2)

        # === Filter 3 ===
        filter3_frame = tk.Frame(filter_frame, bg=self.frame_bg, borderwidth=0)
        filter3_frame.pack(fill=tk.X, pady=2)
        self.filter3_column = ttk.Combobox(filter3_frame, width=12, state="readonly")
        self.filter3_column.pack(side=tk.LEFT, padx=2)
        ttk.Label(filter3_frame, text="Contains:").pack(side=tk.LEFT, padx=2)
        self.filter3_value = ttk.Entry(filter3_frame, width=12)
        self.filter3_value.pack(side=tk.LEFT, padx=2)
        self.filter3_exclude = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter3_frame, text="Exclude", variable=self.filter3_exclude).pack(side=tk.LEFT, padx=2)

        # === Filter 4 ===
        filter4_frame = tk.Frame(filter_frame, bg=self.frame_bg, borderwidth=0)
        filter4_frame.pack(fill=tk.X, pady=2)
        self.filter4_column = ttk.Combobox(filter4_frame, width=12, state="readonly")
        self.filter4_column.pack(side=tk.LEFT, padx=2)
        ttk.Label(filter4_frame, text="Contains:").pack(side=tk.LEFT, padx=2)
        self.filter4_value = ttk.Entry(filter4_frame, width=12)
        self.filter4_value.pack(side=tk.LEFT, padx=2)
        self.filter4_exclude = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter4_frame, text="Exclude", variable=self.filter4_exclude).pack(side=tk.LEFT, padx=2)
        
        # Filter Action Buttons
        filter_buttons = tk.Frame(filter_frame, bg=self.frame_bg, borderwidth=0)
        filter_buttons.pack(fill=tk.X, pady=5)
        ttk.Button(filter_buttons, text="Apply Filters", command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_buttons, text="Clear Filters", command=self.clear_filters).pack(side=tk.LEFT, padx=5)

        # --- Right Side: Mods & Data Management ---
        right_panel = tk.Frame(control_inner_frame, bg=self.bg_color, borderwidth=0)
        right_panel.pack(side=tk.LEFT, padx=20, fill='both', expand=True)

        # --- Mod Application & Randomize ---
        mod_frame = tk.LabelFrame(right_panel, text="Mods", 
                                   bg=self.frame_bg, fg=self.fg_color, 
                                   borderwidth=0, relief=tk.FLAT, padx=5, pady=5)
        mod_frame.pack(fill=tk.X, pady=5)

        # Mod Application
        mod_app_frame = tk.Frame(mod_frame, bg=self.frame_bg, borderwidth=0)
        mod_app_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(mod_app_frame, text="Select Mod:").pack(side=tk.LEFT, padx=5)
        self.mod_selector = ttk.Combobox(mod_app_frame, values=list(mod_dict.keys()), width=15, state="readonly")
        self.mod_selector.pack(side=tk.LEFT, padx=5)
        self.mod_selector.bind('<<ComboboxSelected>>', self.update_mod_description)

        ttk.Button(mod_app_frame, text="Apply to Selected", command=self.apply_mod_to_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(mod_app_frame, text="Apply to All", command=self.apply_mod_to_all).pack(side=tk.LEFT, padx=5)

        self.mod_desc_label = ttk.Label(mod_app_frame, text="Select a mod...", wraplength=300, foreground=self.fg_color)
        self.mod_desc_label.pack(side=tk.LEFT, padx=5)

        ttk.Separator(mod_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=5)

        # Randomize Mods
        random_frame = tk.Frame(mod_frame, bg=self.frame_bg, borderwidth=0)
        random_frame.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(random_frame, text="Randomly applies any valid mod to target. Please note some mods apply Negative values. Use above selection to see descriptions.", foreground=self.desc_grey, wraplength=300).pack(side=tk.LEFT, padx=5)

        # Quality Row
        quality_row = tk.Frame(mod_frame, bg=self.frame_bg, borderwidth=0)
        quality_row.pack(fill=tk.X, pady=2, padx=5)

        ttk.Label(quality_row, text="Quality:").pack(side=tk.LEFT, padx=5)
        self.random_quality = ttk.Combobox(quality_row, values=["All", "2 (High)", "1 (Normal)", "-1 (Negative)"], width=12, state="readonly")
        self.random_quality.set("All")
        self.random_quality.pack(side=tk.LEFT, padx=5)
        self.random_quality.bind('<<ComboboxSelected>>', self.update_random_mod_description)

        ttk.Button(quality_row, text="Randomize Selected", command=self.randomize_mod_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(quality_row, text="Randomize All", command=self.randomize_mod_all).pack(side=tk.LEFT, padx=5)

        self.random_desc_label = ttk.Label(quality_row, text="", foreground=self.desc_grey, wraplength=300)
        self.random_desc_label.pack(side=tk.LEFT, padx=5)
        
        self.update_random_mod_description()

        # --- Bulk Edit & Math & Row Management ---
        bulk_edit_frame = tk.LabelFrame(right_panel, text="Bulk Edit, Math & Rows", 
                                        bg=self.frame_bg, fg=self.fg_color, 
                                        borderwidth=0, relief=tk.FLAT, padx=5, pady=5)
        bulk_edit_frame.pack(fill=tk.X, pady=5)

        # Bulk Edit
        bulk_inner = tk.Frame(bulk_edit_frame, bg=self.frame_bg, borderwidth=0)
        bulk_inner.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(bulk_inner, text="Column:").pack(side=tk.LEFT, padx=5)
        self.bulk_column = ttk.Combobox(bulk_inner, width=12, state="readonly")
        self.bulk_column.pack(side=tk.LEFT, padx=5)

        ttk.Label(bulk_inner, text="Value:").pack(side=tk.LEFT, padx=5)
        self.bulk_value = ttk.Entry(bulk_inner, width=12)
        self.bulk_value.pack(side=tk.LEFT, padx=5)

        self.bulk_filtered_only = tk.BooleanVar(value=True)
        ttk.Checkbutton(bulk_inner, text="Filtered Only", variable=self.bulk_filtered_only).pack(side=tk.LEFT, padx=5)

        ttk.Button(bulk_inner, text="Apply", command=self.apply_bulk_edit).pack(side=tk.LEFT, padx=5)

        # Math Editor
        math_inner = tk.Frame(bulk_edit_frame, bg=self.frame_bg, borderwidth=0)
        math_inner.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(math_inner, text="Column:").pack(side=tk.LEFT, padx=5)
        self.math_column = ttk.Combobox(math_inner, width=12, state="readonly")
        self.math_column.pack(side=tk.LEFT, padx=5)

        ttk.Label(math_inner, text="Operation:").pack(side=tk.LEFT, padx=5)
        self.math_operation = ttk.Combobox(math_inner, values=["Add (+)", "Subtract (-)", "Multiply (*)", "Divide (/)"], width=12, state="readonly")
        self.math_operation.pack(side=tk.LEFT, padx=5)
        self.math_operation.set("Add (+)")

        ttk.Label(math_inner, text="Value:").pack(side=tk.LEFT, padx=5)
        self.math_value = ttk.Entry(math_inner, width=10)
        self.math_value.pack(side=tk.LEFT, padx=5)

        ttk.Button(math_inner, text="Apply Math", command=self.apply_math).pack(side=tk.LEFT, padx=5)

        # Row Management
        row_btns = tk.Frame(bulk_edit_frame, bg=self.frame_bg, borderwidth=0)
        row_btns.pack(fill=tk.X, pady=5, padx=5)

        ttk.Button(row_btns, text="Add Row", command=self.add_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(row_btns, text="Delete Row", command=self.delete_selected_rows).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row_btns, text="Undo Paste", command=self.undo_paste).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(row_btns, text="Tip: Pasting >1 row adds to bottom", 
                  foreground=self.desc_grey, wraplength=250).pack(side=tk.LEFT, padx=10)

    # Tree View (Main Table)
    def _setup_tree_view(self):
        tree_frame = tk.Frame(self.root, bg=self.bg_color, borderwidth=0)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree = ttk.Treeview(tree_frame, columns=[], height=20, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.bind("<Double-1>", self.on_cell_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_selection_change)
        
        # Key bindings (Ctrl+C, Ctrl+V)
        self.tree.bind("<Control-c>", self.copy_selection)
        self.tree.bind("<Control-v>", self.paste_selection)
        self.tree.bind("<Control-C>", self.copy_selection)
        self.tree.bind("<Control-V>", self.paste_selection)

    # Status Bar
    def _setup_status_bar(self):
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        self.status_label.config(background="#1a1a1a", foreground="white")

    # -------------------------------------------------------------------------
    # FILE OPERATIONS
    # -------------------------------------------------------------------------
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("TSV files", "*.tsv"), 
            ("All files", "*.*")
        ])
        if file_path:
            try:
                self.file_path = file_path
                self.load_file(file_path)
                self.file_label.config(text=f"Loaded: {os.path.basename(file_path)}")
                self.update_status(f"Loaded {len(self.data)} entities")
                self.modified = False
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".tsv",
            filetypes=[("TSV files", "*.tsv"), ("All files", "*.*")],
            title="Save Entity Data"
        )
        
        if not file_path:
            self.update_status("Save cancelled.")
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers, delimiter='\t')
                writer.writeheader()
                writer.writerows(self.data)
            
            self.file_path = file_path
            self.file_label.config(text=f"Saved: {os.path.basename(file_path)}")
            self.update_status(f"Successfully saved {len(self.data)} entities to {os.path.basename(file_path)}")
            self.modified = False

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
            self.update_status(f"Error saving file: {e}")

    def load_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            self.headers = reader.fieldnames
            self.data = list(reader)
        
        self.filtered_data = self.data.copy()
        self.update_tree()
        self.update_filter_columns()

    # -------------------------------------------------------------------------
    # TABLE DISPLAY & UPDATES
    # -------------------------------------------------------------------------
    def update_tree(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if data is None:
            data = self.filtered_data

        self.tree['columns'] = self.headers
        self.tree.column("#0", width=0, stretch=tk.NO)

        # Calculate appropriate widths for each column
        for header in self.headers:
            # Start with header width (minimum)
            final_width = (len(header) * 10) + 20
            
            # Check data content
            for row in data:
                value = str(row.get(header, ""))
                value_width = (len(value) * 8) + 10
                final_width = max(final_width, value_width)
            
            # Cap at 400 pixels
            final_width = min(final_width, 400)
            
            self.tree.column(header, anchor=tk.W, width=final_width, minwidth=final_width)
            self.tree.heading(header, text=header)

        for idx, row in enumerate(data):
            values = [row.get(header, "") for header in self.headers]
            self.tree.insert("", "end", iid=idx, values=values)

    def update_filter_columns(self):
        if self.headers:
            values = self.headers
            self.filter1_column['values'] = values
            self.filter2_column['values'] = values
            self.filter3_column['values'] = values
            self.filter4_column['values'] = values
            self.bulk_column['values'] = values
            self.math_column['values'] = values

    def update_status(self, message):
        self.status_label.config(text=message)

    # -------------------------------------------------------------------------
    # FILTERING
    # -------------------------------------------------------------------------
    def apply_filters(self):
        self.filtered_data = self.data.copy()

        # Helper function to handle quote logic
        def matches_filter(row_val, filter_val):
            row_str = str(row_val)
            filter_str = filter_val
            
            # Check if exact match is requested (wrapped in quotes)
            if filter_str.startswith('"') and filter_str.endswith('"'):
                # Remove quotes for exact comparison
                search_val = filter_str[1:-1]
                return search_val.lower() == row_str.lower()
            else:
                # Default partial match (contains)
                return filter_str.lower() in row_str.lower()

        # --- Filter 1 ---
        col1 = self.filter1_column.get()
        val1 = self.filter1_value.get()
        exclude1 = self.filter1_exclude.get()

        if col1 and val1:
            if exclude1:
                self.filtered_data = [row for row in self.filtered_data if not matches_filter(row.get(col1, ""), val1)]
            else:
                self.filtered_data = [row for row in self.filtered_data if matches_filter(row.get(col1, ""), val1)]

        # --- Filter 2 ---
        col2 = self.filter2_column.get()
        val2 = self.filter2_min.get()
        exclude2 = self.filter2_exclude.get()
        
        if col2 and val2:
            if exclude2:
                self.filtered_data = [row for row in self.filtered_data if not matches_filter(row.get(col2, ""), val2)]
            else:
                self.filtered_data = [row for row in self.filtered_data if matches_filter(row.get(col2, ""), val2)]

        # --- Filter 3 ---
        col3 = self.filter3_column.get()
        val3 = self.filter3_value.get()
        exclude3 = self.filter3_exclude.get()

        if col3 and val3:
            if exclude3:
                self.filtered_data = [row for row in self.filtered_data if not matches_filter(row.get(col3, ""), val3)]
            else:
                self.filtered_data = [row for row in self.filtered_data if matches_filter(row.get(col3, ""), val3)]

        # --- Filter 4 ---
        col4 = self.filter4_column.get()
        val4 = self.filter4_value.get()
        exclude4 = self.filter4_exclude.get()

        if col4 and val4:
            if exclude4:
                self.filtered_data = [row for row in self.filtered_data if not matches_filter(row.get(col4, ""), val4)]
            else:
                self.filtered_data = [row for row in self.filtered_data if matches_filter(row.get(col4, ""), val4)]

        self.update_tree()
        self.update_status(f"Filtered to {len(self.filtered_data)} entities")

    def clear_filters(self):
        self.filter1_value.delete(0, tk.END)
        self.filter1_column.set('')
        self.filter1_exclude.set(False)

        self.filter2_min.delete(0, tk.END)
        self.filter2_column.set('')
        self.filter2_exclude.set(False)

        self.filter3_value.delete(0, tk.END)
        self.filter3_column.set('')
        self.filter3_exclude.set(False)

        self.filter4_value.delete(0, tk.END)
        self.filter4_column.set('')
        self.filter4_exclude.set(False)

        self.update_tree()
        self.update_status("Filters cleared.")

    def apply_global_search(self):
        search_term = self.global_search_var.get().strip()
        
        if not search_term:
            self.clear_global_search()
            return

        exact_match = False
        if search_term.startswith('"') and search_term.endswith('"'):
            search_term = search_term[1:-1]
            exact_match = True

        search_lower = search_term.lower()
        
        filtered = []
        for row in self.data:
            found = False
            for key, value in row.items():
                val_str = str(value)
                
                # Special handling for system tags column
                if key == "offeredsystemtags":
                    tags = [tag.strip().lower() for tag in val_str.split(',') if tag.strip()]
                    
                    if exact_match:
                        if search_lower in tags:
                            found = True
                            break
                    else:
                        for tag in tags:
                            if search_lower in tag:
                                found = True
                                break
                        if found:
                            break
                    continue

                # Normal logic for other columns
                if exact_match:
                    if val_str.lower() == search_lower:
                        found = True
                        break
                else:
                    if search_lower in val_str.lower():
                        found = True
                        break
            
            if found:
                filtered.append(row)

        self.filtered_data = filtered
        self.update_tree()
        self.update_status(f"Global Search: Found {len(self.filtered_data)} matches")

    def clear_global_search(self):
        self.global_search_var.set("")
        self.filtered_data = self.data.copy()
        self.update_tree()
        self.update_status("Global Search cleared")

    # -------------------------------------------------------------------------
    # MOD APPLICATION
    # -------------------------------------------------------------------------
    def update_mod_description(self, event=None):
        selected_mod_name = self.mod_selector.get()
        
        if not selected_mod_name:
            self.mod_desc_label.config(text="Select a mod to see its description...")
            return
        
        try:
            mod = mod_dict[selected_mod_name]
            description = mod.get_description()
            self.mod_desc_label.config(text=description)
        except KeyError:
            self.mod_desc_label.config(text="Error: Mod details not found.")

    def apply_mod_to_selected(self):
        mod_name = self.mod_selector.get()
        
        if not mod_name:
            messagebox.showwarning("Warning", "Please select a mod")
            return

        selected_mod = mod_dict.get(mod_name)
        if not selected_mod:
            messagebox.showerror("Error", "Selected mod not found in database.")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select rows in the table")
            return
        
        count = 0
        for item in selected:
            row_idx = int(item)
            if row_idx < len(self.filtered_data):
                entity = self.filtered_data[row_idx]
                
                if selected_mod.valid_entity(entity):
                    selected_mod.apply(entity)
                    count += 1
        
        if count > 0:
            self.modified = True
            self.update_tree()
            self.update_status(f"Applied '{mod_name}' to {count} entities")
        else:
            self.update_status(f"Mod '{mod_name}' was not valid for the selected entities")

    def apply_mod_to_all(self):
        mod_name = self.mod_selector.get()
        
        if not mod_name:
            messagebox.showwarning("Warning", "Please select a mod")
            return

        selected_mod = mod_dict.get(mod_name)
        if not selected_mod:
            messagebox.showerror("Error", "Selected mod not found in database.")
            return

        count = 0
        for row in self.filtered_data:
            if selected_mod.valid_entity(row):
                selected_mod.apply(row)
                count += 1

        if count > 0:
            self.modified = True
            self.update_tree()
            self.update_status(f"Applied '{mod_name}' to {count} entities")
        else:
            self.update_status(f"Mod '{mod_name}' was not valid for the filtered entities")

    # -------------------------------------------------------------------------
    # RANDOMIZE MODS
    # -------------------------------------------------------------------------
    def update_random_mod_description(self, event=None):
        quality = self.random_quality.get()
        
        available_mods = mods
        if quality != "All":
            if "High" in quality:
                quality_val = 2
            elif "Normal" in quality:
                quality_val = 1
            else: # Negative
                quality_val = -1
            available_mods = [m for m in mods if m.quality == quality_val]
        
        mod_names = [m.name for m in available_mods]
        
        reminder = "\nNote: Some mods are Negative quality."
        
        if mod_names:
            text = f"Available: {', '.join(mod_names)}"
            text += reminder
        else:
            text = "No mods available for this quality."

        self.random_desc_label.config(text=text)

    def randomize_mod_selected(self):
        quality = self.random_quality.get()
        
        available_mods = mods
        if quality != "All":
            if "High" in quality:
                quality_val = 2
            elif "Normal" in quality:
                quality_val = 1
            else:
                quality_val = -1
            available_mods = [m for m in mods if m.quality == quality_val]

        if not available_mods:
            messagebox.showwarning("Warning", "No mods available for the selected quality.")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select rows in the table")
            return

        count = 0
        for item in selected:
            row_idx = int(item)
            if row_idx < len(self.filtered_data):
                entity = self.filtered_data[row_idx]
                
                valid_mods = [m for m in available_mods if m.valid_entity(entity)]
                
                if valid_mods:
                    mod = random.choice(valid_mods)
                    mod.apply(entity)
                    count += 1
        
        if count > 0:
            self.modified = True
            self.update_tree()
            self.update_status(f"Randomized mods for {count} entities")

    def randomize_mod_all(self):
        quality = self.random_quality.get()
        
        available_mods = mods
        if quality != "All":
            if "High" in quality:
                quality_val = 2
            elif "Normal" in quality:
                quality_val = 1
            else:
                quality_val = -1
            available_mods = [m for m in mods if m.quality == quality_val]

        if not available_mods:
            messagebox.showwarning("Warning", "No mods available for the selected quality.")
            return

        count = 0
        for row in self.filtered_data:
            valid_mods = [m for m in available_mods if m.valid_entity(row)]
            if valid_mods:
                mod = random.choice(valid_mods)
                mod.apply(row)
                count += 1

        if count > 0:
            self.modified = True
            self.update_tree()
            self.update_status(f"Randomized mods for {count} entities")

    # -------------------------------------------------------------------------
    # BULK EDIT
    # -------------------------------------------------------------------------
    def apply_bulk_edit(self):
        """Applies the entered value to the selected column for all (filtered) entities."""
        col = self.bulk_column.get()
        val = self.bulk_value.get()

        if not col:
            messagebox.showwarning("Warning", "Please select a column")
            return
        if not val:
            messagebox.showwarning("Warning", "Please enter a value")
            return

        target_data = self.filtered_data if self.bulk_filtered_only.get() else self.data
        
        count = 0
        if self.bulk_filtered_only.get():
            for row in target_data:
                row[col] = val
                count += 1
        else:
            for row in self.data:
                row[col] = val
                count += 1

        self.modified = True
        self.update_tree()
        self.update_status(f"Bulk updated {count} rows")

    # -------------------------------------------------------------------------
    # ROW MANAGEMENT (Add/Delete)
    # -------------------------------------------------------------------------
    def add_row(self):
        if not self.headers:
            messagebox.showwarning("Warning", "Please load a file first to define column headers.")
            return

        new_row = {header: "" for header in self.headers}
        self.data.append(new_row)
        self.filtered_data = self.data.copy()
        
        self.modified = True
        self.update_tree()
        self.update_status("Added new empty row")

    def delete_selected_rows(self):
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("Warning", "Please select rows to delete")
            return

        if len(selected) > 1:
            if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected)} rows?"):
                return
        else:
            if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected row?"):
                return

        entities_to_delete = []
        for item in selected:
            row_idx = int(item)
            if row_idx < len(self.filtered_data):
                entities_to_delete.append(self.filtered_data[row_idx])

        for entity in entities_to_delete:
            if entity in self.data:
                self.data.remove(entity)

        self.filtered_data = self.data.copy()
        
        self.modified = True
        self.update_tree()
        self.update_status(f"Deleted {len(entities_to_delete)} row(s)")

    # -------------------------------------------------------------------------
    # COPY & PASTE FUNCTIONALITY
    # -------------------------------------------------------------------------
    def copy_selection(self, event=None):
        selected = self.tree.selection()
        if not selected:
            self.update_status("No rows selected to copy")
            return

        rows_data = []
        for item in selected:
            row_idx = int(item)
            if row_idx < len(self.filtered_data):
                entity = self.filtered_data[row_idx]
                # Create a tab-separated row (compatible with Excel)
                row_values = [str(entity.get(header, "")) for header in self.headers]
                rows_data.append("\t".join(row_values))
        
        # Join rows with newlines for Excel compatibility
        clipboard_text = "\n".join(rows_data)
        
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_text)
        
        self.update_status(f"Copied {len(rows_data)} row(s) to clipboard")

    def paste_selection(self, event=None):
        try:
            clipboard_text = self.root.clipboard_get()
        except tk.TclError:
            self.update_status("Clipboard is empty")
            return

        selected = self.tree.selection()
        if not selected:
            self.update_status("Select a row to paste into")
            return

        # Save state for undo before pasting
        self.pre_paste_data = [row.copy() for row in self.data]

        lines = clipboard_text.strip().split("\n")
        
        start_idx = int(selected[0])
        
        count = 0
        for i, line in enumerate(lines):
            if i == 0:
                target_idx = start_idx
            else:
                new_row = {header: "" for header in self.headers}
                self.data.append(new_row)
                self.filtered_data = self.data.copy()
                target_idx = len(self.filtered_data) - 1
            
            values = line.split("\t")
            entity = self.filtered_data[target_idx]
            
            for col_index, value in enumerate(values):
                if col_index < len(self.headers):
                    header = self.headers[col_index]
                    entity[header] = value
                    count += 1

        self.modified = True
        self.update_tree()
        
        rows_pasted = len(lines)
        self.update_status(f"Pasted {rows_pasted} row(s)")

    def undo_paste(self, event=None):
        if self.pre_paste_data is None:
            self.update_status("Nothing to undo")
            return

        # Restore from backup
        self.data = [row.copy() for row in self.pre_paste_data]
        self.filtered_data = self.data.copy()
        
        self.pre_paste_data = None # Clear the backup
        
        self.modified = True
        self.update_tree()
        self.update_status("Undo paste successful")

    # -------------------------------------------------------------------------
    # CELL EDITING
    # -------------------------------------------------------------------------
    def on_cell_double_click(self, event):
        """Handles double-click events on the treeview to edit cell values."""
        # Identify the column and row
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)

        if not item_id or not column:
            return

        try:
            row_index = int(item_id)
            entity = self.filtered_data[row_index]
        except (ValueError, IndexError):
            return

        # Get the column index and header name
        col_index = int(column[1:]) - 1
        if col_index < 0 or col_index >= len(self.headers):
            return
        
        header_name = self.headers[col_index]

        # Get current value
        current_values = self.tree.item(item_id, 'values')
        current_value = current_values[col_index]

        # Calculate geometry
        x, y, width, height = self.tree.bbox(item_id, column)
        
        # Create entry widget
        entry = ttk.Entry(self.tree, width=width)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        
        # Place the entry over the cell
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()

        # Define callbacks
        def save_edit(event=None):
            new_value = entry.get()
            new_values = list(current_values)
            new_values[col_index] = new_value
            
            # Update tree
            self.tree.item(item_id, values=new_values)
            
            # Update data
            entity[header_name] = new_value
            self.modified = True
            
            # Clean up
            entry.destroy()
            self.update_status(f"Updated {header_name} for row {row_index}")

        def cancel_edit(event=None):
            entry.destroy()
            self.update_status("Edit cancelled")

        # Bind keys
        entry.bind('<Return>', save_edit)
        entry.bind('<Escape>', cancel_edit)
        entry.bind('<FocusOut>', save_edit)

    def on_selection_change(self, event):
        selected_item_id = self.tree.focus()
        
        if not selected_item_id:
            self.update_status("Selection cleared.")
            return

        try:
            row_index = int(selected_item_id)
            entity = self.filtered_data[row_index]
            selected_key = self.tree.get(selected_item_id, "values")
            self.update_status("Selected: {selected_key}. Data ready for actions.")

        except IndexError:
            self.update_status("Error: Could not find data for the selected row index.")
        except Exception as e:
            self.update_status("An error occurred during selection change: {e}")
    # -------------------------------------------------------------------------
    # MATH EDITING
    # -------------------------------------------------------------------------
    def apply_math(self):
        """Applies math operations to the selected column."""
        col = self.math_column.get()
        op = self.math_operation.get()
        val_str = self.math_value.get()

        if not col:
            messagebox.showwarning("Warning", "Please select a column")
            return
        if not val_str:
            messagebox.showwarning("Warning", "Please enter a value")
            return

        try:
            value = float(val_str)
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid number")
            return

        # Determine if input is an integer
        input_is_int = (value == int(value))

        # Get target data
        target_data = self.filtered_data if self.bulk_filtered_only.get() else self.data
        
        count = 0
        errors = 0
        
        for row in target_data:
            try:
                current_val_str = row.get(col, "0")
                current_val = float(current_val_str)
                
                if "Add" in op:
                    new_val = current_val + value
                elif "Subtract" in op:
                    new_val = current_val - value
                elif "Multiply" in op:
                    new_val = current_val * value
                elif "Divide" in op:
                    if value == 0:
                        continue
                    new_val = current_val / value
                else:
                    continue
                
                # Check if result should be integer
                # If input is integer AND current value was integer-like AND result is whole number
                original_was_int = (current_val == int(current_val))
                
                if input_is_int and original_was_int and (new_val == int(new_val)):
                    new_val = int(new_val)
                
                row[col] = new_val
                count += 1
            except (ValueError, TypeError, ZeroDivisionError):
                errors += 1

        self.modified = True
        self.update_tree()
        
        if errors > 0:
            self.update_status(f"Math applied to {count} rows ({errors} errors)")
        else:
            self.update_status(f"Math applied to {count} rows")


    # -------------------------------------------------------------------------
    # WINDOW MANAGEMENT
    # -------------------------------------------------------------------------
    def on_closing(self):
        """Handle the window closing event."""
        if self.modified:
            result = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save before closing?")
            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_file()
                self.root.destroy()
            else:  # No
                self.root.destroy()
        else:
            self.root.destroy()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = EntityEditor(root)
    root.mainloop()

