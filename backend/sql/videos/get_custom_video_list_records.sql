SELECT
    v.serial,
    v.title
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