def get_all_dashbaord_items():
    return """
SELECT *
FROM dashboard_item
WHERE user_id = %s
"""