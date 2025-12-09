# 📦 Smart Inventory Management Dashboard

A desktop-based **smart inventory management system** built with Python and Tkinter, designed to track product batches, monitor expiry dates, and provide real-time insights into stock health.  

The dashboard combines an intuitive UI with barcode/QR scanning to help users manage perishable or time-sensitive products efficiently, minimizing wastage and stock-outs.

---

## ✨ Key Features

- **Interactive Dashboard UI**
  - Modern, card-based layout with dark theme.
  - At-a-glance statistics for total products, total quantity, and expiry risk levels.

- **Expiry-Aware Analytics**
  - Categorizes products into:
    - 🔴 **EXPIRED**
    - 🔴 **URGENT** (≤ 7 days to expiry)
    - 🟡 **WARNING** (7–30 days to expiry)
    - 🟢 **SAFE** (> 30 days to expiry)
  - Automatically computes **days remaining to expiry** for each batch.

- **Product Inventory List**
  - Scrollable, searchable table with:
    - Product Name  
    - Lot Number  
    - Quantity  
    - Expiry Date  
    - Days Left  
    - Status (Expired/Urgent/Warning/Safe)
  - Color-coded rows based on expiry status.

- **Manual Product Entry**
  - Add products via a dedicated form with helpful placeholders:
    - Product ID  
    - Product Name  
    - Quantity  
    - Lot Number  
    - Production Date  
    - Expiry Date  
  - Validates date format (`YYYY-MM-DD`) and quantity.

- **Live Barcode / QR Scanner**
  - Opens a **Live Feed Scanner** window using your webcam.
  - Scans barcodes/QR codes and parses data in this format:  
    `PRODUCT_ID|NAME|QTY|LOT|PROD_DATE|EXP_DATE`
  - Automatically updates inventory, sorts by expiry date, and shows the last scanned product with color-coded status.

- **Smart Search & Filters**
  - Real-time search over:
    - Product Name  
    - Lot Number  
    - Product ID  

- **Reporting & Cleanup**
  - Export inventory snapshot to a text-based report.
  - One-click removal of all **expired** batches from the system.

---

## 🧠 Tech Stack

- **Language:** Python 3.x  
- **GUI Framework:** Tkinter  
- **Data Storage:** JSON (local file-based `inventory_database.json`)  
- **Computer Vision:** OpenCV (for live camera feed & scanning overlay)  
- **Imaging:** Pillow (PIL) for rendering OpenCV frames into Tkinter

---

## 📂 Project Structure

```text
.
├── inventory_dashboard.py      # Main application script (this file)
├── inventory_database.json     # Auto-created JSON database for inventory
└── inventory_report_*.txt      # Exported reports (generated at runtime)
