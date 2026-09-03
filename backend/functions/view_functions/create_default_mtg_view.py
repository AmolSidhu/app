import json
import uuid

from mtg.models import MagicViewFields

def create_default_mtg_view(user):
    with open('json/views_default_options.json', 'r') as f:
        raw = json.load(f)

    default_options = raw["magic_cards"]

    fields = []
    user_name = []

    for key, option in default_options.items():
        fields.append(option["field_name"])
        user_name.append(option["user_view"])
    
        
    create_new_view_record = MagicViewFields(
        serial=str(uuid.uuid4()),
        user=user,
        active_fields=fields,
        active_fields_names=user_name
    )
    
    create_new_view_record.save() 