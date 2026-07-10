def paginate_query(query, page, per_page, min_per_page=10, max_per_page=100):
    per_page = max(min_per_page, min(per_page, max_per_page))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'results': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
    }
