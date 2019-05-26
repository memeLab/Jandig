from django.core.management.base import BaseCommand
from core.models import Exhibit
from django.contrib.auth.models import User
from users.models import Artwork, Profile, Marker, Object
from django.core.files.images import ImageFile
import os

class Command(BaseCommand):
    help = "Load project base data"

    def handle(self, *args, **options):
        u1 = User()
        u1.save()
        p1 = u1.profile

        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        path = lambda str: os.path.join(ROOT_DIR,"users", "media", str)
        image = lambda str: ImageFile(open(path(str), "rb"))

        marker = Marker(
            source=image("markers/gueixa.png"), 
            author=p1,
            owner=p1,
            patt=image("patts/gueixa.patt")
        )
        marker.save()

        augmented = Object(source=image("objects/gueixa.gif"), author=p1, owner=p1)
        augmented.save()


        a1 = Artwork(
                    author=p1,
                    marker=marker,
                    augmented=augmented,
                    title="meuPau",
                    description="um meu piru"
                )
        a1.save()

        e1 = Exhibit()
        e2 = Exhibit()
       
        e1.name = "exibicao1"
        e2.name = "exibicao2"
        
        e1.slug = e1.url
        e2.slug = e2.url
        
        e1.save()
        e2.save()

        e1.artworks.add(a1)
        e2.artworks.add(a1)

        self.stdout.write("Finished populating models")