from django.shortcuts import render
from people.models import FaceMatch
from people.forms import RandomForm

# Create your views here.

def search(request):
    if request.method == 'POST':
        form = RandomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'search.html', {
                'form': form
            })
    else:
        form = RandomForm()
        return render(request, 'search.html', {
            'form': form
        })

def matches(request):
    matches = FaceMatch.objects.filter(human_says_maybe=True)
    return render(request, 'matches.html', {"matches": matches})
