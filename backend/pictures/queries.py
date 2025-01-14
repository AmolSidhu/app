def custom_album_data_query():
    return """
SELECT
    p.picture_serial,
    p.picture_title,
    p.picture_tags,
    p.picture_people,
    p.description,
    p.picture_editable
FROM
    pictures p
JOIN
    my_album_pictures map ON p.id = map.picture_id
WHERE
    map.album_id = %s
"""

def favourite_pictures_query():
    return """
SELECT
    p.picture_serial,
    p.picture_title,
    p.picture_tags,
    p.picture_people,
    p.description,
    p.picture_editable
FROM
    pictures p
JOIN
    favourite_images fi ON p.id = fi.picture_id
WHERE
    fi.user_id = %s
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
