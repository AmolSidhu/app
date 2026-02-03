SELECT
    p.picture_serial,
    p.picture_title,
    p.description AS picture_description,
    COALESCE(STRING_AGG(DISTINCT it.tag, ','), '') AS picture_tags,
    COALESCE(STRING_AGG(DISTINCT ip.person, ','), '') AS picture_people
FROM
    pictures p
LEFT JOIN image_tags it ON p.picture_serial = it.picture_id
LEFT JOIN image_people_tags ip ON p.picture_serial = ip.picture_id
WHERE
    p.picture_serial = %s
GROUP BY
    p.picture_serial, p.picture_title, p.description;