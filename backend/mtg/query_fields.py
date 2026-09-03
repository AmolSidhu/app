import re

magic_cards_query_fields = {
    "card_name",
    "mana_cost",
    "cmc",
    "colour_white",
    "colour_blue",
    "colour_black",
    "colour_red",
    "colour_green",
    "colour_colourless",
    "colour_identity_white",
    "colour_identity_blue",
    "colour_identity_black",
    "colour_identity_red",
    "colour_identity_green",
    "colour_identity_colourless",
    "reserved",
    "keywords",
    "foil",
    "non_foil",
    "set_name",
    "rarity",
    "power",
    "toughness",
    "loyalty"
}

magic_cards_query_operators = {
    "eq": "=",
    "ne": "!=",
    "gt": ">",
    "gte": ">=",
    "lt": "<",
    "lte": "<=",
    "contains": "LIKE"
}

def create_where_clause(raw_sql):
    if not raw_sql:
        return "", []

    conditions = raw_sql.split("AND")
    where_clauses = []
    params = []

    for condition in conditions:
        condition = condition.strip()

        match = re.match(r"(\w+)\s*(=|>=|<=|>|<|LIKE)\s*(.+)", condition)
        if not match:
            continue

        field, operator, value = match.groups()

        if field not in magic_cards_query_fields:
            continue

        value = value.strip().strip("'")
        
        if operator.upper() == "LIKE":
            where_clauses.append(f"{field} LIKE %s")
            params.append(value)
        else:
            where_clauses.append(f"{field} {operator} %s")
            params.append(value)

    if not where_clauses:
        return "", []

    return "WHERE " + " AND ".join(where_clauses), params
