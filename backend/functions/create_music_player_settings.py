from music.models import CustomMusicPlayerSettings
from .serial_default_generator import generate_serial_code

def create_default_music_player_settings(user):
    existing_settings = CustomMusicPlayerSettings.objects.filter(user=user).first()
    if existing_settings:
        return False

    serial = generate_serial_code(
        config_section='music',
        serial_key='custom_music_player_settings_serial_code',
        model=CustomMusicPlayerSettings,
        field_name='serial'
    )
    
    new_settings_record = CustomMusicPlayerSettings.objects.create(
        serial=serial,
        user=user,
    )
    
    new_settings_record.save()
    
    return True