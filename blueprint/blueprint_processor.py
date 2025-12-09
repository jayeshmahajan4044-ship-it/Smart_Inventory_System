import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import json

class BlueprintProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Blueprint Processing Module")
        self.root.geometry("1400x800")
        self.root.configure(bg="#1e293b")
        
        self.original_image = None
        self.processed_image = None
        self.nodes = []
        self.display_scale = 1.0
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#1e293b")
        title_frame.pack(pady=20)
        
        title = tk.Label(
            title_frame,
            text="Blueprint Processing Module",
            font=("Arial", 24, "bold"),
            bg="#1e293b",
            fg="#60a5fa"
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Upload a marked blueprint to detect PC locations",
            font=("Arial", 12),
            bg="#1e293b",
            fg="#94a3b8"
        )
        subtitle.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#1e293b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Upload and controls
        left_frame = tk.Frame(main_frame, bg="#334155", relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        control_label = tk.Label(
            left_frame,
            text="Controls",
            font=("Arial", 16, "bold"),
            bg="#334155",
            fg="white"
        )
        control_label.pack(pady=10)
        
        # Upload button
        self.upload_btn = tk.Button(
            left_frame,
            text="📁 Upload Blueprint",
            command=self.upload_image,
            font=("Arial", 12),
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        self.upload_btn.pack(pady=10)
        
        # Process button
        self.process_btn = tk.Button(
            left_frame,
            text="🔍 Auto Detect Markers",
            command=self.auto_detect_and_process,
            font=("Arial", 12),
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.process_btn.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            left_frame,
            text="",
            font=("Arial", 10),
            bg="#334155",
            fg="#94a3b8"
        )
        self.status_label.pack(pady=5)
        
        # Image display
        self.image_label = tk.Label(left_frame, bg="#1e293b")
        self.image_label.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Right panel - Results
        right_frame = tk.Frame(main_frame, bg="#334155", relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        result_label = tk.Label(
            right_frame,
            text="Detected Nodes",
            font=("Arial", 16, "bold"),
            bg="#334155",
            fg="white"
        )
        result_label.pack(pady=10)
        
        # Stats frame
        self.stats_frame = tk.Frame(right_frame, bg="#334155")
        self.stats_frame.pack(pady=10)
        
        self.stats_label = tk.Label(
            self.stats_frame,
            text="No nodes detected yet",
            font=("Arial", 11),
            bg="#334155",
            fg="#94a3b8"
        )
        self.stats_label.pack()
        
        # Scrollable frame for nodes
        canvas_frame = tk.Frame(right_frame, bg="#334155")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg="#1e293b", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.nodes_frame = tk.Frame(canvas, bg="#1e293b")
        
        self.nodes_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.nodes_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Detection parameters
        params_frame = tk.LabelFrame(
            right_frame,
            text="Detection Settings",
            font=("Arial", 11, "bold"),
            bg="#334155",
            fg="white"
        )
        params_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Min Distance slider
        tk.Label(
            params_frame,
            text="Min Distance Between Circles:",
            bg="#334155",
            fg="white",
            font=("Arial", 9)
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.min_dist_var = tk.IntVar(value=25)
        self.min_dist_slider = tk.Scale(
            params_frame,
            from_=10,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.min_dist_var,
            bg="#334155",
            fg="white",
            troughcolor="#1e293b",
            highlightthickness=0
        )
        self.min_dist_slider.grid(row=0, column=1, padx=5, pady=5)
        
        # Min Radius slider
        tk.Label(
            params_frame,
            text="Min Radius:",
            bg="#334155",
            fg="white",
            font=("Arial", 9)
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.min_radius_var = tk.IntVar(value=5)
        self.min_radius_slider = tk.Scale(
            params_frame,
            from_=3,
            to=30,
            orient=tk.HORIZONTAL,
            variable=self.min_radius_var,
            bg="#334155",
            fg="white",
            troughcolor="#1e293b",
            highlightthickness=0
        )
        self.min_radius_slider.grid(row=1, column=1, padx=5, pady=5)
        
        # Max Radius slider
        tk.Label(
            params_frame,
            text="Max Radius:",
            bg="#334155",
            fg="white",
            font=("Arial", 9)
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        self.max_radius_var = tk.IntVar(value=50)
        self.max_radius_slider = tk.Scale(
            params_frame,
            from_=20,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.max_radius_var,
            bg="#334155",
            fg="white",
            troughcolor="#1e293b",
            highlightthickness=0
        )
        self.max_radius_slider.grid(row=2, column=1, padx=5, pady=5)
        
        # Sensitivity slider
        tk.Label(
            params_frame,
            text="Sensitivity:",
            bg="#334155",
            fg="white",
            font=("Arial", 9)
        ).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        self.sensitivity_var = tk.IntVar(value=20)
        self.sensitivity_slider = tk.Scale(
            params_frame,
            from_=10,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.sensitivity_var,
            bg="#334155",
            fg="white",
            troughcolor="#1e293b",
            highlightthickness=0
        )
        self.sensitivity_slider.grid(row=3, column=1, padx=5, pady=5)
        
        # Re-detect button
        self.redetect_btn = tk.Button(
            params_frame,
            text="🔄 Re-detect with New Settings",
            command=self.process_blueprint,
            font=("Arial", 9),
            bg="#f59e0b",
            fg="white",
            activebackground="#d97706",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.redetect_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Export button
        self.export_btn = tk.Button(
            right_frame,
            text="💾 Export Configuration",
            command=self.export_config,
            font=("Arial", 11),
            bg="#8b5cf6",
            fg="white",
            activebackground="#7c3aed",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            state=tk.DISABLED
        )
        self.export_btn.pack(pady=10)
    
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Blueprint Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            self.original_image = cv2.imread(file_path)
            self.display_image(self.original_image)
            self.process_btn.config(state=tk.NORMAL)
            self.redetect_btn.config(state=tk.NORMAL)
            self.nodes = []
            self.update_nodes_display()
    
    def display_image(self, cv_image, window_width=600, window_height=500):
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        
        # Calculate scale to fit in window
        height, width = rgb_image.shape[:2]
        scale_w = window_width / width
        scale_h = window_height / height
        self.display_scale = min(scale_w, scale_h)
        
        new_width = int(width * self.display_scale)
        new_height = int(height * self.display_scale)
        
        resized = cv2.resize(rgb_image, (new_width, new_height))
        
        # Convert to PIL Image
        pil_image = Image.fromarray(resized)
        tk_image = ImageTk.PhotoImage(pil_image)
        
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image
    
    def auto_detect_and_process(self):
        """Automatically determine optimal detection parameters"""
        if self.original_image is None:
            return
        
        self.status_label.config(text="🔄 Analyzing image...")
        self.root.update()
        
        # Analyze image to determine optimal parameters
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # 1. Detect potential marker sizes using contour analysis
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze contour sizes
        circular_sizes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                # If reasonably circular (circularity > 0.5)
                if circularity > 0.5 and area > 50:
                    # Estimate radius
                    radius = np.sqrt(area / np.pi)
                    circular_sizes.append(radius)
        
        # Determine radius range
        if circular_sizes:
            circular_sizes = np.array(circular_sizes)
            median_radius = np.median(circular_sizes)
            std_radius = np.std(circular_sizes)
            
            min_radius = max(3, int(median_radius - std_radius * 1.5))
            max_radius = min(100, int(median_radius + std_radius * 1.5))
            
            # Ensure reasonable range
            if max_radius - min_radius < 10:
                min_radius = max(3, int(median_radius * 0.5))
                max_radius = min(100, int(median_radius * 1.5))
        else:
            # Default values if no circles found in pre-analysis
            min_radius = 5
            max_radius = 50
        
        # 2. Determine min distance based on image size and expected density
        # Assume markers should be at least 2x their size apart
        avg_radius = (min_radius + max_radius) / 2
        min_dist = max(15, int(avg_radius * 2))
        
        # 3. Determine sensitivity based on image contrast
        blur = cv2.GaussianBlur(gray, (9, 9), 2)
        edges = cv2.Canny(blur, 50, 150)
        edge_density = np.sum(edges > 0) / (width * height)
        
        # More edges = need higher threshold (less sensitive)
        if edge_density > 0.15:
            sensitivity = 25
        elif edge_density > 0.10:
            sensitivity = 20
        else:
            sensitivity = 15
        
        # Update sliders
        self.min_dist_var.set(min_dist)
        self.min_radius_var.set(min_radius)
        self.max_radius_var.set(max_radius)
        self.sensitivity_var.set(sensitivity)
        
        self.status_label.config(
            text=f"✓ Auto-detected: MinDist={min_dist}, Radius={min_radius}-{max_radius}, Sens={sensitivity}"
        )
        self.root.update()
        
        # Now process with these parameters
        self.process_blueprint()
    
    def process_blueprint(self):
        if self.original_image is None:
            return
        
        # Create a copy for processing
        image = self.original_image.copy()
        height, width = image.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply multiple preprocessing techniques for better detection
        # 1. Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # 2. Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # 3. Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Get parameters from sliders
        min_dist = self.min_dist_var.get()
        min_radius = self.min_radius_var.get()
        max_radius = self.max_radius_var.get()
        sensitivity = self.sensitivity_var.get()
        
        # Detect circles using HoughCircles with adjusted parameters
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=min_dist,
            param1=50,
            param2=sensitivity,
            minRadius=min_radius,
            maxRadius=max_radius
        )
        
        # Also try on thresholded image
        circles2 = cv2.HoughCircles(
            thresh,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=min_dist,
            param1=50,
            param2=sensitivity,
            minRadius=min_radius,
            maxRadius=max_radius
        )
        
        # Combine results
        all_circles = []
        if circles is not None:
            all_circles.extend(circles[0, :])
        if circles2 is not None:
            all_circles.extend(circles2[0, :])
        
        # Remove duplicates (circles that are too close to each other)
        unique_circles = []
        for circle in all_circles:
            x, y, r = circle
            is_duplicate = False
            for uc in unique_circles:
                ux, uy, ur = uc
                dist = np.sqrt((x - ux)**2 + (y - uy)**2)
                if dist < min_dist:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_circles.append(circle)
        
        self.nodes = []
        
        if len(unique_circles) > 0:
            for i, circle in enumerate(unique_circles):
                x, y, r = circle
                x, y, r = int(x), int(y), int(r)
                
                # Draw circle on image
                cv2.circle(image, (x, y), r, (0, 255, 0), 3)
                cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
                
                # Draw label
                label = f"PC-{i+1}"
                cv2.putText(
                    image,
                    label,
                    (x + r + 5, y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                
                # Store node info
                self.nodes.append({
                    'id': i + 1,
                    'x': x,
                    'y': y,
                    'radius': r,
                    'status': 'free'
                })
        
        # If no circles found, show message on image
        if len(self.nodes) == 0:
            cv2.putText(
                image,
                "No circles detected. Try manual adjustment.",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )
            self.status_label.config(text="⚠️ No markers detected - try adjusting settings manually")
        else:
            self.status_label.config(text=f"✓ Detected {len(self.nodes)} markers successfully!")
        
        self.processed_image = image
        self.display_image(image)
        self.update_nodes_display()
        self.export_btn.config(state=tk.NORMAL if len(self.nodes) > 0 else tk.DISABLED)
    
    def update_nodes_display(self):
        # Clear existing nodes
        for widget in self.nodes_frame.winfo_children():
            widget.destroy()
        
        if not self.nodes:
            self.stats_label.config(text="No nodes detected yet")
            return
        
        # Update stats
        free_count = sum(1 for node in self.nodes if node['status'] == 'free')
        occupied_count = len(self.nodes) - free_count
        
        self.stats_label.config(
            text=f"Total PCs: {len(self.nodes)} | Available: {free_count} | Occupied: {occupied_count}"
        )
        
        # Create node buttons in grid
        for i, node in enumerate(self.nodes):
            row = i // 3
            col = i % 3
            
            color = "#10b981" if node['status'] == 'free' else "#ef4444"
            hover_color = "#059669" if node['status'] == 'free' else "#dc2626"
            
            node_frame = tk.Frame(
                self.nodes_frame,
                bg=color,
                relief=tk.RAISED,
                bd=2,
                cursor="hand2"
            )
            node_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Make frame clickable
            node_frame.bind("<Button-1>", lambda e, n=node: self.toggle_node_status(n))
            
            status_icon = "✓" if node['status'] == 'free' else "✗"
            status_text = "Available" if node['status'] == 'free' else "Occupied"
            
            icon_label = tk.Label(
                node_frame,
                text=status_icon,
                font=("Arial", 20, "bold"),
                bg=color,
                fg="white"
            )
            icon_label.pack(pady=(10, 5))
            icon_label.bind("<Button-1>", lambda e, n=node: self.toggle_node_status(n))
            
            id_label = tk.Label(
                node_frame,
                text=f"PC-{node['id']}",
                font=("Arial", 12, "bold"),
                bg=color,
                fg="white"
            )
            id_label.pack()
            id_label.bind("<Button-1>", lambda e, n=node: self.toggle_node_status(n))
            
            status_label = tk.Label(
                node_frame,
                text=status_text,
                font=("Arial", 9),
                bg=color,
                fg="white"
            )
            status_label.pack(pady=(0, 10))
            status_label.bind("<Button-1>", lambda e, n=node: self.toggle_node_status(n))
            
            # Configure grid weights
            self.nodes_frame.grid_columnconfigure(col, weight=1, minsize=120)
    
    def toggle_node_status(self, node):
        node['status'] = 'occupied' if node['status'] == 'free' else 'free'
        self.update_nodes_display()
    
    def export_config(self):
        if not self.nodes:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Configuration"
        )
        
        if file_path:
            config = {
                'blueprint_info': {
                    'width': self.original_image.shape[1],
                    'height': self.original_image.shape[0]
                },
                'nodes': self.nodes
            }
            
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Show success message
            success_window = tk.Toplevel(self.root)
            success_window.title("Success")
            success_window.geometry("300x100")
            success_window.configure(bg="#334155")
            
            msg = tk.Label(
                success_window,
                text="Configuration exported successfully!",
                font=("Arial", 12),
                bg="#334155",
                fg="white"
            )
            msg.pack(expand=True)
            
            ok_btn = tk.Button(
                success_window,
                text="OK",
                command=success_window.destroy,
                bg="#10b981",
                fg="white",
                padx=20,
                pady=5
            )
            ok_btn.pack(pady=10)

def main():
    root = tk.Tk()
    app = BlueprintProcessor(root)
    root.mainloop()

if __name__ == "__main__":
    main()