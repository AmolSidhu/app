def magic_param_sorter(params):
    where_clauses = []
    where_values = []
    order_by = ''
    order_direction = ''
    limit = 200
    offset = None
    

    return

def convert_operator_to_sql(operator):
    operators = {
        "eq": "=",
        "ne": "!=",
        "gt": ">",
        "gte": ">=",
        "lt": "<",
        "lte": "<=",
        "has": "ILIKE",
        "con": "@>"
    }
    
    return operators.get(operator, "=")