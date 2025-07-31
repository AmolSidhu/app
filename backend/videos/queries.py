
def get_video_list_query():
    return """
SELECT 
    v.title,
    v.serial
FROM
    video v
INNER JOIN
    credentials u ON v.uploaded_by_id = u.username
WHERE
    v.current_status = 'P'
AND
    v.private = FALSE
AND
    u.permission <= %s
ORDER BY 
    v.total_rating_score / NULLIF(v.total_ratings, 0) DESC,
    v.total_ratings DESC
LIMIT %s
OFFSET %s;
"""

def get_video_by_genre_query():
    return """
SELECT 
    v.title, 
    v.serial,
    v.description,
    v.imdb_rating
FROM 
    video v
INNER JOIN 
    video_tags vt ON vt.video_id = v.serial
INNER JOIN 
    credentials u ON v.uploaded_by_id = u.username
WHERE 
    v.current_status = 'P'
AND 
    v.private = FALSE
AND 
    u.permission <= %s
AND 
    vt.tag = %s
ORDER BY 
    v.uploaded_date DESC
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
        v.serial,
        lh.timestamp
    FROM 
        latest_history lh
    JOIN 
        main.video v ON v.serial = lh.master_record_id
    JOIN 
        main.credentials u ON v.uploaded_by_id = u.username
    WHERE 
        v.current_status = 'P'
    AND 
        v.private = FALSE
    AND 
        u.permission <= %s
    ORDER BY 
        lh.timestamp DESC
    LIMIT %s OFFSET %s;
    """

def get_video_search_query():
    return """
SELECT DISTINCT ON (v.serial)
    v.title,
    v.serial
FROM video v
WHERE
    (v.title ILIKE %s)
    AND v.current_status = 'P'
    AND v.private = FALSE
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
        vr.video_serial AS serial,
        CASE 
            WHEN vf.video_id IS NOT NULL THEN TRUE
            ELSE FALSE
        END AS favourites,
        ARRAY_AGG(DISTINCT CASE
            WHEN cvr.video_serial_id = v.serial THEN JSON_BUILD_OBJECT(
                'list_serial', cvl.list_serial,
                'list_name', cvl.list_name
            )::text
        END) FILTER (WHERE cvr.video_serial_id = v.serial) AS in_custom_album,
        ARRAY_AGG(DISTINCT CASE
            WHEN cvr.video_serial_id IS NULL THEN JSON_BUILD_OBJECT(
                'list_serial', cvl.list_serial,
                'list_name', cvl.list_name
            )::text
        END) FILTER (WHERE cvr.video_serial_id IS NULL AND cvl.list_serial IS NOT NULL) AS not_in_custom_album
    FROM 
        main.video_record vr
    LEFT JOIN 
        main.video v ON v.serial = vr.master_record_id
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
    LEFT JOIN 
        main.video_history vh ON vh.master_record_id = v.serial AND vh.user_id = %s
    LEFT JOIN 
        LATERAL (
            SELECT 
                vh.serial_id AS video_serial, 
                vh.master_record_id AS record_serial
            FROM 
                main.video_history vh 
            WHERE 
                vh.user_id = %s
            ORDER BY 
                vh.last_updated DESC
            LIMIT 1
        ) vr_history ON vr_history.record_serial = v.serial
    LEFT JOIN 
        main.video_favourites vf ON vf.video_id = v.serial AND vf.user_id = %s
    LEFT JOIN 
        main.custom_video_list cvl ON cvl.user_id = %s
    LEFT JOIN 
        main.custom_video_list_records cvr ON cvr.video_serial_id = v.serial AND cvl.list_serial = cvr.list_serial_id
    WHERE 
        v.serial = %s
    GROUP BY 
        vr.video_serial, vh.serial_id, vh.master_record_id, v.title, 
        v.description, v.imdb_rating, v.series, v.season_metadata, vr_history.video_serial, vf.video_id;
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

def get_custom_video_list_records_query():
    return """
SELECT
    v.serial AS video_serial,
    v.title AS video_title
FROM
    video v
INNER JOIN
    custom_video_list_records cvlr
    ON v.serial = cvlr.video_serial_id
INNER JOIN
    custom_video_list cvl
    ON cvlr.list_serial_id = cvl.list_serial
WHERE
    cvl.list_serial = %s
    AND cvlr.user_id = %s
LIMIT %s
OFFSET %s;
"""
def get_favourite_videos_query():
    return """
SELECT
    v.title,
    STRING_AGG(DISTINCT vt.tag, ', ') AS tags,
    STRING_AGG(DISTINCT vd.director, ', ') AS directors,
    STRING_AGG(DISTINCT vs.star, ', ') AS stars,
    STRING_AGG(DISTINCT vw.writer, ', ') AS writers,
    STRING_AGG(DISTINCT vc.creator, ', ') AS creators,
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
    v.imdb_rating DESC;
"""