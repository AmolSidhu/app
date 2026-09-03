from django.db import models

class ScraperUploadFile(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100, null=False)
    scraper_name = models.CharField(max_length=100, null=False)
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    scraper_description = models.CharField(max_length=300, null=True, blank=True)
    file_location = models.CharField(max_length=300, null=False, default='')
    status = models.CharField(max_length=50, null=False, default='validating')
    file_type = models.CharField(max_length=50, null=False, default='missing file type')
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'scraper_upload_file'
        verbose_name = 'Scraper Upload File'
        verbose_name_plural = 'Scraper Upload Files'
        
class ScraperOutputFile(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100, null=False)
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    scraper_file = models.ForeignKey('ScraperUploadFile', on_delete=models.CASCADE, related_name='scraper_output_file', null=False)
    run_number = models.IntegerField(null=False, default=1)
    status = models.CharField(max_length=50, null=False, default='processing')
    file_location = models.CharField(max_length=300, null=False, default='')
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'scraper_output_file'
        verbose_name = 'Scraper Output File'
        verbose_name_plural = 'Scraper Output Files'
        
class MagicSets(models.Model):
    set_name = models.CharField(max_length=100, null=False)
    set_code = models.CharField(max_length=20, primary_key=True, unique=True, null=False)
    release_date = models.DateField(null=True, blank=True)
    set_short_name = models.CharField(max_length=50, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)
    set_uri = models.CharField(max_length=300, null=True, blank=True)
    set_search_uri = models.CharField(max_length=300, null=True, blank=True)
    scryfall_set_uri = models.CharField(max_length=300, null=True, blank=True)
    
    class Meta:
        db_table = 'magic_sets'
        verbose_name = 'Magic Set'
        verbose_name_plural = 'Magic Sets'
        
class MagicCards(models.Model):
    card_object = models.CharField(max_length=20, null=False)
    card_id = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    oracle_id = models.CharField(max_length=100, null=True)
    multiverse_ids = models.JSONField(null=True, blank=True)
    mtgo_id = models.IntegerField(null=True, blank=True)
    arena_id = models.IntegerField(null=True, blank=True)
    tcgplayer_id = models.IntegerField(null=True, blank=True)
    cardmarket_id = models.IntegerField(null=True, blank=True)
    card_name = models.CharField(max_length=200, null=False)
    language = models.CharField(max_length=20, null=True, blank=True)
    released_at = models.DateField(null=True, blank=True)
    card_uri = models.CharField(max_length=350, null=True, blank=True)
    scryfall_uri = models.CharField(max_length=350, null=True, blank=True)
    layout = models.CharField(max_length=50, null=True, blank=True)
    highres_image = models.BooleanField(default=False)
    image_status = models.CharField(max_length=50, null=True, blank=True)
    image_uris = models.JSONField(null=True, blank=True)
    mana_cost = models.CharField(max_length=100, null=True, blank=True)
    cmc = models.FloatField(default=0.0)
    type_line = models.CharField(max_length=200, null=True, blank=True)
    oracle_text = models.TextField(null=True, blank=True)
    colors = models.JSONField(null=True, blank=True)
    color_identity = models.JSONField(null=True, blank=True)
    keywords = models.JSONField(null=True, blank=True)
    legalities = models.JSONField(null=True, blank=True)
    games = models.JSONField(null=True, blank=True)
    produced_mana = models.JSONField(null=True, blank=True)
    reserved = models.BooleanField(default=False)
    game_changer = models.BooleanField(default=False)
    foil = models.BooleanField(default=False)
    non_foil = models.BooleanField(default=False)
    finishes = models.JSONField(null=True, blank=True)
    oversized = models.BooleanField(default=False)
    promo = models.BooleanField(default=False)
    reprint = models.BooleanField(default=False)
    variation = models.BooleanField(default=False)
    set_id = models.CharField(max_length=100, null=True, blank=True)
    set_code = models.CharField(max_length=20, null=True, blank=True)
    set_name = models.CharField(max_length=100, null=True, blank=True)
    set_type = models.CharField(max_length=50, null=True, blank=True)
    set_uri = models.CharField(max_length=350, null=True, blank=True)
    set_search_uri = models.CharField(max_length=350, null=True, blank=True)
    scryfall_set_uri = models.CharField(max_length=350, null=True, blank=True)
    rulings_uri = models.CharField(max_length=350, null=True, blank=True)
    prints_search_uri = models.CharField(max_length=350, null=True, blank=True)
    collector_number = models.CharField(max_length=50, null=True, blank=True)
    digital = models.BooleanField(default=False)
    rarity = models.CharField(max_length=50, null=True, blank=True)
    card_back_id = models.CharField(max_length=100, null=True, blank=True)
    artist = models.CharField(max_length=100, null=True, blank=True)
    artist_ids = models.JSONField(null=True, blank=True)
    illustration_id = models.CharField(max_length=100, null=True, blank=True)
    border_color = models.CharField(max_length=50, null=True, blank=True)
    frame = models.CharField(max_length=50, null=True, blank=True)
    full_art = models.BooleanField(default=False)
    textless = models.BooleanField(default=False)
    booster = models.BooleanField(default=False)
    story_spotlight = models.BooleanField(default=False)
    prices = models.JSONField(null=True, blank=True)
    related_uris = models.JSONField(null=True, blank=True)
    purchase_uris = models.JSONField(null=True, blank=True)
    mtgo_foil_id = models.IntegerField(null=True, blank=True)
    power = models.CharField(max_length=10, null=True, blank=True)
    toughness = models.CharField(max_length=10, null=True, blank=True)
    flavor_text = models.TextField(null=True, blank=True)
    edhrec_rank = models.IntegerField(null=True, blank=True)
    penny_rank = models.IntegerField(null=True, blank=True)
    printed_name = models.CharField(max_length=200, null=True, blank=True)
    printed_type_line = models.CharField(max_length=200, null=True, blank=True)
    printed_text = models.TextField(null=True, blank=True)
    security_stamp = models.CharField(max_length=50, null=True, blank=True)
    all_parts = models.JSONField(null=True, blank=True)
    promo_types = models.JSONField(null=True, blank=True)
    loyalty = models.CharField(max_length=10, null=True, blank=True)
    watermark = models.CharField(max_length=50, null=True, blank=True)
    frame_effects = models.JSONField(null=True, blank=True)
    card_faces = models.JSONField(null=True, blank=True)
    preview = models.JSONField(null=True, blank=True)
    resource_id = models.CharField(max_length=100, null=True, blank=True)
    color_indicator = models.JSONField(null=True, blank=True)
    tcgplayer_etched_id = models.CharField(max_length=100, null=True, blank=True)
    content_warning = models.TextField(null=True, blank=True)
    flavor_name = models.CharField(max_length=200, null=True, blank=True)
    attraction_lights = models.JSONField(null=True, blank=True)
    variation_of = models.CharField(max_length=100, null=True, blank=True)
    life_modifier = models.FloatField(null=True, blank=True)
    hand_modifier = models.CharField(max_length=10, null=True, blank=True)
    defense = models.FloatField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    image_dir = models.CharField(max_length=350, null=True, blank=True)
    image_added = models.BooleanField(default=False)
    back_exists = models.BooleanField(default=False)
    back_serial = models.CharField(max_length=100, null=True, blank=True)
    card_json = models.JSONField(null=True, blank=True)
    json_dir = models.CharField(max_length=350, null=True, blank=True)

    class Meta:
        db_table = 'magic_cards'
        verbose_name = 'Magic Card'
        verbose_name_plural = 'Magic Cards'

class MagicTempFiles(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    file_name = models.CharField(max_length=100, null=False)
    file_location = models.CharField(max_length=300, null=False, default='')
    file_status = models.CharField(max_length=50, null=False, default='pending')
    file_extension = models.CharField(max_length=20, null=True, blank=True)
    run_number = models.IntegerField(null=False, default=1)
    failed_status = models.CharField(max_length=50, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'magic_temp_files'
        verbose_name = 'Magic Temp File'
        verbose_name_plural = 'Magic Temp Files'
        
class CompletedTempFilesLog(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    file_name = models.CharField(max_length=100, null=False)
    file_location = models.CharField(max_length=300, null=False, default='')
    file_extension = models.CharField(max_length=20, null=True, blank=True)
    process_status = models.CharField(max_length=50, null=False)
    file_deleted = models.BooleanField(default=False)
    run_number = models.IntegerField(null=False, default=1)
    create_date = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = 'completed_temp_files_log'
        verbose_name = 'Completed Temp File Log'
        verbose_name_plural = 'Completed Temp File Logs'
        
class MagicViewFields(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    active_fields = models.JSONField(null=True, blank=True)
    active_fields_names = models.JSONField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'magic_view_fields'
        verbose_name = 'Magic View Field'
        verbose_name_plural = 'Magic View Fields'
        
class MagicCardsView(models.Model):
    card_id = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    oracle_id = models.CharField(max_length=100, null=True, blank=True)
    card_name = models.CharField(max_length=200, null=False)
    release_date = models.DateField(null=True, blank=True)
    mana_cost = models.CharField(max_length=25, null=True, blank=True)
    cmc = models.FloatField(default=0.0)
    type_line = models.TextField(null=True, blank=True)
    oracle_text = models.TextField(null=True, blank=True)
    colour_white = models.BooleanField(default=False)
    colour_blue = models.BooleanField(default=False)
    colour_black = models.BooleanField(default=False)
    colour_red = models.BooleanField(default=False)
    colour_green = models.BooleanField(default=False)
    colour_colourless = models.BooleanField(default=False)
    colour_identity_white = models.BooleanField(default=False)
    colour_identity_blue = models.BooleanField(default=False)
    colour_identity_black = models.BooleanField(default=False)
    colour_identity_red = models.BooleanField(default=False)
    colour_identity_green = models.BooleanField(default=False)
    colour_identity_colourless = models.BooleanField(default=False)
    reserved = models.BooleanField(default=False)
    keywords = models.JSONField(null=True, blank=True)
    foil = models.BooleanField(default=False)
    non_foil = models.BooleanField(default=False)
    set_name = models.CharField(max_length=60, null=True, blank=True)
    set_type = models.CharField(max_length=20, null=True, blank=True)
    collector_number = models.CharField(max_length=10, null=True, blank=True)
    rarity = models.CharField(max_length=20, null=True, blank=True)
    power = models.CharField(max_length=10, null=True, blank=True)
    toughness = models.CharField(max_length=10, null=True, blank=True)
    flavor_text = models.TextField(null=True, blank=True)
    edh_rank = models.IntegerField(null=True, blank=True)
    penny_rank = models.IntegerField(null=True, blank=True)
    promo_types = models.JSONField(null=True, blank=True)
    loyalty = models.CharField(max_length=10, null=True, blank=True)
    life_modifier = models.FloatField(null=True, blank=True)
    produced_mana = models.JSONField(null=True, blank=True)
    hand_modifier = models.CharField(max_length=10, null=True, blank=True)
    defense = models.FloatField(null=True, blank=True)
    back_exists = models.BooleanField(default=False)
    back_serial = models.CharField(max_length=100, null=True, blank=True)
    image_dir = models.CharField(max_length=350, null=True, blank=True)
    image_added = models.BooleanField(default=False)
    json_dir = models.CharField(max_length=350, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'magic_cards_view'
        verbose_name = 'Magic Card View'
        verbose_name_plural = 'Magic Card Views'

class MagicCardKeywords(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    card = models.ForeignKey(MagicCardsView, on_delete=models.CASCADE, related_name='card_keywords')
    keyword = models.CharField(max_length=100, null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'magic_card_keywords'
        verbose_name = 'Magic Card Keyword'
        verbose_name_plural = 'Magic Card Keywords'

class MagicCardLegalities(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    card = models.ForeignKey(MagicCardsView, on_delete=models.CASCADE, related_name='card_legalities')
    duel = models.BooleanField(default=False)
    brawl = models.BooleanField(default=False)
    penny = models.BooleanField(default=False)
    predh = models.BooleanField(default=False)
    future = models.BooleanField(default=False)
    legacy = models.BooleanField(default=False)
    modern = models.BooleanField(default=False)
    pauper = models.BooleanField(default=False)
    alchemy = models.BooleanField(default=False)
    pioneer = models.BooleanField(default=False)
    vintage = models.BooleanField(default=False)
    historic = models.BooleanField(default=False)
    standard = models.BooleanField(default=False)
    timeless = models.BooleanField(default=False)
    commander = models.BooleanField(default=False)
    gladiator = models.BooleanField(default=False)
    oldschool = models.BooleanField(default=False)
    premodern = models.BooleanField(default=False)
    oathbreaker = models.BooleanField(default=False)
    standardbrawl = models.BooleanField(default=False)
    paupercommander = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'magic_card_legalities'
        verbose_name = 'Magic Card Legality'
        verbose_name_plural = 'Magic Card Legalities'

class MagicCardPrices(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    card = models.ForeignKey(MagicCardsView, on_delete=models.CASCADE, related_name='card_prices')
    eur_price = models.FloatField(null=True, blank=True)
    tix_price = models.FloatField(null=True, blank=True)
    usd_price = models.FloatField(null=True, blank=True)
    eur_foil_price = models.FloatField(null=True, blank=True)
    usd_foil_price = models.FloatField(null=True, blank=True)
    usd_etched_price = models.FloatField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'magic_card_prices'
        verbose_name = 'Magic Card Price'
        verbose_name_plural = 'Magic Card Prices'
        
class MagicCardUris(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    card = models.ForeignKey(MagicCardsView, on_delete=models.CASCADE, related_name='card_uris')
    card_uri = models.CharField(max_length=350, null=True, blank=True)
    scryfall_uri = models.CharField(max_length=350, null=True, blank=True)
    set_uri = models.CharField(max_length=350, null=True, blank=True)
    set_search_uri = models.CharField(max_length=350, null=True, blank=True)
    scryfall_set_uri = models.CharField(max_length=350, null=True, blank=True)
    rulings_uri = models.CharField(max_length=350, null=True, blank=True)
    prints_search_uri = models.CharField(max_length=350, null=True, blank=True)
    related_uris = models.JSONField(null=True, blank=True)
    purchase_uris = models.JSONField(null=True, blank=True)
    image_uris = models.JSONField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'magic_card_uris'
        verbose_name = 'Magic Card URI'
        verbose_name_plural = 'Magic Card URIs'

class MagicCardMiscData (models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    card = models.ForeignKey(MagicCardsView, on_delete=models.CASCADE, related_name='card_misc_data')
    multiverse_ids = models.JSONField(null=True, blank=True)
    arena_id = models.IntegerField(null=True, blank=True)
    tcgplayer_id = models.IntegerField(null=True, blank=True)
    cardmarket_id = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=20, null=True, blank=True)
    layout = models.CharField(max_length=50, null=True, blank=True)
    highres_image = models.BooleanField(default=False)
    image_status = models.CharField(max_length=50, null=True, blank=True)
    games = models.JSONField(null=True, blank=True)
    finishes = models.JSONField(null=True, blank=True)
    oversized = models.BooleanField(default=False)
    promo = models.BooleanField(default=False)
    reprint = models.BooleanField(default=False)
    variation = models.BooleanField(default=False)
    set_code = models.CharField(max_length=20, null=True, blank=True)
    digital = models.BooleanField(default=False)
    artist = models.CharField(max_length=100, null=True, blank=True)
    artist_ids = models.JSONField(null=True, blank=True)
    illustration_id = models.CharField(max_length=100, null=True, blank=True)
    border_color = models.CharField(max_length=50, null=True, blank=True)
    frame = models.CharField(max_length=50, null=True, blank=True)
    full_art = models.BooleanField(default=False)
    textless = models.BooleanField(default=False)
    booster = models.BooleanField(default=False)
    story_spotlight = models.BooleanField(default=False)
    mtgo_foil_id = models.IntegerField(null=True, blank=True)
    printed_name = models.CharField(max_length=200, null=True, blank=True)
    printed_type_line = models.CharField(max_length=200, null=True, blank=True)
    printed_text = models.TextField(null=True, blank=True)
    security_stamp = models.CharField(max_length=50, null=True, blank=True)
    promo_types = models.JSONField(null=True, blank=True)
    watermark = models.CharField(max_length=50, null=True, blank=True)
    frame_effects = models.JSONField(null=True, blank=True)
    card_faces = models.JSONField(null=True, blank=True)
    preview = models.JSONField(null=True, blank=True)
    resource_id = models.CharField(max_length=100, null=True, blank=True)
    color_indicator = models.JSONField(null=True, blank=True)
    tcgplayer_etched_id = models.CharField(max_length=100, null=True, blank=True)
    content_warning = models.TextField(null=True, blank=True)
    flavor_name = models.CharField(max_length=200, null=True, blank=True)
    attraction_lights = models.JSONField(null=True, blank=True)
    variation_of = models.CharField(max_length=100, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'magic_card_misc_data'
        verbose_name = 'Magic Card Misc Data'  
        verbose_name_plural = 'Magic Card Misc Data'