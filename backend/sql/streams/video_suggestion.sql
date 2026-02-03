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
    WHERE v.serial != (SELECT video_id FROM target_video)
    GROUP BY v.serial, v.title, v.imdb_rating, v.main_tag, v.description
)
SELECT * FROM similar_videos
ORDER BY (tag_matches + creator_matches + director_matches + star_matches + writer_matches) DESC
Limit 5;