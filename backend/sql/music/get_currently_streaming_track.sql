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