SELECT DISTINCT ON (v.serial)
    v.title,
    v.serial
FROM video v
WHERE
    (v.title ILIKE %s)
    AND v.current_status = 'P'
    AND v.private = FALSE
ORDER BY v.serial, v.title;