from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fpdf import FPDF
from PIL import Image
from database_setup import *
import os 
from datetime import datetime

class PDFGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Generator")
        self.setGeometry(100, 100, 400, 200)
        self.setStyleSheet("background-color: #333; color: white;")
        self.print_button = QPushButton("Print Report", self)
        self.print_button.setGeometry(150, 80, 100, 30)
        self.print_button.clicked.connect(self.generate_pdf)

    def generate_pdf(self):
        engine = create_engine('sqlite:///database.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        recorded_videos = session.query(RecordedVideo).all()

        class PDF(FPDF):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.recorded_video_id = None
                self.created_at = None

            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'Recorded IMAGES Report', 0, 1, 'C')

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                footer_text = f'Record ID: {self.recorded_video_id} | Date: {self.created_at}'
                self.cell(0, 10, footer_text, 0, 0, 'C')

        pdf = PDF()
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)

        pdf.cell(0, 10, 'Software Developed By Group 04', 0, 1, 'C')
        pdf.ln(10)

        for recorded_video in recorded_videos:
            recorded_video_id = recorded_video.recorded_video_id
            created_at = recorded_video.created_at
            photo_path = recorded_video.exit_video_path
            
            with Image.open(photo_path) as img:
                img_width, img_height = img.size
                aspect_ratio = img_width / img_height
                new_height = 120
                new_width = int(new_height * aspect_ratio)
                img_resized = img.resize((new_width, new_height))
                img_path = "temp_img.jpg"
                img_resized.save(img_path)
                pdf.image(img_path, x=pdf.w / 2 - new_width / 2, w=new_width, h=new_height)
                pdf.recorded_video_id = recorded_video_id
                pdf.created_at = created_at
                pdf.footer()
                pdf.ln(10)

        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")

        if file_path:
            pdf.output(file_path)
            QMessageBox.information(self, "Success", "PDF report generated successfully.")
        else:
            QMessageBox.warning(self, "Warning", "No file selected.")

        os.remove(img_path)

        session.close()

# app = QApplication([])
# window = PDFGenerator()
# window.show()
# app.exec_()
