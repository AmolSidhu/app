SELECT 
    v.title,
    STRING_AGG(DISTINCT vd.director, ', ') AS directors,
    STRING_AGG(DISTINCT vs.star, ', ') AS stars,
    STRING_AGG(DISTINCT vw.writer, ', ') AS writers,
    STRING_AGG(DISTINCT vc.creator, ', ') AS creators,
    v.serial,
    u.username AS uploader_username,
    v.imdb_rating,
    v.description
FROM
    video v
LEFT JOIN
    video_directors vd ON v.serial = vd.video_id
LEFT JOIN
    video_stars vs ON v.serial = vs.video_id
LEFT JOIN
    video_writers vw ON v.serial = vw.video_id
LEFT JOIN
    video_creators vc ON v.serial = vc.video_id
INNER JOIN
    credentials u ON v.uploaded_by_id = u.username
WHERE
    v.current_status = 'P'
AND
    v.private = FALSE
AND
    (
        COALESCE(v.main_tag, '') = ANY(%s)
        OR vd.director = ANY(%s)
        OR vs.star = ANY(%s)
        OR vw.writer = ANY(%s)
        OR vc.creator = ANY(%s)
    )
GROUP BY
    v.serial, v.title, u.username, v.imdb_rating, v.description
ORDER BY 
    v.imdb_rating DESC;