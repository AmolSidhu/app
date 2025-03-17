def custom_album_data_query():
    return """
SELECT
    p.picture_serial,
    p.picture_title,
    p.description,
    STRING_AGG(DISTINCT t.tag, ', ') AS picture_tags,
    STRING_AGG(DISTINCT pt.person, ', ') AS picture_people,
    p.description,
    p.picture_editable
FROM
    pictures p
JOIN
    my_album_pictures map ON map.picture_id = p.picture_serial
LEFT JOIN
    image_tags t ON t.picture_id = p.picture_serial
LEFT JOIN
    image_people_tags pt ON pt.picture_id = p.picture_serial
WHERE
    map.album_id = %s
GROUP BY
    p.picture_serial, p.picture_title, p.description, p.picture_editable
"""

def picture_data_query():
    return """
SELECT
    p.picture_serial,
    p.picture_title,
    p.description AS picture_description,
    COALESCE(STRING_AGG(DISTINCT it.tag, ','), '') AS picture_tags,
    COALESCE(STRING_AGG(DISTINCT ip.person, ','), '') AS picture_people,
    ARRAY_AGG(DISTINCT CASE
        WHEN map.picture_id IS NOT NULL THEN JSON_BUILD_OBJECT('album_serial', ma.album_serial, 'album_name', ma.album_name)::text
    END) FILTER (WHERE map.picture_id IS NOT NULL) AS in_custom_albums,
    ARRAY_AGG(DISTINCT CASE
        WHEN map.picture_id IS NULL THEN JSON_BUILD_OBJECT('album_serial', ma.album_serial, 'album_name', ma.album_name)::text
    END) FILTER (WHERE ma.album_serial IS NOT NULL AND map.picture_id IS NULL) AS not_in_custom_albums,
    CASE
        WHEN fp.picture_id IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS is_favourite
FROM
    pictures p
LEFT JOIN image_tags it ON p.picture_serial = it.picture_id
LEFT JOIN image_people_tags ip ON p.picture_serial = ip.picture_id
LEFT JOIN my_albums ma 
    ON ma.user_id = %s
LEFT JOIN my_album_pictures map 
    ON p.picture_serial = map.picture_id AND ma.album_serial = map.album_id
LEFT JOIN main.favourite_images fp 
    ON p.picture_serial = fp.picture_id AND fp.user_id = %s
WHERE
    p.picture_serial = %s
GROUP BY
    p.picture_serial, p.picture_title, p.description, fp.picture_id;
"""

def favourite_pictures_query():
    return """
SELECT
    p.picture_serial,
    p.picture_title,
    STRING_AGG(DISTINCT it.tag, ', ') AS picture_tags,
    STRING_AGG(DISTINCT ipt.person, ', ') AS picture_people,
    p.description AS picture_description,
    p.picture_editable
FROM
    pictures p
JOIN
    favourite_images fi ON p.picture_serial = fi.picture_id
LEFT JOIN
    image_tags it ON p.picture_serial = it.picture_id
LEFT JOIN
    image_people_tags ipt ON p.picture_serial = ipt.picture_id
WHERE
    fi.user_id = %s
GROUP BY
    p.picture_serial, p.picture_title, p.description, p.picture_editable
"""

def picture_search_query():
    return """
SELECT 
    p.picture_serial,
    p.picture_title,
    STRING_AGG(DISTINCT it.tag, ', ') AS tags,
    STRING_AGG(DISTINCT ipt.person, ', ') AS people,
    p.description,
    p.date_uploaded
FROM
    pictures p
LEFT JOIN
    image_tags it ON it.picture_id::VARCHAR = p.picture_serial
LEFT JOIN
    image_people_tags ipt ON ipt.picture_id::VARCHAR = p.picture_serial
WHERE
    p.current_status = 'A'
AND
    (
        COALESCE(it.tag, '') = ANY(%s)
        OR it.tag LIKE ANY(%s)
        OR COALESCE(ipt.person, '') = ANY(%s)
        OR ipt.person LIKE ANY(%s)
    )
GROUP BY
    p.picture_serial, p.picture_title, p.description, p.date_uploaded
ORDER BY 
    p.date_uploaded DESC;
"""
