from quart import Quart, render_template, request
from werkzeug.utils import secure_filename
from rembg import remove
from PIL import Image

app = Quart(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
async def root():
    return await render_template("index.html")

@app.route('/send', methods=['POST'])
async def remove_background():
    if 'file' not in (await request.files):
        return await render_template("index.html", error="No file part")

    uploaded_file = (await request.files)['file']

    if uploaded_file.filename == '':
        return await render_template("index.html", error="No selected file")

    if uploaded_file and allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        input_path = app.config['UPLOAD_FOLDER'] + '/' + filename
        output_path = app.config['UPLOAD_FOLDER'] + '/final_' + filename

        await uploaded_file.save(input_path)

        try:
            # Open the image
            input_image = Image.open(input_path)

            # Remove the background
            output_image = remove(input_image)

            # Convert RGBA to RGB
            rgb_output_image = output_image.convert("RGB")

            # Save the result as JPEG
            rgb_output_image.save(output_path)

            return await render_template("index.html", inputIm=filename, outputIm='final_' + filename)
        except Exception as e:
            return await render_template("index.html", error=f"Error processing the image: {str(e)}")

    else:
        return await render_template("index.html", error="Invalid file format. Allowed formats: png, jpg, jpeg")

if __name__ == '__main__':
    app.run(debug=True)
