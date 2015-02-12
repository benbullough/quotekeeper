"""
    View module for Quotes app
"""
from operator import attrgetter
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext, loader
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from quotes.models import Quote
from quotes.models import Tag


def get_tag_counts(request):
    """
        Returns a sorted list of tuples containing tag names and counts
    """
    query_set = Tag.objects.filter(quote__user=request.user).annotate(num_quotes=Count('quote'))
    tag_count_dict = {x.name: x.num_quotes for x in query_set}
    tag_count_list = sorted(tag_count_dict.items())
    return tag_count_list

def get_author_counts(request):
    """
        Returns a sorted list of tuples containing author names and counts
    """
    query_results = Quote.objects.filter(user=request.user).values('author').annotate(Count('author'))
    author_count_dict = {x['author']: x['author__count'] for x in query_results}
    author_count_list = sorted(author_count_dict.items())
    return author_count_list

@login_required
def index(request):
    """
        Index page view
    """
    state_vars = ['sort', 'author', 'tag', 'keep']
    #print request.session.items()
    #clear author and tag filters if no state variables are sent
    if not any(key in request.GET for key in state_vars):
        for key in ['author', 'tag']:
            if key in request.session:
                del request.session[key]

    #add items from request.GET to the session overwriting any old values
    for key in state_vars:
        if key in request.GET:
            request.session[key] = request.GET[key]

    if 'author' in request.GET:
        current_filter = 'author'
    elif 'tag' in request.GET:
        current_filter = 'tag'
    elif 'author' in request.session:
        current_filter = 'author'
    elif 'tag' in request.session:
        current_filter = 'tag'
    else:
        current_filter = 'none'

    filter_params = {}
    if current_filter == 'author':
        auth = request.session['author']
        filter_params['author'] = auth
        quote_list = Quote.objects.filter(user=request.user, author=auth)
    elif current_filter == 'tag':
        tag = request.session['tag']
        filter_params['tag'] = tag
        quote_list = Quote.objects.filter(user=request.user, tags__name=tag)
    else:
        quote_list = Quote.objects.filter(user=request.user)

    if 'sort' in request.session:
        if request.session['sort'] == 'text_up':
            quote_list = sorted(quote_list, key=attrgetter('text'))
        elif request.session['sort'] == 'text_down':
            quote_list = sorted(quote_list, key=attrgetter('text'), reverse=True)
        elif request.session['sort'] == 'author_up':
            quote_list = sorted(quote_list, key=attrgetter('author'))
        elif request.session['sort'] == 'author_down':
            quote_list = sorted(quote_list, key=attrgetter('author'), reverse=True)
        elif request.session['sort'] == 'date_up':
            quote_list = sorted(quote_list, key=attrgetter('date_added'))
        elif request.session['sort'] == 'date_down':
            quote_list = sorted(quote_list, key=attrgetter('date_added'), reverse=True)

    paginator = Paginator(quote_list, 20)  #show 20 quotes per page
    page = request.GET.get('page')
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)

    template = loader.get_template('quotes/index.html')
    context = RequestContext(request, {
        'request':request,
        'quote_list': quotes,
        'tag_list_counts': get_tag_counts(request),
        'author_list_counts': get_author_counts(request),
        'filter_params': filter_params,
        'user': request.user,
        'sort': request.session['sort'] if 'sort' in request.session else None,
        'pages': range(1, 1+quotes.paginator.num_pages)
    })
    return HttpResponse(template.render(context))

@login_required
def detail(request, quote_id):
    """
        Quote detail view
    """
    quote = get_object_or_404(Quote, pk=quote_id, user=request.user)
    #if quote.user != request.user:
    #    quote = []; #don't return records for another user
    if quote:
        tags = quote.get_tags_as_list_of_str()
    else:
        tags = []
    return render(request, "quotes/detail.html",
                  {'request':request, "quote": quote, "tags": tags, "user": request.user})

@login_required
def delete(request, quote_id):
    """
        View to perform deletion of a quote
    """
    quote = get_object_or_404(Quote, pk=quote_id, user=request.user)
    #print len(tag_list)
    #if quote.user == request.user:
    quote.delete()
    return HttpResponseRedirect(reverse('quotes:index'))

@login_required
def edit(request, quote_id):
    """
        Quote edit view
    """
    #return HttpResponse("You're editing quote %s" % quote_id)
    #print request.method
    quote = get_object_or_404(Quote, pk=quote_id, user=request.user)
    if quote.user != request.user:
        return HttpResponseRedirect(reverse('quotes:index'))
    else:
        if request.method == "POST":
            quote.text = request.POST['text']
            quote.author = request.POST['author']
            quote.source = request.POST['source']
            quote.notes = request.POST['notes']
            quote.remove_tags_not_in_list(request.POST.getlist('tags'))
            if request.POST.getlist('newtagcheck'):
                #print request.POST['newtag']
                quote.add_tag_from_str(request.POST['newtag'])
            quote.save()
            return HttpResponseRedirect(reverse('quotes:detail', args=(quote.id,)))
        else:
            tags = quote.get_tags_as_list_of_str() if quote else []
            return render(request, "quotes/edit.html", {'request':request,
                                                        "quote": quote,
                                                        "tags": tags,
                                                        "user": request.user})

@login_required
def new(request):
    """
        New quote view
    """
    return render(request, "quotes/new.html", {'request':request, "user": request.user})

@login_required
def add(request):
    """
        View to process the addition of a new quote
    """
    quote = Quote(text=request.POST['text'],
                  author=request.POST['author'],
                  source=request.POST['source'],
                  notes=request.POST['notes'],
                  date_added=timezone.now(),
                  order=1,
                  user=request.user)

    quote.save()  #need to save before adding a tag

    if request.POST.getlist('newtagcheck'):
        quote.add_tag_from_str(request.POST['newtag'])
        quote.save()

    return HttpResponseRedirect(reverse('quotes:index'))



