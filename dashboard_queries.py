from database import execute_query


def get_total_customers():
    query = "SELECT COUNT(*) as total FROM customers"
    result = execute_query(query, fetch_one=True)
    return result["total"] if result else 0


def get_new_today():
    query = "SELECT COUNT(*) as total FROM customers WHERE DATE(IFNULL(last_visited, NOW())) = CURDATE() AND visit_count = 1"
    result = execute_query(query, fetch_one=True)
    return result["total"] if result else 0


def get_visits_today():
    query = (
        "SELECT COUNT(*) as total FROM customers WHERE DATE(last_visited) = CURDATE()"
    )
    result = execute_query(query, fetch_one=True)
    return result["total"] if result else 0


def get_kpi_stats():
    return {
        "totalCustomers": get_total_customers(),
        "newToday": get_new_today(),
        "totalVisitsToday": get_visits_today(),
        "avgVisitDuration": 0,  # Placeholder as discussed
    }


def get_visit_trend(days=10):
    query = """
        SELECT DATE(last_visited) as visit_date, COUNT(*) as visit_count
        FROM customers
        WHERE last_visited IS NOT NULL AND last_visited >= CURDATE() - INTERVAL %s DAY
        GROUP BY DATE(last_visited)
        ORDER BY visit_date ASC
    """
    return execute_query(query, (days,), fetch_all=True)


def get_top_visitors(limit=5):
    query = """
        SELECT COALESCE(name, unique_id) as visitor_name, visit_count
        FROM customers
        ORDER BY visit_count DESC
        LIMIT %s
    """
    return execute_query(query, (limit,), fetch_all=True)
