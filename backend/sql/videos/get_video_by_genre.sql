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
LIMIT %s
OFFSET %s;