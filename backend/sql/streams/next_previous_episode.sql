WITH ordered_videos AS (
    SELECT 
        vr.master_record_id,
        vr.video_serial,
        vr.season,
        vr.episode,
        LEAD(vr.video_serial) OVER (PARTITION BY vr.master_record_id ORDER BY vr.season, vr.episode) AS next_video_serial,
        LEAD(vr.season) OVER (PARTITION BY vr.master_record_id ORDER BY vr.season, vr.episode) AS next_season,
        LEAD(vr.episode) OVER (PARTITION BY vr.master_record_id ORDER BY vr.season, vr.episode) AS next_episode,
        LAG(vr.video_serial) OVER (PARTITION BY vr.master_record_id ORDER BY vr.season, vr.episode) AS prev_video_serial,
        LAG(vr.season) OVER (PARTITION BY vr.master_record_id ORDER BY vr.season, vr.episode) AS prev_season,
        LAG(vr.episode) OVER (PARTITION BY vr.master_record_id ORDER BY vr.season, vr.episode) AS prev_episode
    FROM video_record vr
    WHERE vr.master_record_id = (
        SELECT master_record_id FROM video_record WHERE video_serial = %s
    )
)
SELECT 
    ov.master_record_id,
    ov.video_serial,
    ov.season,
    ov.episode,
    ov.prev_video_serial AS previous_video_serial,
    ov.prev_season AS previous_season,
    ov.prev_episode AS previous_episode,
    ov.next_video_serial AS next_video_serial,
    ov.next_season AS next_season,
    ov.next_episode AS next_episode,
    v.title,
    v.description,
    v.series
FROM ordered_videos ov
JOIN video v ON ov.master_record_id = v.serial
WHERE ov.video_serial = %s;