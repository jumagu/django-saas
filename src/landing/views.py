import helpers.numbers
from django.shortcuts import render
from visits.models import PageVisit

def landing_page_view(request):
    qs = PageVisit.objects.all()
    PageVisit.objects.create(path=request.path)
    page_views_formatted = helpers.numbers.shorten_number(qs.count() * 100_000)
    context = {
        'page_views': page_views_formatted,
    }
    return render(request, 'landing/main.html', context)