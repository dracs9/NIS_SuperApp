from django.views.generic import TemplateView

from .mixins import BaseTemplateMixin


class HomeView(BaseTemplateMixin, TemplateView):
    template_name = 'core/home.html'
    section_name = 'Home'
