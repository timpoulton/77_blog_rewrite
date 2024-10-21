from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import logging
from keep_alive import keep_alive  # Import keep_alive function

# Call the keep_alive function to start the ping server
keep_alive()

# Initialize the Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the fonts (ensure these files are available in your project)
font_path = "NeueMontreal-Regular.otf"
font_title = ImageFont.truetype(font_path, 50)  # Font size for title text
font_main_1 = ImageFont.truetype(font_path, 42)  # Font size for main text on image 1
font_main_2 = ImageFont.truetype(font_path, 32)  # Font size for main text on image 2
font_footer = ImageFont.truetype(font_path, 25)  # Font size for footer text

# Function to draw wrapped text for all images (no highlight)
def draw_text(draw, text, font, text_position, max_width, text_color):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width > max_width:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)

    # Add the last line
    lines.append(' '.join(current_line))

    # Draw each line of text without any highlight
    y_offset = text_position[1]
    for line in lines:
        draw.text((text_position[0], y_offset), line, font=font, fill=text_color)
        line_height = draw.textbbox((0, 0), line, font=font)[3]
        y_offset += line_height + 10  # Add space between lines

# Root endpoint to avoid 404 errors
@app.route('/')
def home():
    return "Flask server is running. Available endpoints: /process-image1, /process-image2, /process-image3"

# Endpoint for processing the first image (no highlight)
@app.route('/process-image1', methods=['POST'])
def process_image_1():
    try:
        data = request.json
        image_url_1 = data.get('image_url_1')
        image_1_text = data.get('image_1_text')
        footer_text = data.get('footer_text')

        # Validate input
        if not all([image_url_1, image_1_text, footer_text]):
            return jsonify({"error": "Missing required data"}), 400

        # Log request data
        logging.info(f"Processing image1 with URL: {image_url_1}")

        # Download and process image 1 (with SSL verification disabled)
        response_1 = requests.get(image_url_1, verify=False)  # SSL verification disabled
        image_1 = Image.open(BytesIO(response_1.content)).resize((1080, 1350), Image.LANCZOS)
        draw_1 = ImageDraw.Draw(image_1)

        # Draw text for image 1 (no highlight)
        draw_text(draw_1, image_1_text, font_main_1, (50, 200), 980, (255, 255, 255))
        draw_text(draw_1, footer_text, font_footer, (50, 1100), 980, (255, 255, 255))

        # Save image to memory
        output_1 = BytesIO()
        image_1.save(output_1, format='PNG', quality=100, optimize=True)
        output_1.seek(0)

        # Return image 1
        return send_file(output_1, mimetype='image/png')

    except Exception as e:
        logging.error(f"Error processing image 1: {str(e)}")
        return jsonify({"error": str(e)}), 400

# Endpoint for processing the second image (no highlight)
@app.route('/process-image2', methods=['POST'])
def process_image_2():
    try:
        data = request.json
        image_url_2 = data.get('image_url_2')
        image_2_text = data.get('image_2_text')
        footer_text = data.get('footer_text')

        # Validate input
        if not all([image_url_2, image_2_text, footer_text]):
            return jsonify({"error": "Missing required data"}), 400

        # Log request data
        logging.info(f"Processing image2 with URL: {image_url_2}")

        # Download and process image 2 (with SSL verification disabled)
        response_2 = requests.get(image_url_2, verify=False)  # SSL verification disabled
        image_2 = Image.open(BytesIO(response_2.content)).resize((1080, 1350), Image.LANCZOS)
        draw_2 = ImageDraw.Draw(image_2)

        # Split the input text into sentences and draw them
        sentences = image_2_text.split('. ')
        y_offset = 200  # Starting Y position for text
        for sentence in sentences:
            if sentence.strip():
                bullet_point = '• ' + sentence.strip() + '.'
                draw_text(draw_2, bullet_point, font_main_2, (50, y_offset), 980, (255, 255, 255))
                y_offset += 200  # Add space between bullet points

        # Draw the footer text
        draw_text(draw_2, footer_text, font_footer, (50, 1100), 980, (255, 255, 255))

        # Save image to memory
        output_2 = BytesIO()
        image_2.save(output_2, format='PNG', quality=100, optimize=True)
        output_2.seek(0)

        # Return image 2
        return send_file(output_2, mimetype='image/png')

    except Exception as e:
        logging.error(f"Error processing image 2: {str(e)}")
        return jsonify({"error": str(e)}), 400

# Endpoint for processing the third image (no highlight, with overlay)
@app.route('/process-image3', methods=['POST'])
def process_image_3():
    try:
        data = request.json
        background_url = data.get('background_url')
        overlay_url = data.get('overlay_url')
        overlay_text = data.get('overlay_text')

        # Validate input
        if not all([background_url, overlay_url, overlay_text]):
            return jsonify({"error": "Missing required data"}), 400

        # Log request data
        logging.info(f"Processing image3 with background URL: {background_url} and overlay URL: {overlay_url}")

        # Download and process the background and overlay images (with SSL verification disabled)
        response_bg = requests.get(background_url, verify=False)  # SSL verification disabled
        background_image = Image.open(BytesIO(response_bg.content)).resize((1080, 1350), Image.LANCZOS)

        response_overlay = requests.get(overlay_url, verify=False)  # SSL verification disabled
        overlay_image = Image.open(BytesIO(response_overlay.content)).resize((1080, 1350), Image.LANCZOS)

        # Paste the overlay onto the background, handle transparency
        if overlay_image.mode == 'RGBA':
            background_image.paste(overlay_image, (0, 0), overlay_image)
        else:
            background_image.paste(overlay_image, (0, 0))

        # Initialize the drawing context
        draw_3 = ImageDraw.Draw(background_image)

        # Draw the overlay text (no highlight)
        draw_text(draw_3, overlay_text, font_title, (50, 750), 980, (255, 255, 255))

        # Save the image to memory
        output_3 = BytesIO()
        background_image.save(output_3, format='PNG', quality=100, optimize=True)
        output_3.seek(0)

        # Return image 3
        return send_file(output_3, mimetype='image/png')

    except Exception as e:
        logging.error(f"Error processing image 3: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
