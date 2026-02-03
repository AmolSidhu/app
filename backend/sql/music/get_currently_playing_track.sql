SELECT
    pr.serial AS playlist_record_serial,
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