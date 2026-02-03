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