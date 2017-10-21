from django.views.generic import TemplateView


class MainDocView(TemplateView):
    template_name = 'docs/overview.html'
