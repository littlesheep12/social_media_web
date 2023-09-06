from django.shortcuts import render

# Create your views here.
def index(request):
    # all func must return something
    return render(request, "core/index.html") # /:slash