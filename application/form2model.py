from models import *
from forms import *


def update_menu(menu, form):
    en = form.en.data
    fr = form.fr.data
    zh = form.zh.data
    meta = {'en': en, 'fr': fr, 'zh': zh}

    parent = None
    children = []
    # if len(form.parent.data) > 0:
    #     parent = form.parent.data
    # if form.action.data:
    #     action = form.action.data
    if len(form.children.data) > 0:
        children = form.children.data

    action = form.action.data

    menu.id = form.id.data
    menu.type = form.type.data
    menu.meta = meta
    menu.parent = parent
    menu.children = [ndb.Key(urlsafe=url) for url in children]
    menu.action = action


def update_page(page, form):
    en = {
        'title': form.title_en.data,
        'content': form.content_en.data
    }
    fr = {
        'title': form.title_fr.data,
        'content': form.content_fr.data
    }
    zh = {
        'title': form.title_zh.data,
        'content': form.content_zh.data
    }
    meta = {'en': en, 'fr': fr, 'zh': zh}
    page.meta = meta
    page.id = form.id.data
    page.type = form.type.data
    page.url = form.url.data
    page.position = ndb.Key(urlsafe=form.position.data)
