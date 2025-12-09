import cv2
from pyzbar import pyzbar

def decode_qr_code(frame, qr_detector):
    """Decode QR codes using OpenCV's built-in detector"""
    data, bbox, _ = qr_detector.detectAndDecode(frame)
    
    if bbox is not None and data:
        # Draw bounding box
        bbox = bbox.astype(int)
        n = len(bbox[0])
        for i in range(n):
            pt1 = tuple(bbox[0][i])
            pt2 = tuple(bbox[0][(i+1) % n])
            cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
        
        # Display the data
        text = f"QR Code: {data}"
        cv2.putText(frame, text, (bbox[0][0][0], bbox[0][0][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        print(f"Detected QR Code: {data}")
        return True
    
    return False


def decode_barcode(frame):
    """Decode barcodes using pyzbar"""
    barcodes = pyzbar.decode(frame)
    found = False
    
    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)

        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        text = f"{barcode_type}: {barcode_data}"
        cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        print(f"Detected {barcode_type}: {barcode_data}")
        found = True
    
    return found


def main():
    """Main function to capture video and scan codes"""
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Initialize QR code detector
    qr_detector = cv2.QRCodeDetector()
    
    print("\nQR Code and Barcode Scanner Started")
    print("Press 'q' to quit")
    print("=" * 50)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to capture frame")
            break
        
        # Decode QR codes (green box)
        decode_qr_code(frame, qr_detector)
        
        # Decode barcodes (blue box)
        decode_barcode(frame)
        
        # Display instructions
        cv2.putText(frame, "Press 'q' to quit", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        status = "QR (Green) | Barcode (Blue)"
        cv2.putText(frame, status, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show the frame
        cv2.imshow('QR Code and Barcode Scanner', frame)
        
        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
