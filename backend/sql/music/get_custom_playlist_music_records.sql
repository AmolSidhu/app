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