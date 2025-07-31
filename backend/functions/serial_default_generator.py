import logging
import json
import re
from django.db.models import Max

logger = logging.getLogger(__name__)

def serial_default_generator(default_codes, current_code):
    code = current_code.split('-')[1]
    code_length = len(code)
    for default_code in default_codes:
        if len(default_code) == code_length:
            return int(default_code)
    return 1


def generate_serial_code(config_section, serial_key, model, field_name):
    try:
        with open('json/serial_codes.json', 'r') as file:
            config = json.load(file)

        if config_section not in config or serial_key not in config[config_section]:
            raise ValueError(f"Missing serial config: {config_section} --- {serial_key}")

        serial_format = config[config_section][serial_key]
        prefix, sample_number = serial_format.split('-')
        num_len = len(sample_number)

        existing_serials = model.objects.filter(
            **{f"{field_name}__startswith": prefix}
        ).values_list(field_name, flat=True)

        matching_serials = [
            serial for serial in existing_serials
            if re.fullmatch(rf"{prefix}-(\d{{{num_len}}})", serial)
        ]

        if matching_serials:
            latest_serial = max(matching_serials)
            match = re.search(rf"{prefix}-(\d+)", latest_serial)
            new_num = int(match.group(1)) + 1 if match else 1
        else:
            new_num = 1

        new_serial = f"{prefix}-{str(new_num).zfill(num_len)}"
        return new_serial

    except Exception as e:
        logger.error(f"Serial generation error for {config_section}.{serial_key}: {e}")
        return None