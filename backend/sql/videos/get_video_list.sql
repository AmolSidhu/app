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