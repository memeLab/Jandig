from django.db import migrations, models
import datetime
from zoneinfo import ZoneInfo


def create_initial_clippings(apps, schema_editor):
    Clipping = apps.get_model("blog", "Clipping")

    timezone = ZoneInfo("America/Sao_Paulo")
    initial_clippings = [
        {
            "id": 1,
            "title": "Jandig #CulturaDigitalBR",
            "description": "Select Magazine",
            "created": datetime.datetime(2011, 12, 12, tzinfo=timezone),
            "link": "https://www.select.art.br/jandig-culturadigitalbr/",
            "file": "7.-Jandig-CulturaDigitalBR.pdf",
        },
        {
            "id": 2,
            "title": "Uma parceria inusitada: MARTE + JANDIG + Escola de Design/UEMG",
            "description": "Estado de Minas Gerais University Website",
            "created": datetime.datetime(2019, 7, 22, tzinfo=timezone),
            "link": "http://ed.uemg.br/uma-parceria-inusitada-marte-jandig-escola-de-design-uemg/",
            "file": "Jandig-UEMG.jpg",
        },
        {
            "id": 3,
            "title": "Programação formativa do X-Reality contou com workshops de realidade virtual e aumentada",
            "description": "LabArteMídia Website",
            "created": datetime.datetime(2019, 7, 1, tzinfo=timezone),
            "link": "https://sites.usp.br/labartemidia/programacao-formativa-do-x-reality-contou-com-workshops-de-realidade-virtual-e-aumentada/",
            "file": "Jandig-LabArteMidia.pdf",
        },
        {
            "id": 4,
            "title": "Create Art with Augmented Reality",
            "description": "Mozilla Open Leaders Blog",
            "created": datetime.datetime(2019, 5, 31, tzinfo=timezone),
            "link": "https://medium.com/read-write-participate/create-art-with-augmented-reality-e26572524021",
            "file": "Jandig-MozOL.pdf",
        },
        {
            "id": 5,
            "title": "Programação Cultural / Abril de 2017",
            "description": "Coletivo Digital Website",
            "created": datetime.datetime(2017, 4, 10, tzinfo=timezone),
            "link": "http://portalnovo.coletivodigital.org.br/2017/04/",
            "file": "1-programacao-cultural-abril-de-2017.pdf",
        },
        {
            "id": 6,
            "title": "Sesc Sorocaba abre as portas em 1º de setembro com visão sustentável",
            "description": "Sorocaba's Newspaper",
            "created": datetime.datetime(2012, 8, 21, tzinfo=timezone),
            "link": "http://www.diariodesorocaba.com.br/noticia/222472",
            "file": "2-sesc-Sorocaba-abre-as-portas.pdf",
        },
        {
            "id": 7,
            "title": "Do artista ao articulador",
            "description": "Select Magazine",
            "created": datetime.datetime(2012, 7, 30, tzinfo=timezone),
            "link": "https://www.select.art.br/do-artista-ao-articulador/",
            "file": "3.-Do-artista-ao-articulador.pdf",
        },
        {
            "id": 8,
            "title": "Ráfagas de software libre",
            "description": "20 Minutos Newspaper",
            "created": datetime.datetime(2012, 7, 30, tzinfo=timezone),
            "link": "https://blogs.20minutos.es/codigo-abierto/category/software-libre/",
            "file": "9.-Rafagas-de-software-livre.pdf",
        },
        {
            "id": 9,
            "title": "Conheça o Jandig",
            "description": "Labmóvel Website",
            "created": datetime.datetime(2012, 3, 31, tzinfo=timezone),
            "link": "https://labmovel.net/2012/03/31/conheca-o-jandig/",
            "file": "4-conheca-o-Jandig.pdf",
        },
        {
            "id": 10,
            "title": "Entrevista com Pixel",
            "description": "Labmóvel Website",
            "created": datetime.datetime(2012, 3, 21, tzinfo=timezone),
            "link": "https://labmovel.net/2012/03/21/entrevista-com-pixel/",
            "file": "5.-Entrevista-com-Pixel.pdf",
        },
        {
            "id": 11,
            "title": "Campus Party: hackers, multinacionales y activistas",
            "description": "20 Minutos Newspaper",
            "created": datetime.datetime(2012, 2, 12, tzinfo=timezone),
            "link": "https://blogs.20minutos.es/codigo-abierto/2012/02/12/campus-party-hackers-multinacionales-y-activistas/",
            "file": "10.-Campus-Party-hackers-multinacionales-y-activistas.pdf",
        },
        {
            "id": 12,
            "title": "New artist in residence projects mobile media art",
            "description": "NIMk Website",
            "created": datetime.datetime(2012, 2, 1, tzinfo=timezone),
            "link": "http://www.nimk.nl/eng/new-artist-in-residence-projects-mobile-media-art",
            "file": "8.-New-artist-in-residence-projects-mobile-media-art.pdf",
        },
        {
            "id": 13,
            "title": "Residência artística Labmovel + NimK",
            "description": "Site Labmóvel",
            "created": datetime.datetime(2012, 2, 1, tzinfo=timezone),
            "link": "https://labmovel.net/2012/02/01/residencia-artistica-labmovel-nimk/",
            "file": "6-residencia-artistica-labmovel-NimK.pdf",
        },
    ]

    for clipping_data in initial_clippings:
        clipping_data["file"] = "clipping_files/" + clipping_data["file"]
        post = Clipping.objects.create(**clipping_data)


def remove_initial_clippings(apps, schema_editor):
    Clipping = apps.get_model("blog", "Clipping")

    Clipping.objects.filter(id__in=range(0, 14)).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0004_clipping"),
    ]

    operations = [
        migrations.RunPython(
            create_initial_clippings, reverse_code=remove_initial_clippings
        ),
    ]
