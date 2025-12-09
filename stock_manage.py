import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import threading
import cv2
from PIL import Image, ImageTk

class InventoryDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Inventory Management Dashboard")
        self.root.geometry("1400x900")  # Made even taller
        self.root.configure(bg='#1e1e2e')
        
        # Make window resizable
        self.root.resizable(True, True)
        
        self.inventory_file = "inventory_database.json"
        self.inventory = self.load_inventory()
        
        # Color thresholds
        self.RED_THRESHOLD = 7
        self.YELLOW_THRESHOLD = 30
        
        # Scanner state
        self.scanning = False
        self.camera = None
        
        self.setup_ui()
        self.update_dashboard()
    
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="#ffffe0", 
                           relief='solid', borderwidth=1, font=('Arial', 10))
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def load_inventory(self):
        """Load inventory from JSON"""
        if os.path.exists(self.inventory_file):
            with open(self.inventory_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_inventory(self):
        """Save inventory to JSON"""
        with open(self.inventory_file, 'w') as f:
            json.dump(self.inventory, f, indent=4)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title Bar with Quick Action Buttons
        title_frame = tk.Frame(self.root, bg='#2d2d44', height=80)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        # Left side - Title
        title_left = tk.Frame(title_frame, bg='#2d2d44')
        title_left.pack(side='left', fill='both', expand=True)
        
        title_label = tk.Label(title_left, text="📦 Smart Inventory Management System",
                              font=('Arial', 20, 'bold'), bg='#2d2d44', fg='white')
        title_label.pack(pady=20, padx=20, anchor='w')
        
        # Right side - Quick Action Icon Buttons
        quick_actions = tk.Frame(title_frame, bg='#2d2d44')
        quick_actions.pack(side='right', padx=20)
        
        # Add Product Icon Button
        add_icon_btn = tk.Button(quick_actions, text="➕",
                                font=('Arial', 28, 'bold'), bg='#3498db', fg='white',
                                width=2, height=1, relief='raised', bd=3,
                                cursor='hand2', command=self.add_product_dialog)
        add_icon_btn.pack(side='left', padx=5)
        self.create_tooltip(add_icon_btn, "Add Product Manually")
        
        # Scanner Icon Button
        scan_icon_btn = tk.Button(quick_actions, text="📷",
                                 font=('Arial', 28), bg='#27ae60', fg='white',
                                 width=2, height=1, relief='raised', bd=3,
                                 cursor='hand2', command=self.toggle_scanner)
        scan_icon_btn.pack(side='left', padx=5)
        self.create_tooltip(scan_icon_btn, "Start Scanner")
        self.scan_icon_btn = scan_icon_btn  # Store reference
        
        # Refresh Icon Button
        refresh_icon_btn = tk.Button(quick_actions, text="🔄",
                                    font=('Arial', 28), bg='#9b59b6', fg='white',
                                    width=2, height=1, relief='raised', bd=3,
                                    cursor='hand2', command=self.update_dashboard)
        refresh_icon_btn.pack(side='left', padx=5)
        self.create_tooltip(refresh_icon_btn, "Refresh Dashboard")
        
        # Create scrollable main container
        canvas = tk.Canvas(self.root, bg='#1e1e2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e2e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Main container inside scrollable frame
        main_container = tk.Frame(scrollable_frame, bg='#1e1e2e')
        main_container.pack(fill='both', expand=True, padx=0, pady=10)
        
        # Left Panel - Statistics
        left_panel = tk.Frame(main_container, bg='#2d2d44', width=400)
        left_panel.pack(side='left', fill='both', padx=(0, 5))
        
        self.setup_statistics_panel(left_panel)
        
        # Right Panel - Inventory List
        right_panel = tk.Frame(main_container, bg='#2d2d44')
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self.setup_inventory_panel(right_panel)
        
        # Bottom Panel - Controls (Now scrollable)
        bottom_panel = tk.Frame(scrollable_frame, bg='#2d2d44', height=200)
        bottom_panel.pack(fill='x', padx=0, pady=(5, 10))
        bottom_panel.pack_propagate(False)
        
        self.setup_control_panel(bottom_panel)
    
    def setup_statistics_panel(self, parent):
        """Setup statistics display panel"""
        stats_label = tk.Label(parent, text="📊 Inventory Statistics",
                              font=('Arial', 16, 'bold'), bg='#2d2d44', fg='white')
        stats_label.pack(pady=15)
        
        # Stats cards container
        stats_container = tk.Frame(parent, bg='#2d2d44')
        stats_container.pack(fill='both', expand=True, padx=10)
        
        # Total Products Card
        self.total_card = self.create_stat_card(stats_container, "Total Products", "0", "#3498db")
        self.total_card.pack(fill='x', pady=10)
        
        # Expired Card (Dark Red)
        self.expired_card = self.create_stat_card(stats_container, "🔴 EXPIRED", "0", "#8b0000")
        self.expired_card.pack(fill='x', pady=10)
        
        # Urgent Card (Red)
        self.urgent_card = self.create_stat_card(stats_container, "🔴 URGENT (< 7 days)", "0", "#e74c3c")
        self.urgent_card.pack(fill='x', pady=10)
        
        # Warning Card (Yellow)
        self.warning_card = self.create_stat_card(stats_container, "🟡 WARNING (7-30 days)", "0", "#f39c12")
        self.warning_card.pack(fill='x', pady=10)
        
        # Safe Card (Green)
        self.safe_card = self.create_stat_card(stats_container, "🟢 SAFE (> 30 days)", "0", "#27ae60")
        self.safe_card.pack(fill='x', pady=10)
        
        # Total Quantity Card
        self.quantity_card = self.create_stat_card(stats_container, "Total Quantity", "0 units", "#9b59b6")
        self.quantity_card.pack(fill='x', pady=10)
    
    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        
        title_label = tk.Label(card, text=title, font=('Arial', 12, 'bold'),
                              bg=color, fg='white')
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(card, text=value, font=('Arial', 20, 'bold'),
                              bg=color, fg='white')
        value_label.pack(pady=(5, 10))
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def setup_inventory_panel(self, parent):
        """Setup inventory list panel"""
        list_label = tk.Label(parent, text="📋 Product Inventory List",
                             font=('Arial', 16, 'bold'), bg='#2d2d44', fg='white')
        list_label.pack(pady=15)
        
        # Search bar
        search_frame = tk.Frame(parent, bg='#2d2d44')
        search_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(search_frame, text="🔍 Search:", font=('Arial', 10),
                bg='#2d2d44', fg='white').pack(side='left', padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_inventory())
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=('Arial', 11), width=30)
        search_entry.pack(side='left', padx=5)
        
        # Treeview for inventory
        tree_frame = tk.Frame(parent, bg='#2d2d44')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient='vertical')
        v_scroll.pack(side='right', fill='y')
        
        h_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        h_scroll.pack(side='bottom', fill='x')
        
        # Treeview
        columns = ('Product', 'Lot No', 'Quantity', 'Expiry Date', 'Days Left', 'Status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                yscrollcommand=v_scroll.set,
                                xscrollcommand=h_scroll.set)
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Define headings
        self.tree.heading('Product', text='Product Name')
        self.tree.heading('Lot No', text='Lot Number')
        self.tree.heading('Quantity', text='Quantity')
        self.tree.heading('Expiry Date', text='Expiry Date')
        self.tree.heading('Days Left', text='Days Left')
        self.tree.heading('Status', text='Status')
        
        # Define column widths
        self.tree.column('Product', width=200)
        self.tree.column('Lot No', width=120)
        self.tree.column('Quantity', width=80)
        self.tree.column('Expiry Date', width=120)
        self.tree.column('Days Left', width=100)
        self.tree.column('Status', width=120)
        
        # Configure tags for color coding
        self.tree.tag_configure('expired', background='#8b0000', foreground='white')
        self.tree.tag_configure('urgent', background='#e74c3c', foreground='white')
        self.tree.tag_configure('warning', background='#f39c12', foreground='white')
        self.tree.tag_configure('safe', background='#27ae60', foreground='white')
        
        self.tree.pack(fill='both', expand=True)
    
    def setup_control_panel(self, parent):
        """Setup control buttons panel"""
        parent.pack_propagate(False)  # Prevent frame from shrinking
        
        # Button container with padding
        container = tk.Frame(parent, bg='#2d2d44')
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        tk.Label(container, text="🎛️ Control Panel", 
                font=('Arial', 14, 'bold'), bg='#2d2d44', fg='white').pack(pady=(0, 10))
        
        # Button frame
        btn_frame = tk.Frame(container, bg='#2d2d44')
        btn_frame.pack(expand=True)
        
        # Add Product Button
        add_btn = tk.Button(btn_frame, text="➕ Add Product\nManually",
                           command=self.add_product_dialog,
                           font=('Arial', 11, 'bold'), bg='#3498db', fg='white',
                           padx=15, pady=12, relief='raised', bd=3,
                           cursor='hand2', width=12, height=2)
        add_btn.grid(row=0, column=0, padx=8, pady=5)
        
        # Scan Barcode Button
        self.scan_btn = tk.Button(btn_frame, text="📷 Start\nScanner",
                                  command=self.toggle_scanner,
                                  font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                                  padx=15, pady=12, relief='raised', bd=3,
                                  cursor='hand2', width=12, height=2)
        self.scan_btn.grid(row=0, column=1, padx=8, pady=5)
        
        # Refresh Button
        refresh_btn = tk.Button(btn_frame, text="🔄 Refresh\nDashboard",
                               command=self.update_dashboard,
                               font=('Arial', 11, 'bold'), bg='#9b59b6', fg='white',
                               padx=15, pady=12, relief='raised', bd=3,
                               cursor='hand2', width=12, height=2)
        refresh_btn.grid(row=0, column=2, padx=8, pady=5)
        
        # Export Button
        export_btn = tk.Button(btn_frame, text="📤 Export\nReport",
                              command=self.export_report,
                              font=('Arial', 11, 'bold'), bg='#e67e22', fg='white',
                              padx=15, pady=12, relief='raised', bd=3,
                              cursor='hand2', width=12, height=2)
        export_btn.grid(row=0, column=3, padx=8, pady=5)
        
        # Clear Expired Button
        clear_btn = tk.Button(btn_frame, text="🗑️ Remove\nExpired",
                             command=self.clear_expired,
                             font=('Arial', 11, 'bold'), bg='#c0392b', fg='white',
                             padx=15, pady=12, relief='raised', bd=3,
                             cursor='hand2', width=12, height=2)
        clear_btn.grid(row=0, column=4, padx=8, pady=5)
    
    def calculate_days_to_expiry(self, expiry_date_str):
        """Calculate days remaining until expiry"""
        try:
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
            today = datetime.now()
            days_remaining = (expiry_date - today).days
            return days_remaining
        except:
            return None
    
    def get_expiry_status(self, days_remaining):
        """Determine expiry status"""
        if days_remaining is None:
            return "UNKNOWN", "unknown"
        
        if days_remaining < 0:
            return "EXPIRED", "expired"
        elif days_remaining <= self.RED_THRESHOLD:
            return "URGENT", "urgent"
        elif days_remaining <= self.YELLOW_THRESHOLD:
            return "WARNING", "warning"
        else:
            return "SAFE", "safe"
    
    def update_dashboard(self):
        """Update all dashboard elements"""
        # Calculate statistics
        total_products = 0
        expired_count = 0
        urgent_count = 0
        warning_count = 0
        safe_count = 0
        total_quantity = 0
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Process inventory
        for product_id, product_data in self.inventory.items():
            for batch in product_data.get('batches', []):
                total_products += 1
                total_quantity += batch.get('quantity', 0)
                
                days = self.calculate_days_to_expiry(batch['expiry_date'])
                status_text, tag = self.get_expiry_status(days)
                
                if status_text == "EXPIRED":
                    expired_count += 1
                elif status_text == "URGENT":
                    urgent_count += 1
                elif status_text == "WARNING":
                    warning_count += 1
                elif status_text == "SAFE":
                    safe_count += 1
                
                # Add to treeview
                days_text = f"{days} days" if days is not None else "Unknown"
                if days is not None and days < 0:
                    days_text = f"{abs(days)} days ago"
                
                self.tree.insert('', 'end', values=(
                    batch['name'],
                    batch['lot_no'],
                    batch['quantity'],
                    batch['expiry_date'],
                    days_text,
                    status_text
                ), tags=(tag,))
        
        # Update statistics cards
        self.total_card.value_label.config(text=str(total_products))
        self.expired_card.value_label.config(text=str(expired_count))
        self.urgent_card.value_label.config(text=str(urgent_count))
        self.warning_card.value_label.config(text=str(warning_count))
        self.safe_card.value_label.config(text=str(safe_count))
        self.quantity_card.value_label.config(text=f"{total_quantity} units")
    
    def filter_inventory(self):
        """Filter inventory based on search"""
        search_term = self.search_var.get().lower()
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Re-populate with filtered results
        for product_id, product_data in self.inventory.items():
            for batch in product_data.get('batches', []):
                if (search_term in batch['name'].lower() or 
                    search_term in batch['lot_no'].lower() or
                    search_term in product_id.lower()):
                    
                    days = self.calculate_days_to_expiry(batch['expiry_date'])
                    status_text, tag = self.get_expiry_status(days)
                    
                    days_text = f"{days} days" if days is not None else "Unknown"
                    if days is not None and days < 0:
                        days_text = f"{abs(days)} days ago"
                    
                    self.tree.insert('', 'end', values=(
                        batch['name'],
                        batch['lot_no'],
                        batch['quantity'],
                        batch['expiry_date'],
                        days_text,
                        status_text
                    ), tags=(tag,))
    
    def add_product_dialog(self):
        """Open dialog to add product manually"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Product Manually")
        dialog.geometry("500x550")
        dialog.configure(bg='#2d2d44')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        title = tk.Label(dialog, text="➕ Add New Product", 
                        font=('Arial', 18, 'bold'), bg='#2d2d44', fg='white')
        title.pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(dialog, bg='#2d2d44')
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Form fields with better styling
        fields = [
            ("Product ID:", tk.StringVar(), "e.g., PROD001"),
            ("Product Name:", tk.StringVar(), "e.g., Fresh Milk 1L"),
            ("Quantity:", tk.StringVar(), "e.g., 50"),
            ("Lot Number:", tk.StringVar(), "e.g., LOT2024001"),
            ("Production Date:", tk.StringVar(), "YYYY-MM-DD"),
            ("Expiry Date:", tk.StringVar(), "YYYY-MM-DD")
        ]
        
        entries = {}
        for i, (label_text, var, placeholder) in enumerate(fields):
            # Label
            label = tk.Label(form_frame, text=label_text, font=('Arial', 11, 'bold'),
                           bg='#2d2d44', fg='white', anchor='w')
            label.grid(row=i*2, column=0, sticky='w', pady=(10, 2))
            
            # Entry with placeholder
            entry = tk.Entry(form_frame, textvariable=var, font=('Arial', 11), 
                           width=35, relief='solid', bd=1)
            entry.grid(row=i*2+1, column=0, sticky='ew', pady=(0, 5))
            entry.insert(0, placeholder)
            entry.config(fg='gray')
            
            # Placeholder behavior
            def on_focus_in(event, e=entry, ph=placeholder):
                if e.get() == ph:
                    e.delete(0, 'end')
                    e.config(fg='black')
            
            def on_focus_out(event, e=entry, ph=placeholder):
                if e.get() == '':
                    e.insert(0, ph)
                    e.config(fg='gray')
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
            
            entries[label_text] = (var, entry, placeholder)
        
        form_frame.columnconfigure(0, weight=1)
        
        # Helper text
        helper = tk.Label(dialog, 
                         text="💡 Tip: Use YYYY-MM-DD format for dates (e.g., 2024-10-15)",
                         font=('Arial', 9), bg='#2d2d44', fg='#f39c12')
        helper.pack(pady=5)
        
        def save_product():
            try:
                # Get values, checking for placeholders
                product_id = entries["Product ID:"][0].get()
                if product_id == entries["Product ID:"][2]:
                    product_id = ""
                
                name = entries["Product Name:"][0].get()
                if name == entries["Product Name:"][2]:
                    name = ""
                
                quantity_str = entries["Quantity:"][0].get()
                if quantity_str == entries["Quantity:"][2]:
                    quantity_str = ""
                
                lot_no = entries["Lot Number:"][0].get()
                if lot_no == entries["Lot Number:"][2]:
                    lot_no = ""
                
                prod_date = entries["Production Date:"][0].get()
                if prod_date == entries["Production Date:"][2]:
                    prod_date = ""
                
                exp_date = entries["Expiry Date:"][0].get()
                if exp_date == entries["Expiry Date:"][2]:
                    exp_date = ""
                
                # Validate
                if not all([product_id, name, quantity_str, lot_no, prod_date, exp_date]):
                    messagebox.showerror("Error", "All fields are required!")
                    return
                
                quantity = int(quantity_str)
                
                # Validate dates
                try:
                    datetime.strptime(prod_date, "%Y-%m-%d")
                    datetime.strptime(exp_date, "%Y-%m-%d")
                except:
                    messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                    return
                
                # Add to inventory
                if product_id not in self.inventory:
                    self.inventory[product_id] = {'batches': []}
                
                batch = {
                    'lot_no': lot_no,
                    'name': name,
                    'quantity': quantity,
                    'production_date': prod_date,
                    'expiry_date': exp_date,
                    'scanned_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                self.inventory[product_id]['batches'].append(batch)
                self.inventory[product_id]['batches'].sort(key=lambda x: x['expiry_date'])
                
                self.save_inventory()
                self.update_dashboard()
                
                # Calculate status
                days = self.calculate_days_to_expiry(exp_date)
                status, _ = self.get_expiry_status(days)
                
                # Show success with status
                messagebox.showinfo("Success", 
                    f"✓ Product Added Successfully!\n\n"
                    f"Name: {name}\n"
                    f"Lot: {lot_no}\n"
                    f"Expiry: {exp_date}\n"
                    f"Status: {status} ({days} days remaining)")
                
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", "Quantity must be a valid number!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {str(e)}")
        
        # Buttons frame
        btn_frame = tk.Frame(dialog, bg='#2d2d44')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Save Product", command=save_product,
                 font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                 padx=30, pady=10, relief='raised', bd=3,
                 cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy,
                 font=('Arial', 12, 'bold'), bg='#c0392b', fg='white',
                 padx=30, pady=10, relief='raised', bd=3,
                 cursor='hand2').pack(side='left', padx=10)
    
    def toggle_scanner(self):
        """Toggle barcode scanner"""
        if not self.scanning:
            self.start_scanner()
        else:
            self.stop_scanner()
    
    def start_scanner(self):
        """Start barcode scanner in new window"""
        self.scanning = True
        self.scan_btn.config(text="⏹️ Stop Scanner", bg='#c0392b')
        
        # Create scanner window
        self.scanner_window = tk.Toplevel(self.root)
        self.scanner_window.title("📷 Barcode Scanner - Live Feed")
        self.scanner_window.geometry("900x700")
        self.scanner_window.configure(bg='#1e1e2e')
        self.scanner_window.protocol("WM_DELETE_WINDOW", self.stop_scanner)
        
        # Title
        title_frame = tk.Frame(self.scanner_window, bg='#2d2d44')
        title_frame.pack(fill='x', pady=10)
        
        tk.Label(title_frame, text="📷 Live Barcode Scanner", 
                font=('Arial', 18, 'bold'), bg='#2d2d44', fg='white').pack(pady=10)
        
        # Camera frame
        camera_frame = tk.Frame(self.scanner_window, bg='#1e1e2e')
        camera_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.camera_label = tk.Label(camera_frame, bg='black')
        self.camera_label.pack()
        
        # Status frame
        status_frame = tk.Frame(self.scanner_window, bg='#2d2d44', height=150)
        status_frame.pack(fill='x', padx=10, pady=10)
        status_frame.pack_propagate(False)
        
        # Last scanned info
        tk.Label(status_frame, text="📦 Last Scanned Product:", 
                font=('Arial', 12, 'bold'), bg='#2d2d44', fg='white').pack(pady=5)
        
        self.last_scan_label = tk.Label(status_frame, text="No products scanned yet", 
                                       font=('Arial', 11), bg='#2d2d44', fg='#95a5a6',
                                       wraplength=800, justify='left')
        self.last_scan_label.pack(pady=5)
        
        # Instructions
        instructions = tk.Label(status_frame, 
                               text="💡 Point your camera at a barcode or QR code\n"
                                    "Format: PRODUCT_ID|NAME|QTY|LOT|PROD_DATE|EXP_DATE",
                               font=('Arial', 9), bg='#2d2d44', fg='#f39c12')
        instructions.pack(pady=5)
        
        # Control buttons
        btn_frame = tk.Frame(self.scanner_window, bg='#1e1e2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="⏹️ Stop Scanner", command=self.stop_scanner,
                 font=('Arial', 12, 'bold'), bg='#c0392b', fg='white',
                 padx=20, pady=8, relief='raised', bd=3,
                 cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🔄 Refresh Dashboard", 
                 command=self.update_dashboard,
                 font=('Arial', 12, 'bold'), bg='#3498db', fg='white',
                 padx=20, pady=8, relief='raised', bd=3,
                 cursor='hand2').pack(side='left', padx=10)
        
        # Start camera thread
        threading.Thread(target=self.scan_loop, daemon=True).start()
    
    def scan_loop(self):
        """Camera scanning loop with enhanced visual feedback"""
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            messagebox.showerror("Error", "Could not open camera!")
            self.stop_scanner()
            return
        
        # Set higher resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        qr_detector = cv2.QRCodeDetector()
        
        try:
            barcode_detector = cv2.barcode.BarcodeDetector()
            barcode_available = True
        except:
            barcode_detector = None
            barcode_available = False
        
        last_scan = ""
        scan_cooldown = 0
        
        while self.scanning and self.camera.isOpened():
            ret, frame = self.camera.read()
            if not ret:
                break
            
            display_frame = frame.copy()
            
            # Add scanning overlay
            height, width = display_frame.shape[:2]
            
            # Draw scanning guide
            center_x, center_y = width // 2, height // 2
            box_size = 300
            
            # Semi-transparent overlay
            overlay = display_frame.copy()
            cv2.rectangle(overlay, 
                         (center_x - box_size, center_y - box_size),
                         (center_x + box_size, center_y + box_size),
                         (0, 255, 0), 3)
            cv2.addWeighted(overlay, 0.3, display_frame, 0.7, 0, display_frame)
            
            # Add text instructions
            cv2.putText(display_frame, "Place barcode/QR code in the box", 
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if scan_cooldown > 0:
                cv2.putText(display_frame, f"Cooldown: {scan_cooldown//10}s", 
                           (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            
            # Try QR code detection
            qr_data, bbox, _ = qr_detector.detectAndDecode(display_frame)
            
            if bbox is not None and qr_data:
                # Draw detection box
                bbox = bbox.astype(int)
                for i in range(len(bbox[0])):
                    pt1 = tuple(bbox[0][i])
                    pt2 = tuple(bbox[0][(i+1) % len(bbox[0])])
                    cv2.line(display_frame, pt1, pt2, (0, 255, 0), 3)
                
                cv2.putText(display_frame, "QR Code Detected!", 
                           (bbox[0][0][0], bbox[0][0][1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Try barcode detection
            barcode_data = None
            if barcode_available and barcode_detector:
                try:
                    retval, barcode_data, decoded_type, points = barcode_detector.detectAndDecode(display_frame)
                    
                    if retval and barcode_data and points is not None:
                        # Draw detection box
                        points = points.astype(int)
                        for i in range(len(points[0])):
                            pt1 = tuple(points[0][i])
                            pt2 = tuple(points[0][(i+1) % len(points[0])])
                            cv2.line(display_frame, pt1, pt2, (255, 0, 0), 3)
                        
                        cv2.putText(display_frame, f"{decoded_type} Detected!", 
                                   (points[0][0][0], points[0][0][1] - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                except:
                    pass
            
            # Process scanned data
            scanned_data = qr_data or barcode_data
            
            if scanned_data and scan_cooldown == 0 and scanned_data != last_scan:
                success = self.process_scanned_data(scanned_data)
                if success:
                    last_scan = scanned_data
                    scan_cooldown = 30  # 3 second cooldown
                    
                    # Visual feedback
                    cv2.rectangle(display_frame, (0, 0), (width, height), 
                                (0, 255, 0), 30)
            
            if scan_cooldown > 0:
                scan_cooldown -= 1
            
            # Convert and display frame
            frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Resize to fit window
            img.thumbnail((860, 580), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            
            if hasattr(self, 'camera_label') and self.camera_label.winfo_exists():
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
            else:
                break
        
        if self.camera:
            self.camera.release()
    
    def process_scanned_data(self, data):
        """Process scanned barcode data with enhanced feedback"""
        try:
            parts = data.split('|')
            if len(parts) == 6:
                product_info = {
                    'product_id': parts[0],
                    'name': parts[1],
                    'quantity': int(parts[2]),
                    'lot_no': parts[3],
                    'production_date': parts[4],
                    'expiry_date': parts[5]
                }
                
                product_id = product_info['product_id']
                
                if product_id not in self.inventory:
                    self.inventory[product_id] = {'batches': []}
                
                batch = {
                    'lot_no': product_info['lot_no'],
                    'name': product_info['name'],
                    'quantity': product_info['quantity'],
                    'production_date': product_info['production_date'],
                    'expiry_date': product_info['expiry_date'],
                    'scanned_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                self.inventory[product_id]['batches'].append(batch)
                self.inventory[product_id]['batches'].sort(key=lambda x: x['expiry_date'])
                
                self.save_inventory()
                self.update_dashboard()
                
                # Calculate expiry status
                days = self.calculate_days_to_expiry(product_info['expiry_date'])
                status, _ = self.get_expiry_status(days)
                
                # Status color
                status_colors = {
                    'EXPIRED': '#8b0000',
                    'URGENT': '#e74c3c',
                    'WARNING': '#f39c12',
                    'SAFE': '#27ae60',
                    'UNKNOWN': '#95a5a6'
                }
                color = status_colors.get(status, '#95a5a6')
                
                # Update last scan label
                if hasattr(self, 'last_scan_label') and self.last_scan_label.winfo_exists():
                    scan_info = (f"✓ {product_info['name']} | "
                               f"Lot: {product_info['lot_no']} | "
                               f"Qty: {product_info['quantity']} | "
                               f"Expiry: {product_info['expiry_date']} | "
                               f"Status: {status}")
                    self.last_scan_label.config(text=scan_info, fg=color)
                
                # Show notification
                self.root.after(0, lambda: messagebox.showinfo(
                    "✓ Product Scanned Successfully!", 
                    f"Product: {product_info['name']}\n"
                    f"Lot Number: {product_info['lot_no']}\n"
                    f"Quantity: {product_info['quantity']} units\n"
                    f"Expiry Date: {product_info['expiry_date']}\n"
                    f"Days Remaining: {days}\n"
                    f"Status: {status}",
                    parent=self.scanner_window if hasattr(self, 'scanner_window') else self.root
                ))
                
                return True
            else:
                # Invalid format
                if hasattr(self, 'last_scan_label') and self.last_scan_label.winfo_exists():
                    self.last_scan_label.config(
                        text=f"❌ Invalid barcode format! Expected 6 parts, got {len(parts)}",
                        fg='#e74c3c'
                    )
                return False
                
        except ValueError as e:
            if hasattr(self, 'last_scan_label') and self.last_scan_label.winfo_exists():
                self.last_scan_label.config(
                    text=f"❌ Error: Quantity must be a number!",
                    fg='#e74c3c'
                )
            return False
        except Exception as e:
            if hasattr(self, 'last_scan_label') and self.last_scan_label.winfo_exists():
                self.last_scan_label.config(
                    text=f"❌ Error processing barcode: {str(e)}",
                    fg='#e74c3c'
                )
            return False
    
    def stop_scanner(self):
        """Stop barcode scanner"""
        self.scanning = False
        if self.camera:
            self.camera.release()
        if hasattr(self, 'scanner_window'):
            self.scanner_window.destroy()
        self.scan_btn.config(text="📷 Start Scanner", bg='#27ae60')
    
    def export_report(self):
        """Export inventory report"""
        try:
            report_file = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("INVENTORY REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                for product_id, product_data in self.inventory.items():
                    for batch in product_data.get('batches', []):
                        days = self.calculate_days_to_expiry(batch['expiry_date'])
                        status, _ = self.get_expiry_status(days)
                        
                        f.write(f"Product: {batch['name']}\n")
                        f.write(f"  ID: {product_id}\n")
                        f.write(f"  Lot: {batch['lot_no']}\n")
                        f.write(f"  Quantity: {batch['quantity']}\n")
                        f.write(f"  Expiry: {batch['expiry_date']}\n")
                        f.write(f"  Status: {status}\n")
                        f.write("-"*80 + "\n")
            
            messagebox.showinfo("Success", f"Report exported to {report_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def clear_expired(self):
        """Remove expired products"""
        if not messagebox.askyesno("Confirm", "Remove all expired products?"):
            return
        
        removed = 0
        for product_id in list(self.inventory.keys()):
            batches = self.inventory[product_id]['batches']
            original_count = len(batches)
            
            self.inventory[product_id]['batches'] = [
                b for b in batches
                if self.calculate_days_to_expiry(b['expiry_date']) >= 0
            ]
            
            removed += original_count - len(self.inventory[product_id]['batches'])
            
            if not self.inventory[product_id]['batches']:
                del self.inventory[product_id]
        
        self.save_inventory()
        self.update_dashboard()
        
        messagebox.showinfo("Success", f"Removed {removed} expired products")

def main():
    root = tk.Tk()
    app = InventoryDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()