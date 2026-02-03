SELECT 
    v.title,
    STRING_AGG(DISTINCT vt.tag, ', ') AS tags,
    STRING_AGG(DISTINCT vd.director, ', ') AS directors,
    STRING_AGG(DISTINCT vs.star, ', ') AS stars,
    STRING_AGG(DISTINCT vw.writer, ', ') AS writers,
    STRING_AGG(DISTINCT vc.creator, ', ') AS creators,
    v.serial,
    u.username AS uploader_username,
    v.imdb_rating,
    v.description,
    v.series,
    v.season_metadata
FROM
    video v
LEFT JOIN
    video_tags vt ON vt.video_id = v.serial
LEFT JOIN
    video_directors vd ON vd.video_id = v.serial
LEFT JOIN
    video_stars vs ON vs.video_id = v.serial
LEFT JOIN
    video_writers vw ON vw.video_id = v.serial
LEFT JOIN
    video_creators vc ON vc.video_id = v.serial
INNER JOIN
    credentials u ON v.uploaded_by_id = u.username
WHERE
    v.serial = %s
AND
    v.uploaded_by_id = %s
GROUP BY 
    v.serial, v.title, v.imdb_rating, v.description, v.series, v.season_metadata, u.username;