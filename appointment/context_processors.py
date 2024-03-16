from accounts.models import Specialization

def menu_links(request):
    links = Specialization.objects.all()
    return dict(links=links)