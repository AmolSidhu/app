def get_custom_playlist_music_records_query():
    return """
SELECT
    ar.serial AS artist_serial,
    ar.artist_name,
    tr.serial AS track_serial,
    tr.track_number,
    tr.track_name,
    tr.track_duration
FROM
    custom_music_playlist p
INNER JOIN 
    credentials u
        ON p.user_id = u.username
INNER JOIN
    custom_music_playlist_record pr
        ON p.serial = pr.playlist_id
INNER JOIN
    music_track_record tr
        ON pr.track_id = tr.serial
INNER JOIN
    artist_record ar
        ON tr.artist_record_id = ar.serial
WHERE
    p.serial = %s
AND
    u.username = %s
ORDER BY
    tr.track_number ASC;
"""

def get_currently_playing_track_query():
    return """
SELECT
    pr.serial AS playlist_record_serial,
    pr.play_order,
    tr.serial AS track_serial,
    tr.track_name,
    tr.track_duration,
    tr.track_location,
    ar.artist_name,
    al.album_name
FROM
    custom_music_playlist_record pr
INNER JOIN
    music_track_record tr
        ON pr.track_id = tr.serial
INNER JOIN
    artist_record ar
        ON tr.artist_record_id = ar.serial
INNER JOIN
    music_album_record al
        ON tr.album_record_id = al.serial
WHERE
    pr.playlist_id = %s
AND
    pr.current_track = TRUE;
"""

def get_listed_track_thumbnail_query():
    return """
SELECT
    al.serial AS album_serial,
    al.list_view_thumbnail_location
FROM
    custom_music_playlist_record pr
INNER JOIN
    music_track_record tr
        ON pr.track_id = tr.serial
INNER JOIN
    music_album_record al
        ON tr.album_record_id = al.serial
WHERE
    pr.playlist_id = %s
AND
    pr.track_id = %s
LIMIT 1;
"""

def get_active_player_track_thumbnail_query():
    return """
SELECT
    al.serial AS album_serial,
    al.active_player_thumbnail_location
FROM
    custom_music_playlist_record pr
INNER JOIN
    music_track_record tr
        ON pr.track_id = tr.serial
INNER JOIN
    music_album_record al
        ON tr.album_record_id = al.serial
WHERE
    pr.playlist_id = %s
AND
    pr.serial = %s
LIMIT 1;
"""

def get_currently_streaming_track_query():
    return """
SELECT
    tr.serial AS track_serial,
    CASE
        WHEN tr.full_track_added = TRUE
             AND tr.full_track_location IS NOT NULL
             AND tr.full_track_location <> ''
        THEN tr.full_track_location
        ELSE tr.track_location
    END AS resolved_file_path,

    pr.serial AS custom_track_serial,
    pr.playlist_id,
    mph.track_stop_time
FROM
    custom_music_playlist_record pr
INNER JOIN
    music_track_record tr
        ON pr.track_id = tr.serial
LEFT JOIN
    music_player_history mph
        ON mph.track_record_id = tr.serial
WHERE
    tr.serial = %s
AND
    pr.serial = %s
ORDER BY
    mph.last_played_date DESC
LIMIT 1;
"""
