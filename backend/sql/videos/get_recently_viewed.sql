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
LIMIT %s
OFFSET %s;