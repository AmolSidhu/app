SELECT
    v.title,
    v.serial,
    v.imdb_rating,
    v.description
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
    video_favourites vf ON vf.video_id = v.serial and vf.user_id = %s
WHERE
    v.current_status = 'P'
AND
    v.private = FALSE
GROUP BY
    v.serial, v.title, v.imdb_rating, v.description
ORDER BY
    v.imdb_rating DESC
LIMIT %s
OFFSET %s;