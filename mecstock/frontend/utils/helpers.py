def format_currency(value):
    return f"${value:,.2f}"

def calculate_total_cost(services):
    return sum(service['cost'] for service in services)

def get_service_status_label(status):
    status_labels = {
        'pending': 'Pending',
        'completed': 'Completed',
        'in_progress': 'In Progress',
        'canceled': 'Canceled'
    }
    return status_labels.get(status, 'Unknown')

def validate_email(email):
    import re
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def format_date(date):
    return date.strftime("%d/%m/%Y") if date else "N/A"