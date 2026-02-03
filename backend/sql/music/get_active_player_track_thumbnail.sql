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