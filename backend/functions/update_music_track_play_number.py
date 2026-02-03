from music.models import CustomMusicPlaylist, CustomMusicPlaylistRecord

import random

def update_music_track_play_number(user, playlist, shuffle_play, order_play):
    playlist_record = CustomMusicPlaylistRecord.objects.filter(serial=playlist,
                                                               user=user).first()
    if not playlist_record:
        return False
    playlist_records = CustomMusicPlaylistRecord.objects.filter(
        playlist=playlist_record.playlist).all()
    if shuffle_play:
        records_list = list(playlist_records)
        random.shuffle(records_list)
        for idx, record in enumerate(records_list):
            record.play_order = idx + 1
            record.current_track = (idx == 0)
            record.save()
    if order_play and not shuffle_play:
        for idx, record in enumerate(playlist_records):
            record.play_order = idx + 1
            record.current_track = (idx == 0)
            record.save()
    return True   

def generate_music_track_play_number(user, playlist,
                                     shuffle_play, order_play,
                                     if_current_track=False,
                                     current_track_serial=''):
    if if_current_track:
        current_track_record = CustomMusicPlaylistRecord.objects.filter(
            serial=current_track_serial, playlist=playlist).first()
        if not current_track_record:
            return False
        playlist_records = CustomMusicPlaylistRecord.objects.filter(
            playlist=playlist).exclude(serial=current_track_serial).all(
                ).order_by('added_date')
        current_track_record.play_order = 1
        current_track_record.current_track = True
        current_track_record.save()
        if shuffle_play:
            records_list = list(playlist_records)
            random.shuffle(records_list)
            for idx, record in enumerate(records_list):
                record.play_order = idx + 2
                record.current_track = False
                record.save()
        if order_play and not shuffle_play:
            for idx, record in enumerate(playlist_records):
                record.play_order = idx + 2
                record.current_track = False
                record.save()
    else:
        playlist_records = CustomMusicPlaylistRecord.objects.filter(
            playlist=playlist).all()
        if shuffle_play:
            records_list = list(playlist_records)
            random.shuffle(records_list)
            for idx, record in enumerate(records_list):
                record.play_order = idx + 1
                record.current_track = (idx == 0)
                record.save()
        if order_play and not shuffle_play:
            for idx, record in enumerate(playlist_records):
                record.play_order = idx + 1
                record.current_track = (idx == 0)
                record.save()
    return True