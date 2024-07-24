from flask import Flask, jsonify
from deepface import DeepFace
import win32print
import win32ui
from PIL import Image, ImageWin
import qrcode

app = Flask(__name__)

PRINTER_NAME = 'EPSON TM-T20II Receipt'


def analyze_image(image_path):
    try:
        result = DeepFace.analyze(img_path=image_path, actions=['gender', 'race'], detector_backend='mtcnn')
        return result
    except Exception as e:
        print("Failed to analyze image:", e)
        return {}

def print_text(hdc, text, x, y):
    hdc.TextOut(x, y, text)


def print_image(hdc, path, x, y):
    bmp = Image.open(path)
    dib = ImageWin.Dib(bmp)
    dib.draw(hdc.GetHandleOutput(), (x, y, x + bmp.width, y + bmp.height))

def print_receipt(attributes):
    # Generate QR code
    qr_data = "http://invisible-privilege.de"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')
    qr_img.save('qrcode.bmp')

    hPrinter = win32print.OpenPrinter(PRINTER_NAME)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Test", None, "RAW"))
        try:
            win32print.StartPagePrinter(hPrinter)
            
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(PRINTER_NAME)
            hdc.StartDoc("Receipt")
            hdc.StartPage()
            
            # Set font size and style for main text
            main_font_height = 40
            main_font = win32ui.CreateFont({
                "name": "Arial",
                "height": main_font_height,
                "weight": 700,
            })
            hdc.SelectObject(main_font)
            
            # Calculate the center position based on a 60mm width
            page_width = int((60 / 25.4) * hdc.GetDeviceCaps(88))  # Convert 60mm to pixels
            page_start_x = int((10 / 25.4) * hdc.GetDeviceCaps(88))  # Start 10mm from the left edge

            # Centering helper function
            def center_text(hdc, text, y, font_height):
                text_width = hdc.GetTextExtent(text)[0]
                x = page_start_x + (page_width - text_width) // 2
                hdc.TextOut(x, y, text)
                return y + font_height + 20  # Adjust line spacing
            
            y = 100
            y = center_text(hdc, "You were just discriminated", y, main_font_height)
            y = center_text(hdc, "against by AI because:", y, main_font_height)
            y = center_text(hdc, "You were detected as a", y, main_font_height)
            y += 20  # Extra space before attributes
            
            for attribute in attributes:
                y = center_text(hdc, attribute, y, main_font_height)
            
            y += 40  
            
            # Print QR code
            qr_img_path = 'qrcode.bmp'
            qr_img = Image.open(qr_img_path)
            qr_img_width, qr_img_height = qr_img.size
            qr_x = page_start_x + (page_width - qr_img_width) // 2
            print_image(hdc, qr_img_path, qr_x, y)
            y += qr_img_height + 20
            
            # Set font size and style for URL text
            url_font_height = 30
            url_font = win32ui.CreateFont({
                "name": "Arial",
                "height": url_font_height,
                "weight": 400,  # Less bold
            })
            hdc.SelectObject(url_font)

            # Print URL
            y = center_text(hdc, "invisible-privilege.de", y, url_font_height)
            y += 10  # Closer spacing
            
            # Set font size and style back for additional text
            hdc.SelectObject(main_font)
            y = center_text(hdc, "Privilege is invisible to", y, main_font_height)
            y = center_text(hdc, "those who have it", y, main_font_height)
            
            hdc.EndPage()
            hdc.EndDoc()
            
            win32print.EndPagePrinter(hPrinter)
        finally:
            win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)

@app.route('/analyze', methods=['GET'])
def analyze():
    image_path = 'img/captured_face.0.jpg'  # Assume the image is in the same directory as this script

    # Analyze the image for gender and race
    result = analyze_image(image_path)
    
    if isinstance(result, list):
        # If multiple faces detected, take the first one (you can handle multiple faces as needed)
        result = result[0]

    if result:
        gender_result = result.get('gender', {})
        if 'Man' in gender_result and gender_result['Man'] > gender_result.get('Woman', 0):
            gender = 'Man'
        elif 'Woman' in gender_result and gender_result['Woman'] > gender_result.get('Man', 0):
            gender = 'Woman'
        else:
            gender = 'N/A'

        race = result.get('dominant_race', 'N/A')
        
        attributes = [gender, race]
        
        if 'N/A' not in attributes:
            print_receipt(attributes)
        
        return jsonify({'gender': gender, 'race': race}), 200
    else:
        return jsonify({'error': 'Failed to analyze image'}), 500

if __name__ == '__main__':
    app.run(debug=True)
