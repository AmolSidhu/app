from PIL import Image
import piexif

def extract_exif_data(image):
    try:
        picture = Image.open(image)

        if "exif" not in picture.info:
            return "No Exif data found."

        data = piexif.load(picture.info["exif"])

        full_data = {}
        for exif in data:
            if isinstance(data[exif], dict):
                for tag, value in data[exif].items():
                    tag_name = piexif.TAGS[exif].get(tag, {"name": tag})["name"]
                    
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except UnicodeDecodeError:
                            value = value.hex()
                            
                    full_data[tag_name] = value

        return full_data
    except Exception as e:
        return f"Error: {e}"
