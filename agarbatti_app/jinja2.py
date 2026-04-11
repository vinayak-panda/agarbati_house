from jinja2 import Environment
from django.urls import reverse
from django.templatetags.static import static
from datetime import datetime


def url(viewname, *args, **kwargs):
    """Custom url function that supports pk=, id= as kwargs"""
    # Extract known URL kwargs and pass them properly
    url_kwargs = {}
    for key in ('pk', 'id', 'slug'):
        if key in kwargs:
            url_kwargs[key] = kwargs.pop(key)
    if url_kwargs:
        return reverse(viewname, kwargs=url_kwargs)
    if args:
        return reverse(viewname, args=args)
    return reverse(viewname)


def environment(**options):
    options.pop('app_dirname', None)
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': url,
        'now': datetime.now,
    })
    env.filters['replace'] = lambda s, old, new: s.replace(old, new)
    return env
