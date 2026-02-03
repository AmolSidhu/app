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
    oracle_id = models.CharField(max_length=100, null=False)
    multiverse_ids = models.JSONField(max_length=300, null=True, blank=True)
    mtgo_id = models.FloatField(max_length=100, null=True, blank=True)
    arena_id = models.FloatField(max_length=100, null=True, blank=True)
    tcgplayer_id = models.FloatField(null=True, blank=True)
    cardmarket_id = models.FloatField(max_length=100, null=True, blank=True)
    card_name = models.CharField(max_length=200, null=False)
    lang = models.CharField(max_length=20, null=False)
    released_at = models.DateField(null=True, blank=True)
    card_uri = models.CharField(max_length=300, null=True, blank=True)
    scryfall_uri = models.CharField(max_length=300, null=True, blank=True)
    layout = models.CharField(max_length=50, null=False)
    highres_image = models.BooleanField(null=False, default=False)
    image_status = models.CharField(max_length=50, null=False)
    image_uris = models.JSONField
    mana_cost = models.CharField(max_length=100, null=True, blank=True)
    cmc = models.FloatField(null=False, default=0.0)
    type_line = models.CharField(max_length=200, null=False)
    oracle_text = models.TextField(null=True, blank=True)
    colour = models.CharField(max_length=50, null=True, blank=True)
    colour_identity = models.CharField(max_length=50, null=False)
    keywords = models.JSONField()
    legalities = models.JSONField()
    games = models.JSONField()
    produced_mana = models.CharField(max_length=100, null=True, blank=True)
    reserved = models.BooleanField(null=False, default=False)
    game_changer = models.BooleanField(null=False, default=False)
    foil = models.BooleanField(null=False, default=False)
    non_foil = models.BooleanField(null=False, default=False)
    finishes = models.JSONField()
    oversized = models.BooleanField(null=False, default=False)
    promo = models.BooleanField(null=False, default=False)
    reprint = models.BooleanField(null=False, default=False)
    variation = models.BooleanField(null=False, default=False)
    set_id = models.CharField(max_length=100, null=False)
    set_code = models.CharField(max_length=20, null=False)
    set_name = models.CharField(max_length=100, null=False)
    set_type = models.CharField(max_length=50, null=False)
    set_uri = models.CharField(max_length=300, null=True, blank=True)
    set_search_uri = models.CharField(max_length=300, null=True, blank=True)
    scryfall_set_uri = models.CharField(max_length=300, null=True, blank=True)
    rulings_uri = models.CharField(max_length=300, null=True, blank=True)
    prints_search_uri = models.CharField(max_length=300, null=True, blank=True)
    collector_number = models.CharField(max_length=50, null=False)
    digital = models.BooleanField(null=False, default=False)
    rarity = models.CharField(max_length=50, null=False)
    card_back_id = models.CharField(max_length=100, null=True, blank=True)
    artist = models.CharField(max_length=100, null=True, blank=True)
    artist_ids = models.JSONField()
    illustration_id = models.CharField(max_length=100, null=True, blank=True)
    border_color = models.CharField(max_length=50, null=False)
    frame = models.CharField(max_length=50, null=False)
    full_art = models.BooleanField(null=False, default=False)
    textless = models.BooleanField(null=False, default=False)
    booster = models.BooleanField(null=False, default=False)
    story_spotlight = models.BooleanField(null=False, default=False)
    prices = models.JSONField()
    related_uris = models.JSONField()
    purchase_uris = models.JSONField()
    mtgo_foil_id = models.CharField(max_length=100, null=True, blank=True)
    power = models.CharField(max_length=10, null=True, blank=True)
    toughness = models.CharField(max_length=10, null=True, blank=True)
    flavour_text = models.TextField(null=True, blank=True)
    edhrec_rank = models.IntegerField(null=True, blank=True)
    penny_rank = models.IntegerField(null=True, blank=True)
    printed_name = models.CharField(max_length=200, null=True, blank=True)
    printed_type_line = models.CharField(max_length=200, null=True, blank=True)
    printed_text = models.TextField(null=True, blank=True)
    security_stamp = models.CharField(max_length=50, null=True, blank=True)
    all_parts = models.JSONField()
    promo_types = models.JSONField()
    loyalty = models.IntegerField(null=True, blank=True)
    watermark = models.CharField(max_length=50, null=True, blank=True)
    frame_effects = models.JSONField()
    card_faces = models.JSONField()
    preview = models.JSONField()
    resource_id = models.CharField(max_length=100, null=True, blank=True)
    colour_indicator = models.JSONField()
    tcgplayer_etched_id = models.CharField(max_length=100, null=True, blank=True)
    content_warning = models.TextField(null=True, blank=True)
    flavour_name = models.CharField(max_length=200, null=True, blank=True)
    attraction_lights = models.JSONField()
    variation_of = models.CharField(max_length=100, null=True, blank=True)
    life_modifier = models.FloatField(null=True, blank=True)
    hand_modifier = models.CharField(max_length=10, null=True, blank=True)
    defense = models.FloatField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'magic_cards'
        verbose_name = 'Magic Card'
        verbose_name_plural = 'Magic Cards'
