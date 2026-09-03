import json
import uuid
import os
from decimal import Decimal
from django.db import models
from mtg.models import MagicTempFiles


def convert(decimal_num):
    if isinstance(decimal_num, Decimal):
        return float(decimal_num)
    return decimal_num


def chunk_magic_data_file(file_path='', chunk_size=500):
    with open('json/directory.json', 'r') as directory_file:
        directory = json.load(directory_file)

    output_dir = directory['magic_temp_files_dir']
    os.makedirs(output_dir, exist_ok=True)

    previous_run_number = MagicTempFiles.objects.aggregate(
        max_run_number=models.Max('run_number')
    )['max_run_number'] or 0

    current_run_number = previous_run_number + 1

    chunk = []
    x = 1

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    item = json.loads(line)
                except Exception as e:
                    print("JSON PARSE ERROR ON LINE:", line)
                    raise e

                chunk.append(item)

                if len(chunk) >= chunk_size:
                    out_path = os.path.join(output_dir, f"chunk_{x}.json")

                    with open(out_path, "w") as out:
                        json.dump(chunk, out, default=convert)

                    MagicTempFiles.objects.create(
                        serial=str(uuid.uuid4()),
                        file_name=f"chunk_{x}",
                        file_location=output_dir,
                        file_status='pending',
                        file_extension='.json',
                        run_number=current_run_number
                    )

                    chunk = []
                    x += 1

        if chunk:
            out_path = os.path.join(output_dir, f"chunk_{x}.json")

            with open(out_path, "w") as out:
                json.dump(chunk, out, default=convert)

            MagicTempFiles.objects.create(
                serial=str(uuid.uuid4()),
                file_name=f"chunk_{x}",
                file_location=output_dir,
                file_status='pending',
                file_extension='.json',
                run_number=current_run_number
            )

        return True

    except Exception as e:
        print("Error chunking file:", e)
        return False
