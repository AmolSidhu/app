def get_article_title_search_query():
    return """
    SELECT * FROM main_article
    WHERE title ILIKE %s
    """

def get_article_tag_search_query():
    return """
    SELECT * FROM article_tags
    WHERE tags ILIKE %s
    """