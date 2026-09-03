import json
import os
import requests
from time import sleep
            
def download_card_image(json_file, output_dir):
    with open(json_file, "r") as f:
        cards = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    for card in cards:
        card_id = card.get("id")

        if "image_uris" in card:
            png_url = card["image_uris"].get("png")
            if png_url:
                try:
                    clean_url = png_url.split("?")[0]
                    ext = os.path.splitext(clean_url)[1]
                    filename = f"{card_id}{ext}"
                    filepath = os.path.join(output_dir, filename)

                    response = requests.get(png_url)
                    response.raise_for_status()

                    with open(filepath, "wb") as img:
                        img.write(response.content)

                    print(f"Downloaded: {filename}")

                except Exception as e:
                    print(f"Failed to download {png_url}: {e}")

        if "card_faces" in card:
            for idx, face in enumerate(card["card_faces"]):
                if "image_uris" in face:
                    png_url = face["image_uris"].get("png")
                    if png_url:
                        try:
                            clean_url = png_url.split("?")[0]
                            ext = os.path.splitext(clean_url)[1]
                            filename = f"{card_id}_face{idx}{ext}"
                            filepath = os.path.join(output_dir, filename)

                            response = requests.get(png_url)
                            response.raise_for_status()

                            with open(filepath, "wb") as img:
                                img.write(response.content)

                            print(f"Downloaded: {filename}")

                        except Exception as e:
                            print(f"Failed to download {png_url}: {e}")

def magic_image_downloader(image_url, image_url_back, output_path, serial):
    images_created = []

    try:
        if image_url:
            clean = image_url.split("?")[0]
            ext = os.path.splitext(clean)[1]
            file_path = os.path.join(output_path, f"{serial}{ext}")

            response = requests.get(image_url)
            if response.status_code == 200:
                with open(file_path, "wb") as img:
                    img.write(response.content)
                images_created.append(serial)
        else:
            print(f"No front image for {serial}")

        if image_url_back:
            sleep(1)
            clean_back = image_url_back.split("?")[0]
            ext_back = os.path.splitext(clean_back)[1]
            file_path_back = os.path.join(output_path, f"{serial}_1{ext_back}")

            response_back = requests.get(image_url_back)
            if response_back.status_code == 200:
                with open(file_path_back, "wb") as img_back:
                    img_back.write(response_back.content)
                images_created.append(f"{serial}_1")

        return images_created

    except Exception as e:
        print(f"Failed to download image for {serial}: {e}")
        return images_created
