def next_previous_episode_data():
    return """
WITH ordered_videos AS (
    SELECT 
        master_record_id,
        video_serial,
        season,
        episode,
        LEAD(video_serial) OVER (PARTITION BY master_record_id ORDER BY season, episode) AS next_video_serial,
        LEAD(season) OVER (PARTITION BY master_record_id ORDER BY season, episode) AS next_season,
        LEAD(episode) OVER (PARTITION BY master_record_id ORDER BY season, episode) AS next_episode,
        LAG(video_serial) OVER (PARTITION BY master_record_id ORDER BY season, episode) AS prev_video_serial,
        LAG(season) OVER (PARTITION BY master_record_id ORDER BY season, episode) AS prev_season,
        LAG(episode) OVER (PARTITION BY master_record_id ORDER BY season, episode) AS prev_episode
    FROM main.video_record
    WHERE master_record_id = %s
)
SELECT 
    master_record_id,
    video_serial,
    season,
    episode,
    prev_video_serial AS previous_video_serial,
    prev_season AS previous_season,
    prev_episode AS previous_episode,
    next_video_serial AS next_video_serial,
    next_season AS next_season,
    next_episode AS next_episode
FROM ordered_videos
WHERE video_serial = %s;
"""