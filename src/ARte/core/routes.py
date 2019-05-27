from boogie.router import Router

from .models import Exhibit
from .models import Artwork2

urlpatterns = Router(
    template="core/exhibit.jinja2",
    models={"exhibit": Exhibit},
    lookup_field={"exhibit": "slug"},
)


@urlpatterns.route("<model:exhibit>/")
def exhibit(request, exhibit):
    ctx = { 
        'exhibit' : exhibit,
        'artworks':
            [
                Artwork2(patt="antipodas", gif="antipodas", scale="1.5 1.5"),
                Artwork2(patt="gueixa", gif="gueixa"),
            ]
    }
    return ctx
