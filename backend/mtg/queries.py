def get_magic_card_data_query(where_clauses):
    if not where_clauses:
        return """
            WITH user_fields AS (
                SELECT jsonb_array_elements_text(fields) AS field
                FROM magic_view_fields
                WHERE user_id = %s
            ),
            page_cards AS (
                SELECT card_id
                FROM magic_cards
                ORDER BY card_id
                LIMIT %s OFFSET %s
            )
            SELECT
                mc.card_id,
                uf.field,
                (mc.card_json -> uf.field) AS value
            FROM magic_cards mc
            JOIN page_cards pc ON pc.card_id = mc.card_id
            CROSS JOIN user_fields uf
            ORDER BY mc.card_id;
        """

    base = """
        WITH user_fields AS (
            SELECT jsonb_array_elements_text(fields) AS field
            FROM magic_view_fields
            WHERE user_id = %s
        ),
        expanded AS (
            SELECT
                mc.card_id,
                uf.field,
                (mc.card_json -> uf.field) AS value
            FROM magic_cards mc
            CROSS JOIN user_fields uf
        ),
        matching_cards AS (
            SELECT DISTINCT card_id
            FROM expanded
            WHERE 1 = 1
    """

    fixed = [c.replace("value ", "value::text ") for c in where_clauses]
    base += " AND " + " AND ".join(fixed)

    base += """
        ),
        page_cards AS (
            SELECT card_id
            FROM matching_cards
            ORDER BY card_id 
            LIMIT %s OFFSET %s
        )
        SELECT
            e.card_id,
            e.field,
            e.value
        FROM expanded e
        JOIN page_cards pc ON pc.card_id = e.card_id
        ORDER BY e.card_id;
    """

    return base


def magic_card_data_query(where_clause=""):
    base = """
        SELECT card_id, card_name, release_date, 
        mana_cost, cmc, type_line, oracle_text, colour_white,
        colour_blue, colour_black, colour_red, colour_green,
        colour_colourless, colour_identity_white,
        colour_identity_blue, colour_identity_black,
        colour_identity_red, colour_identity_green,
        colour_identity_colourless, reserved, keywords,
        foil, non_foil, set_name, set_type, 
        collector_number, rarity, power, toughness,
        flavor_text, edh_rank, penny_rank, promo_types,
        loyalty, life_modifier, produced_mana, 
        hand_modifier, defense, back_exists
        FROM magic_cards_view
        {where_clause}
        ORDER BY release_date DESC
        LIMIT %s OFFSET %s;
    """
    return base.format(where_clause=where_clause)
