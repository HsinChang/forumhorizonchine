from models import *
from forms import *


def update_menu(menu, form):
    en = form.en.data
    fr = form.fr.data
    zh = form.zh.data
    meta = {'en': en, 'fr': fr, 'zh': zh}

    action = form.action.data

    menu.id = form.id.data
    menu.meta = meta
    if menu.type == 'SIDE_NAV':
        menu.action = None
    else:
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
