
def get_video_list_query():
    return """
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
    CASE
        WHEN v.total_ratings = 0 THEN 0
        ELSE v.total_rating_score / v.total_ratings
    END AS rating_with_tiebreaker,
    CASE
        WHEN v.uploaded_by_id = %s THEN 1
        ELSE 0
    END AS user_match
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
    v.current_status = 'P'
AND
    v.private = FALSE
AND
    u.permission <= %s
GROUP BY
    v.serial, v.title, u.username, v.imdb_rating, v.description, v.total_ratings, v.total_rating_score, v.uploaded_by_id
ORDER BY 
    rating_with_tiebreaker DESC, v.total_ratings DESC
LIMIT %s
OFFSET %s;
"""

def get_video_by_genre_query():
    return """
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
    CASE
        WHEN v.total_ratings = 0 THEN 0
        ELSE v.total_rating_score / v.total_ratings
    END AS rating_with_tiebreaker,
    CASE
        WHEN v.uploaded_by_id = %s THEN 1
        ELSE 0
    END AS user_match
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
    v.current_status = 'P'
AND 
    v.private = FALSE
AND 
    u.permission <= %s
AND 
    EXISTS (
        SELECT 1 
        FROM video_tags sub_vt 
        WHERE sub_vt.video_id = v.serial 
        AND sub_vt.tag = %s
    )
GROUP BY 
    v.serial, v.title, u.username, v.imdb_rating, v.description, v.total_ratings, v.total_rating_score, v.uploaded_by_id
ORDER BY 
    rating_with_tiebreaker DESC, v.total_ratings DESC
LIMIT %s OFFSET %s;
"""

def get_recently_viewed_query():
    return """
WITH latest_history AS (
    SELECT DISTINCT ON (vh.master_record_id)
        vh.master_record_id,
        vh.video_stop_time,
        vh.serial_id,
        vh.last_updated AS timestamp
    FROM main.video_history vh
    WHERE vh.user_id = %s
    ORDER BY vh.master_record_id, vh.last_updated DESC
)
SELECT 
    v.title, 
    STRING_AGG(DISTINCT vt.tag, ', ') AS tags,
    STRING_AGG(DISTINCT vd.director, ', ') AS directors,
    STRING_AGG(DISTINCT vs.star, ', ') AS stars,
    STRING_AGG(DISTINCT vw.writer, ', ') AS writers,
    STRING_AGG(DISTINCT vc.creator, ', ') AS creators,
    v.serial,
    lh.timestamp,
    u.username AS uploader_username,
    v.imdb_rating,
    v.description,
    CASE
        WHEN v.uploaded_by_id = %s THEN 1
        ELSE 0
    END AS user_match
FROM 
    latest_history lh
JOIN 
    main.video v ON v.serial = lh.master_record_id
LEFT JOIN 
    main.video_tags vt ON vt.video_id = v.serial
LEFT JOIN 
    main.video_directors vd ON vd.video_id = v.serial
LEFT JOIN 
    main.video_stars vs ON vs.video_id = v.serial
LEFT JOIN 
    main.video_writers vw ON vw.video_id = v.serial
LEFT JOIN 
    main.video_creators vc ON vc.video_id = v.serial
JOIN 
    main.credentials u ON v.uploaded_by_id = u.username
WHERE 
    v.current_status = 'P'
AND 
    v.private = FALSE
AND 
    u.permission <= %s
GROUP BY 
    v.serial, v.title, u.username, v.imdb_rating, v.description, lh.timestamp, v.uploaded_by_id
ORDER BY 
    lh.timestamp DESC
LIMIT %s OFFSET %s;
"""

def get_video_search_query():
    return """
SELECT DISTINCT ON (v.serial) 
    v.title,
    v.tags,
    v.directors,
    v.stars,
    v.writers,
    v.creators,
    v.serial,
    u.username as uploader_username,
    v.imdb_rating,
    v.description,
    CASE
        WHEN v.total_ratings = 0 THEN 0
        ELSE v.total_rating_score / v.total_ratings
    END AS rating_with_tiebreaker,
    CASE
        WHEN v.uploaded_by_id = %s THEN 1
        ELSE 0
    END AS user_match
FROM video v
INNER JOIN credentials u ON v.uploaded_by_id = u.id
WHERE 
    (v.title ILIKE %s OR v.tags::text ILIKE %s)
    AND v.current_status = 'P'
    AND v.private = FALSE
    AND u.permission <= %s
ORDER BY v.serial, v.title;
"""

def get_record_data():
    return """
    SELECT 
        v.title AS video_name,
        STRING_AGG(DISTINCT vd.director, ', ') AS video_directors,
        STRING_AGG(DISTINCT vs.star, ', ') AS video_stars,
        STRING_AGG(DISTINCT vw.writer, ', ') AS video_writers,
        STRING_AGG(DISTINCT vc.creator, ', ') AS video_creators,
        STRING_AGG(DISTINCT vt.tag, ', ') AS video_genres,
        v.description AS video_description,
        v.imdb_rating AS video_rating,
        CASE 
            WHEN vh.serial_id IS NOT NULL THEN TRUE
            ELSE FALSE
        END AS resume,
        vh.serial_id AS resume_serial,
        vr.video_serial AS video_serial,
        v.series,
        v.season_metadata,
        vr.video_serial AS serial
    FROM 
        video_record vr
    LEFT JOIN 
        video v ON v.serial = vr.master_record_id
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
    LEFT JOIN 
        video_history vh ON vh.master_record_id = v.serial AND vh.user_id = %s
    LEFT JOIN 
        (
            SELECT 
                vh1.master_record_id,
                vh1.serial_id AS video_serial,
                vh1.master_record_id AS record_serial
            FROM 
                video_history vh1
            WHERE 
                vh1.user_id = %s
            ORDER BY 
                vh1.last_updated DESC
        ) vr_history ON vr_history.record_serial = vr.master_record_id
    WHERE 
        v.serial = %s
    GROUP BY 
        vr.video_serial, vh.serial_id, vh.master_record_id, v.title, 
        v.description, v.imdb_rating, v.series, v.season_metadata, vr_history.video_serial;
    """

def video_search_query():
    return """
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
    """