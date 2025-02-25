import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import csv
import re
import os
import threading

class CustomObjectsConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("CustomObjects Converter")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Data storage
        self.csv_files = []  # List of (csv_path, scenario_name) tuples
        self.output_file = ""
        
        # Options
        self.add_once_to_blueprints = tk.BooleanVar(value=True)
        self.filter_all_blueprints = tk.BooleanVar(value=False)
        
        # Create UI components
        self.create_ui()
        
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side (File selection)
        left_frame = ttk.LabelFrame(main_frame, text="Files & Scenarios", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # CSV Files Section
        csv_frame = ttk.Frame(left_frame)
        csv_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(csv_frame, text="CSV Files:").pack(side=tk.LEFT)
        ttk.Button(csv_frame, text="Add CSV", command=self.add_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(csv_frame, text="Remove Selected", command=self.remove_csv).pack(side=tk.LEFT)
        
        # CSV Files Listbox with scrollbar
        csv_list_frame = ttk.Frame(left_frame)
        csv_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.csv_listbox = tk.Listbox(csv_list_frame, selectmode=tk.SINGLE)
        self.csv_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        csv_scrollbar = ttk.Scrollbar(csv_list_frame, orient=tk.VERTICAL, command=self.csv_listbox.yview)
        csv_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.csv_listbox.config(yscrollcommand=csv_scrollbar.set)
        
        # Scenario entry
        scenario_frame = ttk.Frame(left_frame)
        scenario_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(scenario_frame, text="Scenario:").pack(side=tk.LEFT)
        self.scenario_var = tk.StringVar()
        self.scenario_entry = ttk.Entry(scenario_frame, textvariable=self.scenario_var, width=40)
        self.scenario_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Disable automatic selection of all text when clicking in the entry box
        def on_entry_click(event):
            # Don't select all text on click
            return "break"
        self.scenario_entry.bind("<FocusIn>", on_entry_click)
        
        ttk.Button(scenario_frame, text="Update", command=self.update_scenario).pack(side=tk.LEFT)
        
        # Example
        ttk.Label(left_frame, text="Example: Scenario_Precinct_Push_Security").pack(anchor=tk.W)
        
        # Output file selection
        output_frame = ttk.Frame(left_frame)
        output_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(output_frame, text="Output INI:").pack(side=tk.LEFT)
        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var, width=40, state="readonly").pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse...", command=self.select_output).pack(side=tk.LEFT)
        
        # Options frame
        options_frame = ttk.LabelFrame(left_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(options_frame, text="Add 'Once' parameter to all Blueprint assets", 
                         variable=self.add_once_to_blueprints).pack(anchor=tk.W)
                         
        ttk.Checkbutton(options_frame, text="Filter out ALL Blueprint assets (StaticMesh only)", 
                         variable=self.filter_all_blueprints).pack(anchor=tk.W)
        
        # Convert button
        ttk.Button(left_frame, text="CONVERT", command=self.start_conversion, style="Accent.TButton").pack(fill=tk.X, pady=10)
        
        # Right side (Log & Status)
        right_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.log_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar at bottom
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, variable=self.progress_var, mode="determinate")
        self.progress.pack(fill=tk.X, padx=10, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Set up event binding
        self.csv_listbox.bind('<<ListboxSelect>>', self.on_csv_select)
        
        # Create styles
        self.create_styles()
    
    def create_styles(self):
        style = ttk.Style()
        if "Accent.TButton" not in style.theme_names():
            style.configure("Accent.TButton", font=("Arial", 11, "bold"))
    
    def add_csv(self):
        files = filedialog.askopenfilenames(
            title="Select CSV Files",
            filetypes=[("CSV Files", "*.csv")]
        )
        
        if files:
            for file in files:
                # Default scenario name: use filename without extension
                scenario_name = f"Scenario_{os.path.splitext(os.path.basename(file))[0]}"
                self.csv_files.append((file, scenario_name))
                self.csv_listbox.insert(tk.END, f"{os.path.basename(file)} - {scenario_name}")
    
    def remove_csv(self):
        selection = self.csv_listbox.curselection()
        if selection:
            index = selection[0]
            self.csv_listbox.delete(index)
            self.csv_files.pop(index)
    
    def on_csv_select(self, event):
        selection = self.csv_listbox.curselection()
        if selection:
            index = selection[0]
            _, scenario = self.csv_files[index]
            
            # Only update if the current value is empty or if this is the first selection
            current_value = self.scenario_var.get().strip()
            if not current_value or not hasattr(self, '_last_selected'):
                self.scenario_var.set(scenario)
            
            # Remember this selection
            self._last_selected = index
    
    def update_scenario(self):
        # Try using the last selected index if nothing is currently selected
        selection = self.csv_listbox.curselection()
        if not selection and hasattr(self, '_last_selected'):
            index = self._last_selected
            # Re-select it in the UI
            self.csv_listbox.selection_set(index)
        elif selection:
            index = selection[0]
        else:
            messagebox.showwarning("Warning", "Please select a CSV file first.")
            return
            
        file_path, _ = self.csv_files[index]
        new_scenario = self.scenario_var.get().strip()
        
        if new_scenario:
            self.csv_files[index] = (file_path, new_scenario)
            self.csv_listbox.delete(index)
            self.csv_listbox.insert(index, f"{os.path.basename(file_path)} - {new_scenario}")
            self.csv_listbox.selection_set(index)
            # Keep focus on the entry widget
            self.scenario_entry.focus_set()
        else:
            messagebox.showwarning("Warning", "Scenario name cannot be empty.")
    
    def select_output(self):
        file = filedialog.asksaveasfilename(
            title="Save INI File",
            filetypes=[("INI Files", "*.ini")],
            defaultextension=".ini"
        )
        if file:
            self.output_file = file
            self.output_var.set(file)
    
    def start_conversion(self):
        if not self.csv_files:
            messagebox.showwarning("Warning", "Please add at least one CSV file.")
            return
        
        if not self.output_file:
            messagebox.showwarning("Warning", "Please select an output file.")
            return
        
        # Clear log
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        
        # Reset progress
        self.progress_var.set(0)
        
        # Start conversion in a separate thread
        thread = threading.Thread(target=self.convert)
        thread.daemon = True
        thread.start()
    
    def convert(self):
        self.status_var.set("Converting...")
        self.log("Starting conversion...")
        
        try:
            # Separate dictionaries for blueprints and static meshes
            blueprint_assets = {}  # path -> index
            staticmesh_assets = {}  # path -> index
            config_entries = []
            total_included = 0
            
            # Process each CSV file
            for i, (csv_file, scenario) in enumerate(self.csv_files):
                self.progress_var.set((i / len(self.csv_files)) * 100)
                self.log(f"\nProcessing {os.path.basename(csv_file)} for scenario {scenario}...")
                
                included = self.process_csv(csv_file, scenario, blueprint_assets, staticmesh_assets, config_entries)
                total_included += included
            
            self.log(f"\nTotal unique assets: {len(blueprint_assets) + len(staticmesh_assets)}")
            self.log(f"  Blueprint assets: {len(blueprint_assets)}")
            self.log(f"  Static mesh assets: {len(staticmesh_assets)}")
            self.log(f"Total configuration entries: {total_included}")
            
            # Write to output file
            with open(self.output_file, 'w') as f:
                f.write("[/CustomObjects/Mutators/CustomObjects.CustomObjects_C]\n")
                
                # First, write all blueprint assets
                if blueprint_assets:
                    for path, index in sorted(blueprint_assets.items(), key=lambda x: x[1]):
                        f.write(f";Index {index}\nAssets=BlueprintGeneratedClass'{path}_C'\n")
                
                # Then, write all static mesh assets
                if staticmesh_assets:
                    for path, index in sorted(staticmesh_assets.items(), key=lambda x: x[1]):
                        f.write(f";Index {index}\nStaticMeshAssets=StaticMesh'{path}'\n")
                
                # Write config entries
                for entry in config_entries:
                    params = [
                        f"Scenario={entry['Scenario']}",
                        f"Type={entry['Type']}",
                        f"AssetIndex={entry['AssetIndex']}",
                        f"Location={entry['Location']}",
                        f"Rotation={entry['Rotation']}"
                    ]
                    
                    # Add Once parameter if specified
                    if entry.get('Once', False):
                        params.append("Once")
                    
                    f.write(f"Configs=({', '.join(params)})\n")
            
            self.log(f"\nOutput written to {self.output_file}")
            self.log("Conversion completed successfully!")
            self.status_var.set("Done!")
            
            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo("Success", "Conversion completed successfully!"))
        
        except Exception as e:
            # Store the error first
            error_message = str(e)
            self.log(f"\nERROR: {error_message}")
            self.status_var.set("Error")
            # Now use the stored message
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {error_message}"))
        
        finally:
            self.progress_var.set(100)
    
    def process_csv(self, csv_file, scenario, blueprint_assets, staticmesh_assets, config_entries):
        """Process a single CSV file and update assets and config_entries"""
        skipped_count = 0
        skipped_bp_count = 0
        included_count = 0
        problematic_assets_found = []
        origin_skipped = 0
        
        # Track different asset types
        staticmesh_count = 0
        blueprint_count = 0
        
        with open(csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row_num, row in enumerate(reader, 1):
                try:
                    if len(row) < 6:
                        continue
                    
                    # Parse location first to check if we should skip it
                    location = self.parse_location(row[2])
                    if location is None:
                        origin_skipped += 1
                        continue
                    
                    # Check for blueprint assets first
                    bp_path = self.parse_blueprint_path(row[1])
                    if bp_path:
                        # Skip all blueprints if the option is enabled
                        if self.filter_all_blueprints.get():
                            skipped_bp_count += 1
                            continue
                            
                        # It's a blueprint asset
                        asset_type = "Blueprint"
                        
                        # Also check if we should skip this blueprint based on keywords
                        if self.should_skip_asset(bp_path):
                            skipped_count += 1
                            continue
                            
                        # Additional specific blueprint filtering
                        if any(keyword in bp_path for keyword in [
                            "/Game/Game/Actors/Breakables/", # Breakable objects
                            "/Game/Game/Actors/ShockwaveReactions/", # Shock wave reaction objects
                            "BP_SR_",                 # ShockwaveReaction objects
                            "/Game/Game/Actors/Weapons/", # Weapons
                            "/Game/Game/Actors/Gear/",    # Gear
                            "/Game/Game/Actors/Vehicles/", # Vehicles
                            "/Game/Game/Actors/Characters/", # Characters
                            "/Game/Game/Actors/Objectives/", # Objectives
                            "BP_Prop_",               # Prop blueprints
                            "/Game/Game/AI/",         # AI related assets
                            "/Game/Game/Actors/World/", # World actors
                            "/Game/Environment/BluePrints/", # Environment blueprints
                        ]):
                            self.log(f"  Skipping possibly problematic blueprint: {bp_path}")
                            skipped_count += 1
                            continue
                        
                        # If we got here, it's a blueprint we want to keep
                        self.log(f"  Including blueprint: {bp_path}")
                        
                        # Add to blueprint assets dictionary if not already there
                        if bp_path not in blueprint_assets:
                            blueprint_assets[bp_path] = len(blueprint_assets)
                        
                        rotation = self.parse_rotation(row[3])
                        
                        # Create the config entry
                        config_entry = {
                            'Scenario': scenario,
                            'Type': 'Blueprint',
                            'AssetIndex': blueprint_assets[bp_path],
                            'Location': location,
                            'Rotation': rotation
                        }
                        
                        # Add "Once" parameter if enabled
                        if self.add_once_to_blueprints.get():
                            config_entry['Once'] = True
                            
                        config_entries.append(config_entry)
                        included_count += 1
                        blueprint_count += 1
                    else:
                        # Try for static mesh
                        mesh_path = self.parse_mesh_path(row[5])
                        
                        # Skip problematic assets
                        if self.should_skip_asset(mesh_path):
                            skipped_count += 1
                            
                            # Record problematic assets for debugging
                            problem_assets = [
                                "/Game/Environment/Props/Exterior/Signs/SM_TrafficSigns_Destroyed_01b",
                                "/Game/Environment/Props/Exterior/Street/SM_IndPole_03c",
                                "/Game/Environment/Props/Exterior/Structures/SM_MetalTower__01",
                                "/Game/Environment/Props/Dev/plastic_chair_TrailerE3"
                            ]
                            
                            for problem in problem_assets:
                                if mesh_path and problem in mesh_path:
                                    if mesh_path not in problematic_assets_found:
                                        problematic_assets_found.append(mesh_path)
                                        self.log(f"  Found and skipped problematic asset: {mesh_path}")
                            
                            continue

                        # Add to static mesh assets dictionary if not already there
                        if mesh_path not in staticmesh_assets:
                            staticmesh_assets[mesh_path] = len(staticmesh_assets)

                        rotation = self.parse_rotation(row[3])
                        config_entries.append({
                            'Scenario': scenario,
                            'Type': 'StaticMesh',
                            'AssetIndex': staticmesh_assets[mesh_path],
                            'Location': location,
                            'Rotation': rotation
                        })
                        included_count += 1
                        staticmesh_count += 1
                except Exception as e:
                    self.log(f"  Error processing row {row_num}: {str(e)}")
                    if len(row) >= 6:
                        self.log(f"  Row content (mesh part): {row[5]}")
        
        self.log(f"  Skipped problematic assets: {skipped_count}")
        if self.filter_all_blueprints.get():
            self.log(f"  Skipped all blueprints: {skipped_bp_count}")
        self.log(f"  Skipped objects at origin (0,0,0): {origin_skipped}")
        self.log(f"  Included assets: {included_count} (StaticMesh: {staticmesh_count}, Blueprint: {blueprint_count})")
        
        if not problematic_assets_found:
            self.log("  No known problematic assets were found in this file.")
            
        return included_count
    
    def parse_mesh_path(self, meshes_str):
        """Parse static mesh path from meshes string"""
        match = re.search(r"StaticMesh'(.+?)'", meshes_str)
        return match.group(1) if match else None
        
    def parse_blueprint_path(self, actor_str):
        """Parse blueprint path from actor string"""
        # Match DynamicClass, BlueprintGeneratedClass, or other class paths
        match = re.search(r"(DynamicClass|BlueprintGeneratedClass)'(.+?)'", actor_str)
        if match:
            return match.group(2)
        return None

    def parse_location(self, location_str):
        match = re.search(r"X=([-\d.]+),Y=([-\d.]+),Z=([-\d.]+)", location_str)
        if match:
            x = int(round(float(match.group(1))))
            y = int(round(float(match.group(2))))
            z = int(round(float(match.group(3))))
            
            # Skip if location is at origin (0,0,0)
            if x == 0 and y == 0 and z == 0:
                return None
                
            return f"{x};{y};{z}"
        return None

    def parse_rotation(self, rotation_str):
        """
        Parse rotation string and always use Roll;Pitch;Yaw order 
        since that's the correct mapping
        """
        match = re.search(r"Pitch=([-\d.]+),Yaw=([-\d.]+),Roll=([-\d.]+)", rotation_str)
        if match:
            # Get original values
            pitch = int(round(float(match.group(1))))
            yaw = int(round(float(match.group(2))))
            roll = int(round(float(match.group(3))))
            
            # Return in RPY order (Roll;Pitch;Yaw)
            return f"{roll};{pitch};{yaw}"
        return "0;0;0"

    def should_skip_asset(self, mesh_path):
        # Skip if path is None
        if mesh_path is None:
            return True
        
        # Skip specific problematic assets (exact match)
        problem_assets = [
            # Static mesh problems
            "/Game/Environment/Props/Exterior/Signs/SM_TrafficSigns_Destroyed_01b",
            "/Game/Environment/Props/Exterior/Street/SM_IndPole_03c",
            "/Game/Environment/Props/Exterior/Structures/SM_MetalTower__01",
            "/Game/Environment/Props/Dev/plastic_chair_TrailerE3",
            
            # Blueprint problems (always filter these)
            "/Game/Environment/BluePrints/KitSelectionRoom/BP_KitSelectionRoom_Sec",
            "/Game/Environment/BluePrints/KitSelectionRoom/BP_KitSelectionRoom_Ins"
        ]
        
        # Check for problematic assets
        for problem in problem_assets:
            if problem in mesh_path:
                self.log(f"Skipping problematic asset: {mesh_path}")
                return True
        
        # Skip based on standard keywords (for all assets)
        standard_skip_keywords = [
            # Static mesh keywords
            "Door", "door",           # Any doors
            "MERGED", "Merged",       # Merged assets
            "Window", "window",       # Windows that might cause issues
            "TrafficSign", "trafficsign", # Traffic signs
            "Sign_", "sign_"          # Other signs
        ]
        
        for keyword in standard_skip_keywords:
            if keyword in mesh_path:
                return True
        
        # Only check blueprint-specific keywords if not a static mesh path
        # (Static mesh paths will have '/Game/' but not end with '_C')
        is_blueprint = not mesh_path.endswith('.SM_') and not "StaticMesh" in mesh_path
        
        if is_blueprint:
            # Blueprint-specific skip keywords - these are applied regardless of the filter_all_blueprints checkbox
            # These are known to cause issues so we filter them out even if blueprints are generally allowed
            dangerous_blueprint_keywords = [
                "/BluePrints/Lights/",    # Any lighting blueprints
                "BP_FluorescentLight",    # Fluorescent lights
                "BP_Lantern_",            # Lanterns
                "BP_LightBulb_",          # Light bulbs
                "BP_LightFlourescent_",   # Fluorescent lights (alternate spelling)
                "BP_LightLamp_",          # Light lamps
                "BP_OilLamp_",            # Oil lamps
                "BP_StreetLight_",        # Street lights
                "BP_StreetWallLamp_",     # Street wall lamps
                "BP_FireBarrel_",         # Fire barrels
                "KitSelectionRoom",       # Kit selection rooms
                # Additional very problematic blueprints
                "BP_Wire",                # Wire blueprints
                "SplineMeshBase",         # Spline mesh objects
                "Sidewalk_Splines",       # Sidewalk splines
                "Alarm_Loudspeaker",      # Alarm objects
                "VehicleSpawner",         # Vehicle spawners
            ]
            
            for keyword in dangerous_blueprint_keywords:
                if keyword in mesh_path:
                    return True
                    
        return False
    
    def log(self, message):
        """Add message to the log text widget"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        # Force update to ensure the UI shows the new message
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomObjectsConverter(root)
    root.mainloop()
