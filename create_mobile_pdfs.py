#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from PIL import Image
import argparse

def create_pdf_from_images(image_folder, output_pdf, title=None):
    """
    Create a PDF from all images in a folder, optimized for mobile viewing.
    Uses A5 portrait orientation which is a good size for mobile devices.
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
    page_width, page_height = A5
    
    # Create a PDF with A5 page size
    c = canvas.Canvas(output_pdf, pagesize=A5)
    
    # Add title page if title is provided
    if title:
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(page_width/2, page_height*0.6, title)
        
        # Add date
        c.setFont("Helvetica", 14)
        c.drawCentredString(page_width/2, page_height*0.5, "June 15, 2025")
        
        # Add author
        c.setFont("Helvetica", 12)
        c.drawCentredString(page_width/2, page_height*0.45, "By: Daniel Rosehill")
        
        c.showPage()
    
    # Process each image
    for i, img_path in enumerate(image_files):
        print(f"Adding image {i+1}/{len(image_files)}: {img_path.name}")
        
        try:
            # Open the image with PIL
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Calculate scaling to fit the image within the page
            # Leave small margins
            margin = 20  # points
            max_width = page_width - 2*margin
            max_height = page_height - 2*margin
            
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
            
            # Add page number at the bottom
            c.setFont("Helvetica", 8)
            c.drawCentredString(page_width/2, 20, f"Page {i+1}")
            
            # Start a new page for the next image
            c.showPage()
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
    
    # Save the PDF
    try:
        c.save()
        print(f"PDF created successfully: {output_pdf}")
        return True
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create mobile-friendly PDFs from image folders')
    parser.add_argument('--source', choices=['original', 'watermarked', 'watermarked_legible'], 
                        default='watermarked_legible', 
                        help='Which image set to use (default: watermarked_legible)')
    args = parser.parse_args()
    
    # Base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Source directories based on user choice
    if args.source == 'original':
        wireless_folder = os.path.join(base_dir, "emergency-wireless-notifiers")
        hfc_folder = os.path.join(base_dir, "hfc-guide")
    else:
        wireless_folder = os.path.join(base_dir, args.source, "emergency-wireless-notifiers")
        hfc_folder = os.path.join(base_dir, args.source, "hfc-guide")
    
    # Create output directory
    pdf_dir = os.path.join(base_dir, "pdf_guides")
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Create PDFs
    wireless_pdf = os.path.join(pdf_dir, "emergency_wireless_notifications_guide.pdf")
    hfc_pdf = os.path.join(pdf_dir, "hfc_guide.pdf")
    
    if os.path.exists(wireless_folder) and os.path.isdir(wireless_folder):
        print(f"\nCreating PDF for Emergency Wireless Notifications Guide")
        create_pdf_from_images(
            wireless_folder, 
            wireless_pdf, 
            "Emergency Wireless Notifications\nConfiguration Guide"
        )
    
    if os.path.exists(hfc_folder) and os.path.isdir(hfc_folder):
        print(f"\nCreating PDF for Home Front Command Guide")
        create_pdf_from_images(
            hfc_folder, 
            hfc_pdf, 
            "Home Front Command App\nConfiguration Guide"
        )
    
    print(f"\nPDFs saved to: {pdf_dir}")

if __name__ == "__main__":
    main()
