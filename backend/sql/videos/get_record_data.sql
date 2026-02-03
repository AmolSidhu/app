SELECT 
    v.title AS video_name,
    STRING_AGG(DISTINCT vd.director, ', ') AS video_directors,
    STRING_AGG(DISTINCT vs.star, ', ') AS video_stars,
    STRING_AGG(DISTINCT vw.writer, ', ') AS video_writers,
    STRING_AGG(DISTINCT vc.creator, ', ') AS video_creators,
    STRING_AGG(DISTINCT vt.tag, ', ') AS video_genres,
    v.description AS video_description,
    v.imdb_rating AS video_rating,
    CASE 
        WHEN vh.serial_id IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS resume,
    vh.serial_id AS resume_serial,
    vr.video_serial AS video_serial,
    v.series,
    v.season_metadata,
    vr.video_serial AS serial,
    CASE 
        WHEN vf.video_id IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS favourites,
    ARRAY_AGG(DISTINCT CASE
        WHEN cvr.video_serial_id = v.serial THEN JSON_BUILD_OBJECT(
            'list_serial', cvl.list_serial,
            'list_name', cvl.list_name
        )::text
    END) FILTER (WHERE cvr.video_serial_id = v.serial) AS in_custom_album,
    ARRAY_AGG(DISTINCT CASE
        WHEN cvr.video_serial_id IS NULL THEN JSON_BUILD_OBJECT(
            'list_serial', cvl.list_serial,
            'list_name', cvl.list_name
        )::text
    END) FILTER (WHERE cvr.video_serial_id IS NULL AND cvl.list_serial IS NOT NULL) AS not_in_custom_album
FROM 
    main.video_record vr
LEFT JOIN 
    main.video v ON v.serial = vr.master_record_id
LEFT JOIN 
    main.video_tags vt ON vt.video_id = v.serial
LEFT JOIN 
    main.video_directors vd ON vd.video_id = v.serial
LEFT JOIN 
    main.video_stars vs ON vs.video_id = v.serial
LEFT JOIN 
    main.video_writers vw ON vw.video_id = v.serial
LEFT JOIN 
    main.video_creators vc ON vc.video_id = v.serial
LEFT JOIN 
    main.video_history vh ON vh.master_record_id = v.serial AND vh.user_id = %s
LEFT JOIN 
    LATERAL (
        SELECT 
            vh.serial_id AS video_serial, 
            vh.master_record_id AS record_serial
        FROM 
            main.video_history vh 
        WHERE 
            vh.user_id = %s
        ORDER BY 
            vh.last_updated DESC
        LIMIT 1
    ) vr_history ON vr_history.record_serial = v.serial
LEFT JOIN 
    main.video_favourites vf ON vf.video_id = v.serial AND vf.user_id = %s
LEFT JOIN 
    main.custom_video_list cvl ON cvl.user_id = %s
LEFT JOIN 
    main.custom_video_list_records cvr ON cvr.video_serial_id = v.serial AND cvl.list_serial = cvr.list_serial_id
WHERE 
    v.serial = %s
GROUP BY 
    vr.video_serial, vh.serial_id, vh.master_record_id, v.title, 
    v.description, v.imdb_rating, v.series, v.season_metadata, vr_history.video_serial, vf.video_id;