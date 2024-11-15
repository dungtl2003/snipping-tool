import sys
import easyocr
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QTextEdit, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QRect

# Define the main application window
class OCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Create main layout and label for displaying the image
        self.setWindowTitle("OCR with Selectable Text Overlay")
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.image_label = QLabel(self)  # Label to display the image
        self.layout.addWidget(self.image_label)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        # Load the image from ImageLabel and run OCR
        image_path = 'image/anh1.png'  # Replace with your image path or update ImageLabel image source
        self.load_and_process_image(image_path)

    def load_and_process_image(self, image_path):
        # Initialize OCR reader
        reader = easyocr.Reader(['en', 'vi'])

        # Read and process the image
        image = cv2.imread(image_path)
        results = reader.readtext(image)
        
        # Convert image to PIL format for easy manipulation
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)

        # Process each detected text area
        for (bbox, text, prob) in results:
            print(text)

            (tl, tr, br, bl) = bbox
            tl = (int(tl[0]), int(tl[1]))
            br = (int(br[0]), int(br[1]))

            text_width = br[0] - tl[0]
            text_height = br[1] - tl[1]
            ###
            # Tính toán tỷ lệ phông chữ ban đầu
            font_scale = 1.0
            font_thickness = 2
            
            # Tính toán kích thước của văn bản với tỷ lệ phông chữ ban đầu
            font = ImageFont.truetype("arial.ttf", int(text_height))
            text_size = draw.textbbox((0, 0), text, font=font)
            text_size_width = text_size[2] - text_size[0]
            text_size_height = text_size[3] - text_size[1]
            
            # Điều chỉnh tỷ lệ phông chữ sao cho văn bản vừa vặn trong bounding box
            font_size = min(text_width / text_size_width, text_height / text_size_height)
            font = ImageFont.truetype("arial.ttf", int(text_height * font_size))


            ###
            
            # Draw rectangle around the detected text area
            draw.rectangle([tl, br], fill=(200, 200, 200))  # Light gray background for text area
            # draw.text((tl[0], tl[1]), text, font=font, fill=(0, 0, 0))

            
            # Create a QTextEdit widget over the bounding box
            text_edit = QTextEdit(self)
            text_edit.setText(text)
            text_edit.setGeometry(QRect(tl[0], tl[1], br[0] - tl[0], br[1] - tl[1]))

            text_edit.setStyleSheet("background: transparent; border: none;")  # Transparent background
            text_edit.setReadOnly(True)  # Make it read-only so text can be copied
            text_edit.show()

        # Convert back to OpenCV format to display
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Display the processed image in QLabel
        self.image_label.setPixmap(QPixmap.fromImage(q_image))
        self.image_label.adjustSize()

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    sys.exit(app.exec())
