from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def home(request):
    """
        View for home page
    """
    return HttpResponse(render(request, "quotekeeper/index.html", {'request':request} ))

def logout_view(request):
    """
        View to complete logout
    """
    logout(request)
    return HttpResponseRedirect(reverse('home'))

