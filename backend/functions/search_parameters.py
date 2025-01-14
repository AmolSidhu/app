def build_video_query_parameters(search):
    return [
        search.video_exact_genre + search.video_similar_genre,
        search.video_exact_directors + search.video_similar_directors,
        search.video_exact_stars + search.video_similar_stars,
        search.video_exact_writers + search.video_similar_writers,
        search.video_exact_creators + search.video_similar_creators,
    ]

def build_picture_query_parameters(search):
    return [
        search.picture_exact_tags,
        [f'%{tag}%' for tag in search.picture_similar_tags],
        search.picture_exact_people,
        [f'%{person}%' for person in search.picture_similar_people],
    ]
