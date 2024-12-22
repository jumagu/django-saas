from datetime import datetime

def current_date(request):
    return {'now': datetime.now()}

def current_year(request):
    return {'current_year': datetime.now().year}