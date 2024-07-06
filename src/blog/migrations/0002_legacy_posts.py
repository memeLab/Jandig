from django.db import migrations, models
import datetime
from zoneinfo import ZoneInfo


def create_initial_posts(apps, schema_editor):
    Category = apps.get_model("blog", "Category")
    Post = apps.get_model("blog", "Post")
    PostImage = apps.get_model("blog", "PostImage")

    obras_category, _ = Category.objects.get_or_create(name="Obras")
    noticias_category, _ = Category.objects.get_or_create(name="Notícias")
    ativas_category, _ = Category.objects.get_or_create(name="Ativas")
    exhibitions_category, _ = Category.objects.get_or_create(name="Exhibitions")

    timezone = ZoneInfo("America/Sao_Paulo")
    initial_posts = [
        {
            "post": {
                "id": 1,
                "title": "Making Of",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 0, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """Behind-the-scenes images of development, various interventions, and exhibitions.""",
            },
            "images": [
                {
                    "file": "IMG_1283-2.jpg",
                    "description": "Preparing homemade paste for the first urban intervention",
                },
                {
                    "file": "IMG_1289.jpg",
                    "description": "Preparing homemade paste for the first urban intervention",
                },
                {
                    "file": "IMG_20170419_124719_832.jpg",
                    "description": "Installing the Janelas Digitais exhibition",
                },
                {
                    "file": "IMG_20170420_154121_254-1.jpg",
                    "description": "Installing the Janelas Digitais exhibition",
                },
                {
                    "file": "IMG_20170420_170458.jpg",
                    "description": "Installing the Janelas Digitais exhibition",
                },
                {
                    "file": "2011-11-29-19.40.27.jpg",
                    "description": "Drafting the poster for the CulturaDigital.br festival",
                },
                {
                    "file": "IMG_20170413_163535_258.jpg",
                    "description": "Test of the “Sexy na Janela” animation",
                },
                {"file": "Jandig_20131031_154312.jpg", "description": "Marker tests"},
                {
                    "file": "IMG_20170519_193224_636.jpg",
                    "description": "Marker tests for the “Algo a Mais” exhibition",
                },
                {
                    "file": "Jandig_20120331_201203.jpg",
                    "description": "Testing a marker on a yellow T-shirt",
                },
                {
                    "file": "Jandig_20120331_200803.jpg",
                    "description": "Testing a marker on a sticker",
                },
            ],
        },
        {
            "post": {
                "id": 2,
                "title": "Urban Interventions",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 1, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """Urban interventions in London, UK (2017); Montreal, Canada (2017); and São Paulo, Brazil (2011).""",
            },
            "images": [
                {"file": "DLTITQXXkAA_-Ar.jpg", "description": "London"},
                {"file": "IMG_20171017_165803462_HDR.jpg", "description": "Montreal"},
                {"file": "DMXanr4WkAEQ1pP.jpg", "description": "Montreal"},
                {"file": "IMG_1304.jpg", "description": "São Paulo"},
                {"file": "IMG_1322.jpg", "description": "São Paulo"},
                {"file": "IMG_1325.jpg", "description": "São Paulo"},
                {"file": "IMG_1328.jpg", "description": "São Paulo"},
                {"file": "IMG_1338.jpg", "description": "São Paulo"},
                {"file": "IMG_13491.jpg", "description": "São Paulo"},
                {"file": "IMG_1350.jpg", "description": "São Paulo"},
                {"file": "IMG_1355.jpg", "description": "São Paulo"},
                {"file": "IMG_1327-1.jpg", "description": "São Paulo"},
            ],
        },
        {
            "post": {
                "id": 3,
                "title": "Ônibus Hacker",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 2, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """The intervention was carried out on the Ônibus Hacker in São Paulo, Brazil (December 2011), during the departure for the CulturaDigital.br festival at MAM in Rio de Janeiro.""",
            },
            "images": [
                {"file": "IMG_1358.jpg", "description": None},
                {"file": "IMG_1362.jpg", "description": None},
                {"file": "IMG_1365-1.jpg", "description": None},
            ],
        },
        {
            "post": {
                "id": 4,
                "title": "CulturaDigital.br Festival",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 3, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """Posters and a lecture on Jandig were presented at the Museum of Modern Art in Rio de Janeiro, Brazil, from December 2 to 4, 2011, during the CulturaDigital.br Festival.
            
            More than just an event for showcasing ideas and projects, the CulturaDigital.br Festival was a gathering of Brazilian digital culture agents with their global peers. It brought together creators, producers, and activists working at the intersection of culture, politics, and technology, promoting innovations in their fields.
            
            Jandig had its first concrete realization during the Festival. It was our trial by fire! We conducted an intervention and had a representative give a lecture presenting the project and the techniques and concepts involved in its execution.""",
            },
            "images": [
                {
                    "file": "6477047909_edf32607a8_o.jpg",
                    "description": "Talk presenting Jandig",
                },
                {
                    "file": "6477047909_edf32607a8_o.jpg",
                    "description": "Remix of one of Jandig's posters and a photo taken at the event",
                },
                {
                    "file": "fitacrepe_mam-1.jpg",
                    "description": "One of Jandig's posters with markers spread across the event",
                },
            ],
        },
        {
            "post": {
                "id": 5,
                "title": "Campus Party Brazil",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 4, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """The first official Jandig exhibition occurred from February 6 to 12, 2012, at Campus Party in São Paulo, Brazil. We displayed a series of markers of various sizes arranged in a maze. The markers were printed by us on 180g paper and later cut with a paper cutter.
            
            During the seven-day exhibition, attendees could bring t-shirts to have a marker printed on them using the silk-screen technique. While the t-shirts dried, they were hung on a clothesline as part of the installation.
            
            On the esteemed Digital Arts stage, we had the privilege of sharing the (still brief) <a href="https://youtu.be/En2ZslXd0q0?si=fH1qKDB_-NfBARPQ">history of Jandig</a>: from its inception, the journey of uniting people, the software development, the first interventions, to the invaluable lessons we've gleaned along the way. This session was followed by an interview with Campus Party TV.
            
            Moreover, during the event, we had the exciting opportunity to collaborate with the renowned band Móveis Coloniais de Acaju. The band incorporated images of Jandig and the unique sound of the stamp into a <a href="https://youtu.be/SFn7twtVW0o?si=rgXriyrG5fQu5cUL">music video recorded live during the event</a>, adding a new dimension to our artistic expression. They also <a href="https://youtu.be/iYNUUs54kNg?si=OXeuXQMQd72Oe9pS">interviewed us</a> during the event.""",
            },
            "images": [
                {
                    "file": "jandig-CP-6-1.jpg",
                    "description": "Placa apresentando o Jandig",
                },
                {
                    "file": "palestra_jandig_cp2012-5.jpg",
                    "description": "Palestra sobre o Jandig no palco de Artes Digitais",
                },
                {
                    "file": "palestra_jandig_cp2012-6.jpg",
                    "description": "Demonstração durante a palestra",
                },
                {
                    "file": "palestra_jandig_cp2012-10.jpg",
                    "description": "Um urso de pelúcia ganhou um marcador",
                },
                {
                    "file": "palestra_jandig_cp2012-13-1.jpg",
                    "description": "Entrevista para a TV Campus Party",
                },
                {
                    "file": "jandig-CP-15-1.jpg",
                    "description": "Aplicando silk-screen em uma camiseta",
                },
                {
                    "file": "jandig-CP-14.jpg",
                    "description": "Camiseta após a aplicação de silk",
                },
                {
                    "file": "jandig-CP-17.jpg",
                    "description": "Verificando se a tinta secou",
                },
                {"file": "jandig-CP-1-1.jpg", "description": "Exposição"},
                {"file": "Jandig_20120211_133940.jpg", "description": "Exposição"},
                {"file": "Jandig_20120211_134014.jpg", "description": "Exposição"},
                {
                    "file": "jandig-CP-7.jpg",
                    "description": "Entrevista para a Móveis Coloniais de Acaju",
                },
                {
                    "file": "Jandig_20120211_134137.jpg",
                    "description": "Superfície utilizada pela Móveis Coloniais de Araju para gravar som de carimbadas, após a gravação",
                },
            ],
        },
        {
            "post": {
                "id": 6,
                "title": "AiR – Mobile Media Art",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 5, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """Mobile Media Art Artists in Residency was an initiative organized by NIMk (Netherlands) and Vivo ARTE.MOV (Brazil) from March to April 2012. This pioneering artistic residency utilized mobile laboratories equipped for digital production and dissemination, developed in Amsterdam and São Paulo. 
            Pixel was selected for the residency with the Jandig initiative. During the residency, Jandig inspired the design of the <a href="http://nimk.nl/blog/ar/narrative-navigation/">Narrative Navigation</a>  installation. The final installation was presented in São Paulo and Rotterdam (Netherlands). 
            During the residency Artistic interventions at the São Paulo Cultural Center and at Dom José Gaspar Square (São Paulo, Brazil).""",
            },
            "images": [
                {"file": "2012-03-25-19.07.29.jpg", "description": None},
                {"file": "2012-04-15-16.39.58.jpg", "description": None},
                {"file": "LabMovel-24.jpg", "description": None},
                {"file": "LabMovel-26.jpg", "description": None},
                {"file": "LabMovel-32.jpg", "description": None},
                {"file": "LabMovel-37.jpg", "description": None},
                {"file": "LabMovel-38.jpg", "description": None},
                {"file": "LabMovel-41.jpg", "description": None},
                {"file": "LabMovel-43.jpg", "description": None},
            ],
        },
        {
            "post": {
                "id": 7,
                "title": "BaixoCentro Festival",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 6, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """BaixoCentro, a street festival that began as a seed of an idea at the Casa da Cultura Digital in mid-2011, was nurtured into existence by a collective effort. The aim was to create a festival that would connect cultural hubs in the neighborhoods around the Minhocão in São Paulo, a vision that we all shared and worked towards.
            
            By early 2012, the festival had blossomed into a network of over a hundred volunteers, a testament to the community's dedication and belief in the project. A crowdfunding campaign, which achieved the project's funding, was a significant milestone, making it one of the most successful campaigns in Brazil at the time.
            
            Jandig carried out urban interventions from March 23 to 31 for the festival's 2012 program. The interventions started with meetings with the public at the Casa da Cultura Digital, who then joined us in posting art in various locations.""",
            },
            "images": [
                {"file": "2012-03-31-20.42.27.jpg", "description": None},
                {"file": "Jandig_20120331_204753.jpg", "description": None},
                {"file": "Jandig_20120331_204837.jpg", "description": None},
                {"file": "2012-03-31-21.08.32.jpg", "description": None},
            ],
        },
        {
            "post": {
                "id": 8,
                "title": "Algo a Mais?",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 7, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """In 2012, we were invited to create an exhibition for the opening of Sesc Sorocaba (Brazil).
            
            The Algo a Mais? (Something More?) exhibition theme was robots. We invited animators to create content to appear in augmented reality, a designer to create the markers, and a hacker to develop moving robots that held markers. 
            Besides the robots, we also had markers in magnets (allowing the public to rearrange part of the exhibition). We gave stickers with markers to the attendees, allowing them to get part of the exhibition. 
            
            The Algo a Mais? exhibition was a resounding success. Originally planned for September, its popularity led to an extension. Sesc, impressed by the response, requested to prolong the exhibition for an additional month until the end of October.
            
            
            <iframe width="560" height="315" src="https://www.youtube.com/watch?v=h4H2KFBXykQ" frameborder="0" allowfullscreen></iframe>
            """,
            },
            "images": [
                {"file": "IMG_1567.jpg", "description": None},
                {"file": "IMG_1541.jpg", "description": None},
                {"file": "2012-09-02-16.50.06.jpg", "description": None},
                {"file": "IMG_1564.jpg", "description": None},
                {"file": "2012-09-01-10.22.42.jpg", "description": None},
                {"file": "2012-09-01-10.24.07.jpg", "description": None},
                {"file": "2012-09-01-10.24.18.jpg", "description": None},
                {"file": "IMG_1565.jpg", "description": None},
            ],
        },
        {
            "post": {
                "id": 9,
                "title": "FISL",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 8, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """The International Free Software Forum - FISL - took place annually from 2000 to 2018 in Porto Alegre, Brazil. FISL is considered one of the world's most significant open-source events, providing integrated technical, political, and social discussions about free software. In July 2012, the event hosted 7,709 participants from 23 countries.
            
            At the invitation of the event's organization, we gave a lecture. We also created artwork based on the event's logo, which was featured on posters throughout the exhibition area, and stickers were distributed to participants (along with stickers from other exhibitions).""",
            },
            "images": [
                {"file": "Jandig_20120724_184642.jpg", "description": None},
                {"file": "Ay1b6kICYAEP2FF.jpg", "description": None},
                {"file": "Ay1cEu1CAAAcYvO.jpg", "description": None},
                {"file": "Ayv8FkGCIAIqVWJ.jpg", "description": None},
                {"file": "Jandig_20120724_194605.jpg", "description": None},
                {"file": "Jandig_20120724_201008.jpg", "description": None},
            ],
        },
        {
            "post": {
                "id": 10,
                "title": "Janelas Digitais",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 9, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """The Janelas Digitais exhibition was at Coletivo Digital São Paulo (Brazil) from April to June 2017.
            
            The text below is by Thiago Esperandio, curator of Coletivo Digital.
            
            <b>Janelas Digitais (Jandig), conceived by VJ Pixel</b>
            There is much to say about the Jandig Project that brings this exhibition to Coletivo Digital. However, it’s inevitable to break any formality and start by saying it is incredibly cool. The reaction of anyone who downloads the app and sees this joyful fusion of art and technology is usually a big smile… whether it’s due to the interaction with a technology that still feels quite futuristic or the access to virtual works that bring a playful and colorful vision to the black and white markers (most likely, it’s both). After this initial moment of fun, Janelas Digitais becomes even more extraordinary when we know that the works – both virtual and tangible – are licensed under Creative Commons, allowing other creators to use them; that the app’s source code is open for anyone to explore and learn from; and that the entire project involved various artists working collaboratively. In times of technological wars, the rise of ultra-conservative thinking, a society of control, and the internet under attack from corrupt powers, it is a privilege for Coletivo Digital to host these digital windows, bringing such fraternal and inspiring landscapes to our welcoming space.""",
            },
            "images": [
                {"file": "IMG_9909-1.jpg", "description": None},
                {"file": "MG_9905.jpg", "description": None},
                {"file": "Jandig.jpg", "description": None},
                {"file": "IMG_9921-2.jpg", "description": None},
                {"file": "IMG_20170421_191253_178.jpg", "description": None},
                {"file": "IMG_9935-1.jpg", "description": None},
                {"file": "Jandig_20170420_220437.jpg", "description": None},
                {"file": "Jandig_20170420_220602.jpg", "description": None},
                {"file": "IMG_20170313_150654.jpg", "description": None},
                {"file": "Jandig_20170420_220550.jpg", "description": None},
                {"file": "Jandig_20170420_201543.jpg", "description": None},
                {"file": "IMG_9923.jpg", "description": None},
                {"file": "Jandig2.jpg", "description": None},
                {"file": "FB_IMG_1492460805870.jpg", "description": None},
            ],
        },
        {
            "post": {
                "id": 11,
                "title": "Virada Cultural",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 10, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """Exhibition during Virada Cultural at Sesc Belenzinho (São Paulo, Brazil), May 2017.
            
            Virada Cultural is an annual event promoted by the São Paulo municipal government since 2005. With the support of various artistic and institutional partners, it aims to provide 24 continuous hours of cultural events at various locations throughout the city.
            
            This exhibition premiered the cube with markers. In addition to the displayed boxes, there were also buildable cubes with markers. Some works from this exhibition have become “classics,” such as Tokusatsu and Temaki.""",
            },
            "images": [
                {"file": "IMG_20170521_142327_972.jpg", "description": None},
                {"file": "Jandig_20170520_204811.jpg", "description": None},
                {"file": "Jandig_20170520_201449.jpg", "description": None},
                {
                    "file": "Jandig_20170520_201544.jpg",
                    "description": None,
                },
                {"file": "IMG_20170520_214145_290.jpg", "description": None},
                {"file": "IMG_20170521_154532_735.jpg", "description": None},
                {"file": "IMG_20170520_233302589.jpg", "description": None},
                {"file": "IMG-20170520-WA0003.jpg", "description": None},
                {"file": "IMG_20170520_205738_867.jpg", "description": None},
                {"file": "IMG_20170521_172545_124.jpg", "description": None},
            ],
        },
        {
            "post": {
                "id": 12,
                "title": "GAS Station",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 11, tzinfo=timezone),
                "categories": [exhibitions_category],
                "body": """GAS Station (Games and Art Stratford) is a space dedicated to projects, ideas, and conversations at the intersection of games, performing arts, and technology. GAS supports early-stage projects in London with space, equipment, and mentorship, fostering partnerships and exchanges among professionals from various creative fields. The space is curated by ZU-UK, an internationally renowned company known for creating critically acclaimed and socially engaged performances and digital art that place the audience at the center of the experience.
            
            In October 2017, a Jandig intervention was carried out in the institution's container area.""",
            },
            "images": [
                {"file": "20171006_155417.jpg", "description": None},
                {"file": "20171006_154846.jpg", "description": None},
                {"file": "20171006_155353.jpg", "description": None},
                {"file": "20171006_155338.jpg", "description": None},
                {"file": "20171006_155322.jpg", "description": None},
                {"file": "20171006_154803.jpg", "description": None},
            ],
        },
    ]

    for dict_data in initial_posts:
        post_data = dict_data["post"]
        images = dict_data["images"]
        categories = post_data["categories"]

        del post_data["categories"]
        post = Post.objects.create(**post_data)
        post.categories.set(categories)
        post.save()

        for image_data in images:
            image_data["file"] = "post_images/" + image_data["file"]
            image = PostImage.objects.create(**image_data)
            image.posts.add(post)


def remove_initial_posts(apps, schema_editor):
    Category = apps.get_model("blog", "Category")
    Post = apps.get_model("blog", "Post")
    PostImage = apps.get_model("blog", "PostImage")

    Category.objects.filter(name="Obras").delete()
    Category.objects.filter(name="Notícias").delete()
    Category.objects.filter(name="Ativas").delete()

    Post.objects.filter(id__in=range(0, 12)).delete()
    PostImage.objects.filter(id__in=range(0, 99)).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_posts, reverse_code=remove_initial_posts),
    ]
