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