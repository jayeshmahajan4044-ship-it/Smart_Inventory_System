import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont, ImageTk
import qrcode
from datetime import datetime
import os
from tkcalendar import DateEntry

class ModernBarcodeGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Barcode & QR Code Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Output folder
        self.output_folder = "product_barcodes"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        # Store current preview image
        self.preview_image = None
        self.current_label_image = None
        
        # Color scheme
        self.colors = {
            'primary': '#2196F3',
            'primary_dark': '#1976D2',
            'secondary': '#4CAF50',
            'danger': '#F44336',
            'background': '#f0f0f0',
            'card': '#ffffff',
            'text': '#333333',
            'text_light': '#666666',
            'border': '#e0e0e0'
        }
        
        # Configure styles
        self.setup_styles()
        
        # Create UI
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
    def setup_styles(self):
        """Setup modern UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10),
                       font=('Segoe UI', 10, 'bold'))
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_dark'])])
        
        style.configure('Secondary.TButton',
                       background=self.colors['secondary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8),
                       font=('Segoe UI', 9, 'bold'))
        
        # Configure label styles
        style.configure('Title.TLabel',
                       background=self.colors['primary'],
                       foreground='white',
                       font=('Segoe UI', 20, 'bold'),
                       padding=10)
        
        style.configure('Card.TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 10))
        
        style.configure('Heading.TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 12, 'bold'))
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       borderwidth=1,
                       relief='solid',
                       padding=8)
        
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame,
                              text="📦 Barcode & QR Code Generator",
                              bg=self.colors['primary'],
                              fg='white',
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=20)
        
    def create_main_content(self):
        """Create main content area"""
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Input form
        left_panel = self.create_input_panel(main_container)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel - Preview and actions
        right_panel = self.create_preview_panel(main_container)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
    def create_input_panel(self, parent):
        """Create input form panel"""
        panel = tk.Frame(parent, bg=self.colors['card'], relief='solid', borderwidth=1)
        
        # Panel header
        header = tk.Frame(panel, bg=self.colors['card'])
        header.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(header,
                text="Product Information",
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        
        tk.Label(header,
                text="Enter product details to generate barcode/QR code",
                bg=self.colors['card'],
                fg=self.colors['text_light'],
                font=('Segoe UI', 9)).pack(anchor='w', pady=(5, 0))
        
        # Scrollable form container
        canvas = tk.Canvas(panel, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        self.create_form_fields(form_frame)
        
        return panel
        
    def create_form_fields(self, parent):
        """Create all form input fields"""
        # Product ID
        self.create_field(parent, "Product ID *", 'product_id', 0,
                         placeholder="e.g., PROD001")
        
        # Product Name
        self.create_field(parent, "Product Name *", 'product_name', 1,
                         placeholder="e.g., Fresh Milk 1L")
        
        # Price
        self.create_field(parent, "Price (₹) *", 'price', 2,
                         placeholder="e.g., 70")
        
        # Quantity
        self.create_field(parent, "Quantity *", 'quantity', 3,
                         placeholder="e.g., 50")
        
        # Lot Number
        self.create_field(parent, "Lot Number *", 'lot_no', 4,
                         placeholder="e.g., LOT2024001")
        
        # Barcode Type Selection
        tk.Label(parent,
                text="Barcode Type *",
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').grid(row=10, column=0, sticky='w', pady=(25, 5), columnspan=2)
        
        barcode_frame = tk.Frame(parent, bg=self.colors['card'])
        barcode_frame.grid(row=11, column=0, columnspan=2, sticky='ew', pady=(0, 5))
        
        self.barcode_type = tk.StringVar(value='both')
        
        types = [
            ('📊 Both (Barcode + QR)', 'both'),
            ('📏 Barcode Only', 'barcode'),
            ('⬜ QR Code Only', 'qr')
        ]
        
        for i, (text, value) in enumerate(types):
            rb = tk.Radiobutton(barcode_frame,
                               text=text,
                               variable=self.barcode_type,
                               value=value,
                               bg=self.colors['card'],
                               fg=self.colors['text'],
                               font=('Segoe UI', 10),
                               selectcolor=self.colors['primary'],
                               activebackground=self.colors['card'])
            rb.pack(anchor='w', pady=5)
        
        # Production Date
        self.create_date_field(parent, "Production Date *", 'production_date', 6)
        
        # Expiry Date
        self.create_date_field(parent, "Expiry Date *", 'expiry_date', 7)
        
        # Action buttons
        button_frame = tk.Frame(parent, bg=self.colors['card'])
        button_frame.grid(row=16, column=0, columnspan=2, sticky='ew', pady=(30, 20))
        
        generate_btn = tk.Button(button_frame,
                                text="🚀 Generate Label",
                                command=self.generate_label,
                                bg=self.colors['primary'],
                                fg='white',
                                font=('Segoe UI', 11, 'bold'),
                                relief='flat',
                                cursor='hand2',
                                padx=30,
                                pady=12)
        generate_btn.pack(fill='x', pady=(0, 10))
        
        clear_btn = tk.Button(button_frame,
                             text="🗑️ Clear Form",
                             command=self.clear_form,
                             bg='white',
                             fg=self.colors['text'],
                             font=('Segoe UI', 10),
                             relief='solid',
                             borderwidth=1,
                             cursor='hand2',
                             padx=20,
                             pady=10)
        clear_btn.pack(fill='x')
        
    def create_field(self, parent, label_text, var_name, row, placeholder=""):
        """Create a form field"""
        tk.Label(parent,
                text=label_text,
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').grid(row=row*2, column=0, sticky='w', pady=(15, 5))
        
        entry = tk.Entry(parent,
                        font=('Segoe UI', 10),
                        relief='solid',
                        borderwidth=1,
                        bg='white',
                        fg=self.colors['text'])
        entry.grid(row=row*2+1, column=0, columnspan=2, sticky='ew', pady=(0, 5))
        entry.insert(0, placeholder)
        entry.config(fg=self.colors['text_light'])
        
        # Placeholder behavior
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=self.colors['text'])
        
        def on_focus_out(event):
            if entry.get() == '':
                entry.insert(0, placeholder)
                entry.config(fg=self.colors['text_light'])
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        
        setattr(self, var_name, entry)
        
    def create_date_field(self, parent, label_text, var_name, row):
        """Create a date picker field"""
        tk.Label(parent,
                text=label_text,
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 10, 'bold'),
                anchor='w').grid(row=row*2, column=0, sticky='w', pady=(15, 5))
        
        date_entry = DateEntry(parent,
                              font=('Segoe UI', 10),
                              background=self.colors['primary'],
                              foreground='white',
                              borderwidth=1,
                              date_pattern='yyyy-mm-dd')
        date_entry.grid(row=row*2+1, column=0, columnspan=2, sticky='ew', pady=(0, 5))
        
        setattr(self, var_name, date_entry)
        
    def create_preview_panel(self, parent):
        """Create preview panel"""
        panel = tk.Frame(parent, bg=self.colors['card'], relief='solid', borderwidth=1)
        
        # Panel header
        header = tk.Frame(panel, bg=self.colors['card'])
        header.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(header,
                text="Preview & Actions",
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        
        # Preview area
        preview_container = tk.Frame(panel, bg='#f5f5f5', relief='solid', borderwidth=1)
        preview_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.preview_label = tk.Label(preview_container,
                                     text="📄\n\nPreview will appear here\n\nGenerate a label to see the preview",
                                     bg='#f5f5f5',
                                     fg=self.colors['text_light'],
                                     font=('Segoe UI', 12),
                                     justify='center')
        self.preview_label.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Action buttons
        action_frame = tk.Frame(panel, bg=self.colors['card'])
        action_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        save_btn = tk.Button(action_frame,
                            text="💾 Save Label",
                            command=self.save_label,
                            bg=self.colors['secondary'],
                            fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat',
                            cursor='hand2',
                            padx=20,
                            pady=10,
                            state='disabled')
        save_btn.pack(fill='x', pady=(0, 10))
        self.save_btn = save_btn
        
        samples_btn = tk.Button(action_frame,
                               text="📦 Generate Sample Products",
                               command=self.generate_samples,
                               bg='white',
                               fg=self.colors['primary'],
                               font=('Segoe UI', 10),
                               relief='solid',
                               borderwidth=1,
                               cursor='hand2',
                               padx=20,
                               pady=10)
        samples_btn.pack(fill='x')
        
        return panel
        
    def create_footer(self):
        """Create footer section"""
        footer = tk.Frame(self.root, bg=self.colors['card'], height=50)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        
        
    def encode_product_data(self, product_id, name, quantity, lot_no, production_date, expiry_date):
        """Encode product data in scanner-compatible format"""
        encoded_data = f"{product_id}|{name}|{quantity}|{lot_no}|{production_date}|{expiry_date}"
        return encoded_data
    
    def create_code128_barcode(self, encoded_data):
        """Generate Code128 barcode"""
        try:
            code128 = Code128(encoded_data, writer=ImageWriter())
            filename = code128.save(f'{self.output_folder}/temp_barcode',
                                   options={'write_text': False, 'module_height': 15, 'module_width': 0.3})
            
            with Image.open(filename) as img:
                barcode_img = img.copy()
            
            try:
                os.remove(filename)
            except:
                pass
            
            return barcode_img
        except Exception as e:
            messagebox.showerror("Error", f"Code128 generation failed: {e}")
            return None
    
    def create_qr_code(self, encoded_data):
        """Generate QR code"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(encoded_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        return qr_img
    
    def create_product_label(self, product_id, name, price, quantity, lot_no,
                            production_date, expiry_date, barcode_type='both'):
        """Create complete product label with barcode/QR code"""
        
        encoded_data = self.encode_product_data(product_id, name, quantity, lot_no,
                                               production_date, expiry_date)
        
        label_width = 700
        label_height = 500 if barcode_type == 'both' else 450
        label = Image.new('RGB', (label_width, label_height), 'white')
        draw = ImageDraw.Draw(label)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 26)
            info_font = ImageFont.truetype("arial.ttf", 16)
            small_font = ImageFont.truetype("arial.ttf", 12)
            code_font = ImageFont.truetype("courier.ttf", 10)
        except:
            title_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            code_font = ImageFont.load_default()
        
        draw.rectangle([5, 5, label_width-5, label_height-5], outline='black', width=3)
        
        y_position = 25
        draw.text((label_width//2, y_position), name,
                 fill='black', font=title_font, anchor='mt')
        
        y_position = 70
        line_spacing = 28
        
        info_lines = [
            f"Product ID: {product_id}",
            f"Price: ₹{price:.2f}",
            f"Quantity: {quantity} units",
            f"Lot No: {lot_no}",
            f"Mfg Date: {production_date}",
            f"Exp Date: {expiry_date}"
        ]
        
        for line in info_lines:
            draw.text((20, y_position), line, fill='black', font=info_font)
            y_position += line_spacing
        
        current_y = y_position + 20
        
        if barcode_type in ['barcode', 'both']:
            barcode_img = self.create_code128_barcode(encoded_data)
            if barcode_img:
                barcode_width = 600
                barcode_height = int(barcode_img.height * (barcode_width / barcode_img.width))
                barcode_resized = barcode_img.resize((barcode_width, barcode_height))
                
                barcode_x = (label_width - barcode_width) // 2
                label.paste(barcode_resized, (barcode_x, current_y))
                current_y += barcode_height + 5
                
                draw.text((label_width//2, current_y), "Scan this barcode",
                         fill='black', font=small_font, anchor='mt')
        
        if barcode_type in ['qr', 'both']:
            qr_img = self.create_qr_code(encoded_data)
            qr_size = 150
            qr_resized = qr_img.resize((qr_size, qr_size))
            
            if barcode_type == 'both':
                qr_x = label_width - qr_size - 20
                qr_y = 70
            else:
                qr_x = (label_width - qr_size) // 2
                qr_y = current_y
            
            label.paste(qr_resized, (qr_x, qr_y))
            
            if barcode_type == 'qr':
                draw.text((label_width//2, qr_y + qr_size + 10), "Scan QR Code",
                         fill='black', font=small_font, anchor='mt')
        
        format_text = "Format: PROD_ID|NAME|QTY|LOT|MFG_DATE|EXP_DATE"
        draw.text((label_width//2, label_height - 15), format_text,
                 fill='gray', font=code_font, anchor='mt')
        
        return label, encoded_data
    
    def validate_inputs(self):
        """Validate all form inputs"""
        # Get values and check for placeholders
        product_id = self.product_id.get().strip()
        if product_id.startswith('e.g.,') or not product_id:
            messagebox.showwarning("Validation Error", "Please enter a valid Product ID")
            return False
        
        name = self.product_name.get().strip()
        if name.startswith('e.g.,') or not name:
            messagebox.showwarning("Validation Error", "Please enter a valid Product Name")
            return False
        
        try:
            price = float(self.price.get().strip().replace('e.g.,', '').strip())
            if price <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Validation Error", "Please enter a valid Price (positive number)")
            return False
        
        try:
            quantity = int(self.quantity.get().strip().replace('e.g.,', '').strip())
            if quantity <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Validation Error", "Please enter a valid Quantity (positive integer)")
            return False
        
        lot_no = self.lot_no.get().strip()
        if lot_no.startswith('e.g.,') or not lot_no:
            messagebox.showwarning("Validation Error", "Please enter a valid Lot Number")
            return False
        
        return True
    
    def generate_label(self):
        """Generate barcode label"""
        if not self.validate_inputs():
            return
        
        try:
            # Get cleaned values
            product_id = self.product_id.get().strip()
            name = self.product_name.get().strip()
            price = float(self.price.get().strip().replace('e.g.,', '').strip())
            quantity = int(self.quantity.get().strip().replace('e.g.,', '').strip())
            lot_no = self.lot_no.get().strip()
            production_date = self.production_date.get()
            expiry_date = self.expiry_date.get()
            barcode_type = self.barcode_type.get()
            
            # Generate label
            label, encoded_data = self.create_product_label(
                product_id, name, price, quantity, lot_no,
                production_date, expiry_date, barcode_type
            )
            
            self.current_label_image = label
            
            # Display preview
            preview_width = 500
            preview_height = int(label.height * (preview_width / label.width))
            preview_img = label.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(preview_img)
            self.preview_label.config(image=photo, text='')
            self.preview_label.image = photo
            
            # Enable save button
            self.save_btn.config(state='normal')
            
            messagebox.showinfo("Success", f"Label generated successfully!\n\nEncoded Data:\n{encoded_data}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate label:\n{str(e)}")
    
    def save_label(self):
        """Save the generated label"""
        if self.current_label_image is None:
            messagebox.showwarning("Warning", "No label to save. Generate a label first.")
            return
        
        try:
            product_id = self.product_id.get().strip()
            lot_no = self.lot_no.get().strip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            default_filename = f"label_{product_id}_{lot_no}_{timestamp}.png"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialdir=self.output_folder,
                initialfile=default_filename
            )
            
            if filepath:
                self.current_label_image.save(filepath, 'PNG')
                messagebox.showinfo("Success", f"Label saved successfully!\n\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save label:\n{str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.product_id.delete(0, tk.END)
        self.product_name.delete(0, tk.END)
        self.price.delete(0, tk.END)
        self.quantity.delete(0, tk.END)
        self.lot_no.delete(0, tk.END)
        self.production_date.set_date(datetime.now())
        self.expiry_date.set_date(datetime.now())
        self.barcode_type.set('both')
        
        # Reset placeholders
        self.product_id.insert(0, "e.g., PROD001")
        self.product_id.config(fg=self.colors['text_light'])
        self.product_name.insert(0, "e.g., Fresh Milk 1L")
        self.product_name.config(fg=self.colors['text_light'])
        self.price.insert(0, "e.g., 3.99")
        self.price.config(fg=self.colors['text_light'])
        self.quantity.insert(0, "e.g., 50")
        self.quantity.config(fg=self.colors['text_light'])
        self.lot_no.insert(0, "e.g., LOT2024001")
        self.lot_no.config(fg=self.colors['text_light'])
        
        # Clear preview
        self.preview_label.config(image='',
                                 text="📄\n\nPreview will appear here\n\nGenerate a label to see the preview")
        self.current_label_image = None
        self.save_btn.config(state='disabled')
    
    def generate_samples(self):
        """Generate sample products"""
        samples = [
            {
                'product_id': 'PROD001',
                'name': 'Fresh Milk 1L',
                'price': 3.99,
                'quantity': 50,
                'lot_no': 'LOT2024001',
                'production_date': '2024-09-20',
                'expiry_date': '2024-10-05'
            },
            {
                'product_id': 'PROD002',
                'name': 'Organic Beans Can',
                'price': 2.50,
                'quantity': 100,
                'lot_no': 'LOT2024002',
                'production_date': '2024-08-15',
                'expiry_date': '2026-08-15'
            },
            {
                'product_id': 'PROD003',
                'name': 'Whole Wheat Bread',
                'price': 4.25,
                'quantity': 30,
                'lot_no': 'LOT2024003',
                'production_date': '2024-09-25',
                'expiry_date': '2024-10-10'
            }
        ]
        
        count = 0
        for sample in samples:
            try:
                label, _ = self.create_product_label(
                    sample['product_id'],
                    sample['name'],
                    sample['price'],
                    sample['quantity'],
                    sample['lot_no'],
                    sample['production_date'],
                    sample['expiry_date'],
                    'both'
                )
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.output_folder}/sample_{sample['product_id']}_{timestamp}.png"
                label.save(filename, 'PNG')
                count += 1
            except Exception as e:
                print(f"Error generating sample {sample['product_id']}: {e}")
        
        messagebox.showinfo("Success", f"Generated {count} sample labels!\n\nLocation: {os.path.abspath(self.output_folder)}")

def main():
    root = tk.Tk()
    app = ModernBarcodeGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()