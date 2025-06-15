#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A5, portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER
from PIL import Image
import argparse
from datetime import datetime

def create_mobile_optimized_pdf(image_folder, output_pdf, title=None, author="Daniel Rosehill"):
    """
    Create a PDF from watermarked images, specifically optimized for mobile viewing.
    Uses A5 portrait orientation which is ideal for mobile devices.
    Includes enhanced readability features for small screens.
    """
    # Get all image files in the folder
    image_files = []
    for ext in ['.png', '.jpg', '.jpeg', '.gif']:
        image_files.extend(list(Path(image_folder).glob(f'*{ext}')))
    
    # Sort image files numerically by their filename
    image_files.sort(key=lambda x: x.name)
    
    if not image_files:
        print(f"No images found in {image_folder}")
        return False
    
    # A5 is a good size for mobile viewing (148mm x 210mm)
    # Using portrait orientation for better mobile viewing
    page_width, page_height = portrait(A5)
    
    # Create a PDF with A5 page size
    c = canvas.Canvas(output_pdf, pagesize=portrait(A5))
    
    # Add title page if title is provided
    if title:
        # Set document information
        c.setTitle(title)
        c.setAuthor(author)
        c.setSubject("Mobile-Optimized Guide")
        
        # Title page styling
        c.setFillColorRGB(0.1, 0.1, 0.1)  # Near black for better contrast
        
        # Draw a light background for better readability
        c.setFillColorRGB(0.97, 0.97, 1.0)  # Very light blue background
        c.rect(0, 0, page_width, page_height, fill=True)
        
        # Title with better spacing for mobile
        c.setFillColorRGB(0.1, 0.1, 0.1)  # Back to near black for text
        c.setFont("Helvetica-Bold", 20)  # Slightly smaller for better fit on mobile
        
        # Handle multi-line titles
        title_lines = title.split('\n')
        for i, line in enumerate(title_lines):
            y_position = page_height*0.65 - (i * 24)
            c.drawCentredString(page_width/2, y_position, line)
        
        # Add date with current date
        current_date = datetime.now().strftime("%B %d, %Y")
        c.setFont("Helvetica", 12)
        c.drawCentredString(page_width/2, page_height*0.5, current_date)
        
        # Add author
        c.setFont("Helvetica", 10)
        c.drawCentredString(page_width/2, page_height*0.45, f"By: {author}")
        
        # Add mobile optimization note
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(page_width/2, page_height*0.4, "Mobile-Optimized Version")
        
        # Add instructions for best viewing
        c.setFont("Helvetica", 8)
        instructions = [
            "For best viewing experience:",
            "• Set your PDF reader to 'Fit to Width'",
            "• Use portrait orientation",
            "• Enable 'Continuous Scrolling' if available"
        ]
        
        for i, line in enumerate(instructions):
            c.drawCentredString(page_width/2, page_height*0.3 - (i * 12), line)
        
        c.showPage()
    
    # Process each image
    for i, img_path in enumerate(image_files):
        print(f"Adding image {i+1}/{len(image_files)}: {img_path.name}")
        
        try:
            # Open the image with PIL
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Calculate scaling to fit the image within the page
            # Leave small margins for better readability on mobile
            margin = 15  # points - slightly smaller margins for more content space
            max_width = page_width - 2*margin
            max_height = page_height - 2*margin - 25  # Extra space for page number
            
            # Calculate scale factor to fit image within page bounds
            width_ratio = max_width / img_width
            height_ratio = max_height / img_height
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate new dimensions
            new_width = img_width * scale_factor
            new_height = img_height * scale_factor
            
            # Calculate position to center the image on the page
            x_pos = (page_width - new_width) / 2
            y_pos = (page_height - new_height) / 2
            
            # Draw the image on the page
            c.drawImage(str(img_path), x_pos, y_pos, width=new_width, height=new_height)
            
            # Add page number at the bottom with better visibility for mobile
            c.setFillColorRGB(0.2, 0.2, 0.2)  # Darker for better contrast
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(page_width/2, 10, f"Page {i+1} of {len(image_files)}")
            
            # Start a new page for the next image
            c.showPage()
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
    
    # Save the PDF
    try:
        c.save()
        print(f"Mobile-optimized PDF created successfully: {output_pdf}")
        return True
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create mobile-optimized PDFs from watermarked images')
    
    # Base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Source directories for watermarked images
    wireless_folder = os.path.join(base_dir, "watermarked", "emergency-wireless-notifiers")
    hfc_folder = os.path.join(base_dir, "watermarked", "hfc-guide")
    
    # Create output directory
    pdf_dir = os.path.join(base_dir, "pdf_guides")
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Create mobile-optimized PDFs
    wireless_pdf = os.path.join(pdf_dir, "emergency_wireless_notifications_guide_mobile.pdf")
    hfc_pdf = os.path.join(pdf_dir, "hfc_guide_mobile.pdf")
    
    if os.path.exists(wireless_folder) and os.path.isdir(wireless_folder):
        print(f"\nCreating mobile-optimized PDF for Emergency Wireless Notifications Guide")
        create_mobile_optimized_pdf(
            wireless_folder, 
            wireless_pdf, 
            "Emergency Wireless Notifications\nConfiguration Guide"
        )
    else:
        print(f"Error: Watermarked directory not found: {wireless_folder}")
    
    if os.path.exists(hfc_folder) and os.path.isdir(hfc_folder):
        print(f"\nCreating mobile-optimized PDF for Home Front Command Guide")
        create_mobile_optimized_pdf(
            hfc_folder, 
            hfc_pdf, 
            "Home Front Command App\nConfiguration Guide"
        )
    else:
        print(f"Error: Watermarked directory not found: {hfc_folder}")
    
    print(f"\nMobile-optimized PDFs saved to: {pdf_dir}")
    print("These PDFs are specifically formatted for optimal viewing on mobile devices.")

if __name__ == "__main__":
    main()
