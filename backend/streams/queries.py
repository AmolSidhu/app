def next_previous_episode_query():
    return """
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
        SELECT master_record_id FROM video_record WHERE video_serial = 'LDbrmQVfpsg'
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
"""

def video_suggestion_query():
    return """
WITH target_video AS (
    SELECT vr.master_record_id AS video_id
    FROM video_record vr
    WHERE vr.video_serial = %s
),
target_tags AS (
    SELECT vt.tag
    FROM video_tags vt
    JOIN target_video tv ON vt.video_id = tv.video_id
),
target_creators AS (
    SELECT vc.creator
    FROM video_creators vc
    JOIN target_video tv ON vc.video_id = tv.video_id
),
target_directors AS (
    SELECT vd.director
    FROM video_directors vd
    JOIN target_video tv ON vd.video_id = tv.video_id
),
target_stars AS (
    SELECT vs.star
    FROM video_stars vs
    JOIN target_video tv ON vs.video_id = tv.video_id
),
target_writers AS (
    SELECT vw.writer
    FROM video_writers vw
    JOIN target_video tv ON vw.video_id = tv.video_id
),
similar_videos AS (
    SELECT v.serial, v.title, v.imdb_rating, v.main_tag, v.description,
        COUNT(DISTINCT vt.tag) AS tag_matches,
        COUNT(DISTINCT vc.creator) AS creator_matches,
        COUNT(DISTINCT vd.director) AS director_matches,
        COUNT(DISTINCT vs.star) AS star_matches,
        COUNT(DISTINCT vw.writer) AS writer_matches
    FROM video v
    LEFT JOIN video_tags vt ON vt.video_id = v.serial AND vt.tag IN (SELECT tag FROM target_tags)
    LEFT JOIN video_creators vc ON vc.video_id = v.serial AND vc.creator IN (SELECT creator FROM target_creators)
    LEFT JOIN video_directors vd ON vd.video_id = v.serial AND vd.director IN (SELECT director FROM target_directors)
    LEFT JOIN video_stars vs ON vs.video_id = v.serial AND vs.star IN (SELECT star FROM target_stars)
    LEFT JOIN video_writers vw ON vw.video_id = v.serial AND vw.writer IN (SELECT writer FROM target_writers)
    WHERE v.serial != (SELECT video_id FROM target_video)  -- Exclude the original video
    GROUP BY v.serial, v.title, v.imdb_rating, v.main_tag, v.description
)
SELECT * FROM similar_videos
ORDER BY (tag_matches + creator_matches + director_matches + star_matches + writer_matches) DESC
Limit 5;
"""