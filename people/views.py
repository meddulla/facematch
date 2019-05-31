from django.shortcuts import render
from people.models import FaceMatch

# Create your views here.

def search(request):
    return render(request, 'search.html')


def matches(request):
    matches = FaceMatch.objects.filter(human_says_maybe=True)
    return render(request, 'matches.html', {"matches": matches})
