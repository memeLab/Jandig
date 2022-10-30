from boogie.router import Router

from .models import Exhibit

urlpatterns = Router(
    template="core/exhibit.jinja2",
    models={"exhibit": Exhibit},
    lookup_field={"exhibit": "slug"},
)


@urlpatterns.route("<model:exhibit>/")
def exhibit(request, exhibit):
    ctx = {"exhibit": exhibit, "artworks": exhibit.artworks.all()}
    return ctx
