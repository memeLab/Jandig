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
                "title": "Exposição em Londres",
                "status": "published",
                "created": datetime.datetime(2010, 11, 25, 18, 32,tzinfo=timezone),
                "categories": [obras_category],
                "body": """Exposição em Londres.
                <br /><b>Autor do objeto:</b> <a href="https://ugosan.org/">Ugo Sangiorgi</a>
                <br /><b>Autor do marcador:</b> <a href="https://memelab.com.br/">VJ pixel</a>""",
            },
            "images": [
                {
                    "file": "1.1ugo-londres.jpg",
                    "description": None,
                },
                {
                    "file": "1.2quadro_A.png",
                    "description": None,
                },
            ],
        },
        {
            "post": {
                "id": 2,
                "title": "Lá Fora",
                "status": "published",
                "created": datetime.datetime(2010, 11, 25, 19, 30,tzinfo=timezone),
                "categories": [obras_category],
                "body": """Fotomontagem ilustrando a necessidade de liberdade.
                <br /><b>Autor do objeto:</b><a href="https://aiedafreitas.com/">Aieda Freitas</a>
                <br /><b>Autor do marcador:</b><a href="https://baixocentro.org/">Andressa Vianna</a>""",
            },
            "images": [
                {"file": "2.1aieda-fora.jpg", "description": None},
                {"file": "2.2U_A.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 3,
                "title": "A sociedade das águas podres",
                "status": "published",
                "created": datetime.datetime(2010, 11, 25, 19, 34,tzinfo=timezone),
                "categories": [obras_category],
                "body": """Uma colagem de imagens com um toque surrealista sobre a poluição das águas.
            <br /><b>Autor do objeto:</b><a href="https://aiedafreitas.com/">Aieda Freitas</a>
            <br /><b>Autor do marcador:</b><a href="https://baixocentro.org/">Andressa Vianna</a>""",
            },
            "images": [
                {"file": "3.1aieda-sociedade.jpg", "description": None},
                {"file": "3.2seta_A.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 4,
                "title": "#ajudemariacleneilda",
                "status": "published",
                "created": datetime.datetime(2010, 11, 25, 19, 38,tzinfo=timezone),
                "categories": [obras_category],
                "body": """Elaborada pela equipe RISSCA (Rede de Incentivo a Saúde e Satisfação Corporal e Alimentar) mostra o rosto de Maria Cleneilda, personagem importante na história dos tratamentos especializados em Transtornos Alimentares. Apesar da sofrida batalha que Cleneilda vem enfrentando, a obra mostra seu rosto saudável e sorrindo, pois é como desejamos que ela volte a ficar. As cores e os traços são inspirados na Pop Art, pois a luta contra o descaso por parte da instituição em que Cleneilda estava sendo tratada comoveu e mobilizou pessoas como nunca antes se viu.
            <br /><b>Autor do objeto:</b><a href="https://rissca.net/blog">Luciana Caraça</a>
            <br /><b>Autor do marcador:</b><a href="https://baixocentro.org/">Andressa Vianna</a>""",
            },
            "images": [
                {"file": "4.1luciana-mcleneilda.jpg", "description": None},
                {"file": "4.2rissca_A.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 5,
                "title": "Borboleta amarela",
                "status": "published",
                "created": datetime.datetime(2010, 11, 25, 19, 59,tzinfo=timezone),
                "categories": [obras_category],
                "body": """Outra forma de trazer o feminino. No desenho a energia sai de dentro pra fora, como quem irradia, como se o plexo solar ou o útero estivesse ativo emanando movimento numa espécie de explosão ou parto.<br />
            <br /><b>Autor do objeto:</b><a href="https://poliketa.blogspot.com/">Taíme Gouvêa</a>
            <br /><b>Autor do marcador:</b><a href="https://baixocentro.org/">Andressa Vianna</a>""",
            },
            "images": [
                {"file": "5.1taime-borboleta.jpg", "description": None},
                {"file": "5.2foco_A.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 6,
                "title": "Mulher Árvore",
                "status": "published",
                "created": datetime.datetime(2010, 11, 25, 20, 1,tzinfo=timezone),
                "categories": [obras_category],
                "body": """Talvez seja algo parecido como criar raízes, expandir energia, dança, movimento... uma brincadeira de tentar fazer das pombas um carrossel que se move com a energia que perpassa o corpo da árvore-mulher kundalini? Árvore da vida, criação de um feminino, uma mulher que dança representando criações diversas? As pombas são a representação do orixá oxalá, criador do humano. E ela, humana que é, em seu devir-árvore, dança olhando pra cima, pra onde se ergue, pra onde cresce... mesmo que em si.
            <br /><b>Autor do objeto:</b><a href="https://poliketa.blogspot.com/">Taíme Gouvêa</a>
            <br /><b>Autor do marcador:</b><a href="https://baixocentro.org/">Andressa Vianna</a>""",
            },
            "images": [
                {"file": "6.1taime-mulher.jpg", "description": None},
                {"file": "6.onda_A-300x300.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 7,
                "title": "Medusa",
                "status": "published",
                "created": datetime.datetime(2010, 11, 25, 20, 5,tzinfo=timezone),
                "categories": [obras_category],
                "body": """As Imagens da série gravuras digitais, foram produzidas a partir do ano de 2003; tratam-se de imagens híbridas que dialogam com as formas tradicionais da criação artística como: desenho, pintura e fotografia  inseridas no processo de pintura digital e manipulação através de software de edição, distribuídas através da rede como uma “impressão digital “. A temática abordada gira em torno das paisagens urbanas e cotidiano da cidade de São Paulo...\n<br /><b>Autor do objeto:</b><a href="https://stressionismo.blogspot.com">Wilson Inacio</a>\n<br /><b>Autor do marcador:</b><a href="https://baixocentro.org/">Andressa Vianna</a>""",
            },
            "images": [
                {"file": "7.1wilson-medusa.jpg", "description": None},
                {"file": "7.2cassete_A.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 8,
                "title": "Urbano",
                "status": "published",
                "created": datetime.datetime(2010, 11, 25, 20, 7,tzinfo=timezone),
                "categories": [obras_category],
                "body": """As Imagens da série gravuras digitais, foram produzidas a partir do ano de 2003; tratam-se de imagens híbridas que dialogam com as formas tradicionais da criação artística como: desenho, pintura e fotografia inseridas no processo de pintura digital e manipulação através de software de edição, distribuídas através da rede como uma "impressão digital". A temática abordada gira em torno das paisagens urbanas e cotidiano da cidade de São Paulo...
            <br /><b>Autor do objeto:</b><a href="https://stressionismo.blogspot.com">Wilson Inacio</a>
            <br /><b>Autor do marcador:</b><a href="https://baixocentro.org/">Andressa Vianna</a>""",
            },
            "images": [{"file": "8.1wilson-urbano.jpg", "description": None}],
        },
        {
            "post": {
                "id": 9,
                "title": "Estamos em construção. Entre na obra.",
                "status": "published",
                "created": datetime.datetime(2011, 9, 26, 16, 21,tzinfo=timezone),
                "categories": [noticias_category],
                "body": """Isso é um canteiro em obras. Aqui você poderá acompanhar e participar do desenvolvimento do Jandig (entenda melhor o que é isso <a href="https://memelab.com.br/jandig/sobre"></a>). Ao mesmo tempo em que trabalhamos na criação do software que irá viabilizar as nossas exposições em realidade aumentada, realizamos ( uma chamada pública <a href="https://memelab.com.br/jandig/participe/"></a>) para reunir obras para nosso acervo.""",
            },
            "images": [],
        },
        {
            "post": {
                "id": 10,
                "title": "Apresentação HTML5",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 12,tzinfo=timezone),
                "categories": [noticias_category],
                "body": """Ao usar uma tecnologia inovadora e futurística como é a realidade aumentada, não poderíamos deixar a apresentação para trás e por isso a desenvolvemos em HTML5 a partir de um código fornecido no site HTML5 rocks <a href="https://www.html5rocks.com"></a>. Acesse a apresentação <a href="https://memelab.com.br/jandig/html5/pres2"></a>.""",
            },
            "images": [],
        },
        {
            "post": {
                "id": 11,
                "title": "(no title)",
                "status": "draft",
                "created": datetime.datetime(2011, 11, 25, 18, 54,tzinfo=timezone),
                "categories": [],
                "body": """O projeto Jandig é uma investigação a respeito da intervenção de marcadores para visualização de obras por meio de realidade aumentada sobre o espaço urbano. Trata-se de um projeto colaborativo de arte digital que propõe a criação de uma Zona Autônoma Temporária (TAZ) em cada espaço em que é instalado. Essas TAZes são formadas através de marcadores espalhados por um espaço por artistas e pelo público – que assim torna-se co-criador daquela experiência. Os usuários interagem com marcadores, utilizando dispositivos móveis para abrir janelas no mundo real para visualizar criações digitais (cedidas através de licença Creative Commons).
                        Nossos objetivos
                        O trabalho de pesquisa e desenvolvimento que propomos visa à criação de uma plataforma para viabilizar a realização de exposições itinerantes com o uso de realidade aumentada. Ao longo do laboratório-residência, pretendemos expandir e incrementar o projeto colaborativo Jandig, que já está em andamento sob coordenação do VJ pixel. Como fruto desse processo, propomos realizar uma instalação/intervenção nos dois pólos do intercâmbio proposto neste projeto.
                        A instalação é feita a partir da disposição de diversos marcadores, que utilizam como suporte adesivos, stencil ou carimbos, em diferentes tamanhos, que serão espalhados pelos ambientes onde será montada a intervenção. Esses suportes são também entregues ao público que circulam pelo espaço, de modo que possam fazer interferências locais e que seja possível “viralizar” os marcadores enquanto a exposição estiver disponível, deixando rastros e proporcionando interações entre os participantes/visitantes.
                        Para enxergar através das “janelas” e ver as imagens fabulosas o que elas revelam, o público deverá apontar os dispositivos para os marcadores, para que uma aplicação apropriada faça a leitura dos mesmos. Essa aplicação, também denominada Jandig, será distribuída online para download (haverão QRCodes com o endereço próximos aos marcadores). As obras que serão exibidas nas janelas digitais do Jandig deverão ser selecionadas por meio de uma chamada pública e liberadas em Creative Commons.
                    """,
            },
            "images": [],
        },
        {
            "post": {
                "id": 12,
                "title": "Baixe no Market",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 18, 54,tzinfo=timezone),
                "categories": [noticias_category],
                "body": """O Jandig está agora disponível para download <a href="https://market.android.com/details?id=com.memelab.jandig"></a> no Android Market.""",
            },
            "images": [],
        },
        {
            "post": {
                "id": 13,
                "title": "Colando Jandig",
                "status": "draft",
                "created": datetime.datetime(2011, 12, 12, 15, 46,tzinfo=timezone),
                "categories": [],
                "body": """Nos dias que saímos colando o Jandig por aí. <a href="https://www.flickr.com/photos/58001963@N04/"></a>
            Cola para Lambe-Lambe
            (para paredes e intervenções na cidade)

            Ingredientes:
            7 colheres de sopa de farinha de trigo
            1 litro d'água
            2 colheres de sopa de vinagre
            1 garrafa plástica de 2 litros (refrigerante) com tampa

            Como preparar:

            Pegue 3/4 da água (750ml) e coloque para ferver numa panela grande.
            Misture as 7 colheres de trigo na água restante em outra panela e vá
            mexendo até o trigo se disolver totalmente. Nessa parte é importante
            mexer bem para não ficar "pelotinhas" que podem vir a entupir o
            orifício por onde a colar vai sair.

            Assim que a água ferver jogue o trigo dissolvido e vá mexendo (não
            pare de mexer). Mexa por cinco minutos aproximadamente, até o caldo
            começar a engrossar. Depois adicione as 2 colheres de vinagre (que
            evita o apodrecimento) e mexa por mais 2 minutos. Deixe a cola esfriar
            um pouco (não muito senão ela seca hehe) e utilizando um funil derrame
            ela na garrafa de refri e guarde na geladeira. Não tire ela da
            geladeira, a não ser quando você for usar.

            Dica: Faça um orifício na tampinha da garrafa para derramar a cola e
            ficar mais prático.
            Obs: Essa cola demora um pouco para secar.""",
            },
            "images": [],
        },
        {
            "post": {
                "id": 14,
                "title": "Rota XXI",
                "status": "published",
                "created": datetime.datetime(2012, 4, 20, 17, 26,tzinfo=timezone),
                "categories": [ativas_category, obras_category],
                "body": """<br /><b>Autor do objeto:</b> Rubens Castillo
            <br /><b>Autor do marcador:</b> Gustavo Athayde <a href="https://www.gustha.com"></a>""",
            },
            "images": [
                {"file": "14.1robo-rodas.gif", "description": None},
                {"file": "14.2robo-rodas.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 15,
                "title": "VOLANS",
                "status": "published",
                "created": datetime.datetime(2012, 4, 20, 17, 27,tzinfo=timezone),
                "categories": [ativas_category, obras_category],
                "body": """<br /><b>Autor do objeto:</b> Rubens Castillo
            <br /><b>Autor do marcador:</b> Gustavo Athayde <a href="https://www.gustha.com"></a>""",
            },
            "images": [
                {"file": "15.1peixe_502x301-12fps.gif", "description": None},
                {"file": "15.2peixe.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 16,
                "title": "FORNAX",
                "status": "published",
                "created": datetime.datetime(2012, 4, 20, 17, 28,tzinfo=timezone),
                "categories": [ativas_category, obras_category],
                "body": """<br /><b>Autor do objeto:</b> Rubens Castillo
            <br /><b>Autor do marcador:</b> Gustavo Athayde <a href="https://www.gustha.com"></a>""",
            },
            "images": [
                {"file": "16.1andando.gif", "description": None},
                {"file": "16.2andando.jpg", "description": None},
            ],
        },
        {
            "post": {
                "id": 17,
                "title": "Plan 9",
                "status": "published",
                "created": datetime.datetime(2012, 4, 20, 17, 29,tzinfo=timezone),
                "categories": [ativas_category, obras_category],
                "body": """Descrição do objeto: Fazem 20 anos que olhei pro céu e vi este disco-voador se deslocando calmamente.

            <br /><b>Autor do objeto:</b> Fábio Yamaji
            <br /><b>Autor do marcador:</b> Gustavo Athayde <a href="https://www.gustha.com"></a>""",
            },
            "images": [
                {"file": "17.1FlyingSaucer_320x148-6fps.gif", "description": None},
                {"file": "17.2FlyingSaucer_300x300.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 18,
                "title": "Iemanjá",
                "status": "published",
                "created": datetime.datetime(2017, 4, 20, 15, 44,tzinfo=timezone),
                "categories": [ativas_category, obras_category],
                "body": """Ilustração em homenagem ao 2 de fevereiro, onde em Salvador - BA se comemora o dia de Iemanjá.

            <br /><b>Autor do objeto:</b> Gustavo Athayde <a href="https://www.gustha.com"></a>
            <br /><b>Autor do marcador:</b> Hebert Valois <a href="https://hvalois.umacidade.net"></a>""",
            },
            "images": [{"file": "18.1iemanja_Janela.png", "description": None}],
        },
        {
            "post": {
                "id": 19,
                "title": "Disco Voador",
                "status": "published",
                "created": datetime.datetime(2017, 4, 20, 16, 3,tzinfo=timezone),
                "categories": [ativas_category, obras_category],
                "body": """#whilemyeyes - Go looking for flying saucers in the sky #estamosfudidos

            <br /><b>Autor do objeto:</b> Hernani Dimantas <a href="https://hdimantas.wordpress.com/"></a>
            <br /><b>Autor do marcador:</b> Gustavo Athayde <a href="https://www.gustha.com"></a>""",
            },
            "images": [
                {"file": "19.1whilemyeyes2_200x200-1.gif", "description": None},
                {
                    "file": "19.220170419MarcJandig72DPI_Saucer-1.png",
                    "description": None,
                },
            ],
        },
        {
            "post": {
                "id": 20,
                "title": "Pedrinhazinha",
                "status": "published",
                "created": datetime.datetime(2017, 4, 20, 17, 29,tzinfo=timezone),
                "categories": [ativas_category, obras_category],
                "body": """Pedrinhazinha é uma reflexão bem-humorada sobre a nada animadora situação dos dependentes químicos em situação de rua, oprimidos por um estado violento e uma injusta e obsoleta guerra às drogas. <br />
            <br /><b>Autor do objeto:</b> Hebert Valois <a href="https://hvalois.umacidade.net"></a>
            <br /><b>Autor do marcador:</b> Hebert Valois <a href="https://hvalois.umacidade.net"></a>""",
            },
            "images": [
                {"file": "20.1Pedrinhazinha_240x180.gif", "description": None},
                {"file": "20.2Pedrinhazinha_Janela.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 21,
                "title": "Sexy na Janela",
                "status": "published",
                "created": datetime.datetime(2017, 4, 20, 17, 30,tzinfo=timezone),
                "categories": [ativas_category, obras_category],
                "body": """A animação é a releitura de um projeto adormecido chamado Sexy de 5ª, onde "pin ups" eram postadas todas as quintas-feiras no blog Deu Mole eu Traço. Trabalhos mais recentes podem ser vistos em www.dribble.com/gustha

            <br /><b>Autor do objeto:</b> Gustavo Athayde <a href="https://www.gustha.com"></a>
            <br /><b>Autor do marcador:</b> Gustavo Athayde <a href="https://www.gustha.com"></a>""",
            },
            "images": [
                {"file": "21.1sxy5a-jandig2_265x400.gif", "description": None},
                {"file": "21.2binoculos_Janela.png", "description": None},
            ],
        },
        {
            "post": {
                "id": 22,
                "title": "Política de Privacidade",
                "status": "draft",
                "created": datetime.datetime(2017, 5, 11, 11, 27,tzinfo=timezone),
                "categories": [],
                "body": """Política de Privacidade do Jandig
            Este Aplicativo recolhe alguns Dados Pessoais dos Usuários.
            Resumo da Política de privacidade
            Os Dados Pessoais são coletados para os seguintes propósitos e usando os seguintes serviços:
            Permissões de dispositivos para acesso a Dados Pessoais
            Permissões de dispositivos para acesso a Dados Pessoais
            Dados Pessoais: Permissão de câmera
            Política de privacidade completa
            Controlador de Dados e Proprietário
            Tipos de Dados coletados
            Entre os tipos de Dados Pessoais que este Aplicativo recolhe, por si só ou por meio terceiros, estão:
            Permissão de câmera.
            Outros Dados Pessoais recolhidos podem ser descritos em outras seções desta política de privacidade ou pelo texto explicativo específico apresentado no contexto da coleta de Dados.
            Os Dados Pessoais podem ser livremente fornecidos pelo Usuário, ou coletados automaticamente quando se utiliza este Aplicativo.
            Qualquer uso de Cookies - ou de outras ferramentas de rastreamento - pelo este Aplicativo ou pelos proprietários dos serviços terceirizados utilizados por este Aplicativo, salvo indicação em contrário, servem para identificar os Usuários e lembrar as suas preferências, com o único propósito de fornecer os serviços requeridos pelos Usuários.
            O não fornecimento de determinados Dados Pessoais pode tornar impossível para este Aplicativo prestar os seus serviços.
            O Usuário assume a responsabilidade pelos Dados Pessoais de terceiros publicados ou compartilhados por meio deste serviço (este Aplicativo) e confirma que tem o consentimento da parte terceira para fornecer Dados para o Proprietário.
            Modo e local de processamento dos Dados
            Método de processamento
            O Controlador de Dados processa os dados de Usuários de forma adequada e tomará as medidas de segurança adequadas para impedir o acesso não autorizado, divulgação, alteração ou destruição não autorizada dos Dados.
            O processamento de dados é realizado utilizando computadores e /ou ferramentas de TI habilitadas, seguindo procedimentos organizacionais e meios estritamente relacionados com os fins indicados. Além do Controlador de Dados, em alguns casos, os Dados podem ser acessados por certos tipos de pessoas envolvidas com a operação do site (administração, vendas, marketing, administração legal do sistema) ou pessoas externas (como fornecedores terceirizados de serviços técnicos, carteiros, provedores de hospedagem, empresas de TI, agências de comunicação) nomeadas, quando necessário, como Processadores de Dados por parte do Proprietário. A lista atualizada destas partes pode ser solicitada a partir do Controlador de Dados a qualquer momento.
            Lugar
            Os dados são processados nas sedes de operação do Controlador de Dados, e em quaisquer outros lugares onde as partes envolvidas com o processamento estejam localizadas. Para mais informações, por favor entre em contato com o Controlador de Dados.
            Período de conservação
            Os Dados são mantidos pelo período necessário para prestar o serviço solicitado pelo Usuário, ou pelos fins descritos neste documento, e o Usuário pode solicitar o Controlador de Dados para que os suspenda ou remova.
            O Uso dos Dados coletados
            Os Dados relativos ao Usuário são coletados para permitir que o Proprietário forneça os serviços, bem como para os seguintes propósitos:
            Permissões de dispositivos para acesso a Dados Pessoais.
            Os Dados Pessoais utilizados para cada finalidade estão descrito nas seções específicas deste documento.
            Permissões de dispositivos para acesso a Dados Pessoais
            Este Aplicativo solicita determinadas permissões dos Usuário que lhe permitem acessar os Dados do dispositivo do Usuário conforme descritos abaixo.
            Por padrão estas permissões devem ser concedidas pelo Usuário antes que as respectivas informações possam ser acessadas. Uma vez que a permissão tenha sido dada, esta pode ser revogada pelo Usuário a qualquer momento. Para poder revogar estas permissões os Usuários devem consultar as configurações do dispositivo ou entrar em contato com o Proprietário para receber suporte através dos dados para contato fornecidos no presente documento.
            O procedimento exato para controlar as permissões de aplicativos poderá depender dos dispositivo e software do Usuário.
            Por favor observar que a revogação de tais permissões poderá afetar o funcionamento apropriado do este Aplicativo
            Se o Usuário conceder quaisquer das permissões relacionadas abaixo, estes Dados Pessoais respectivos poderão ser processados (isto é, acessados, modificados ou removidos) por este Aplicativo.
            Permissão de câmera
            Usada para acessar a câmera ou capturar imagens e vídeo do dispositivo.
            Informações detalhadas sobre o processamento de Dados Pessoais
            Os Dados Pessoais são recolhidos para os seguintes fins e utilizando os seguintes serviços:
            Permissões de dispositivos para acesso a Dados Pessoais
            Informações adicionais sobre a coleta e processamento de Dados
            Ação jurídica
            Os Dados Pessoais dos Usuários podem ser utilizados para fins jurídicos pelo Controlador de Dados em juízo ou nas etapas conducentes à possível ação jurídica decorrente de uso indevido deste serviço (este Aplicativo) ou dos serviços relacionados.
            O Usuário declara estar ciente de que o Controlador dos Dados poderá ser obrigado a revelar os Dados Pessoais mediante solicitação das autoridades governamentais.
            Informações adicionais sobre os Dados Pessoais do Usuário
            Além das informações contidas nesta política de privacidade, este Aplicativo poderá fornecer ao Usuário informações adicionais e contextuais sobre os serviços específicos ou a coleta e processamento de Dados Pessoais mediante solicitação.
            Logs do sistema e manutenção
            Para fins de operação e manutenção, este Aplicativo e quaisquer serviços de terceiros poderão coletar arquivos que gravam a interação com este Aplicativo (Logs do sistema) ou usar, para este fim, outros Dados Pessoais (tais como endereço IP).
            As informações não contidas nesta política
            Mais detalhes sobre a coleta ou processamento de Dados Pessoais podem ser solicitados ao Controlador de Dados, a qualquer momento. Favor ver as informações de contato no início deste documento.
            Os direitos dos Usuários
            Os Usuários têm o direito de, a qualquer tempo, consultar o Controlador de Dados para saber se os seus Dados Pessoais foram armazenados e saber mais sobre o conteúdo e origem, verificar a sua exatidão ou para pedir que sejam complementados, cancelados, atualizados ou corrigidos, ou que sejam transformados em formato anônimo ou bloquear quaisquer dados mantidos em violação da lei, bem como se opor ao seu tratamento por quaisquer todas as razões legítimas. Os pedidos devem ser enviados para o Controlador de Dados usando a informação de contato fornecida acima.
            Este Aplicativo não suporta pedidos de “Não Me Rastreie”.
            Para determinar se qualquer um dos serviços de terceiros que utiliza honram solicitações de “Não Me Rastreie”, por favor leia as políticas de privacidade.
            Mudanças nesta política de privacidade
            O Controlador de Dados se reserva o direito de fazer alterações nesta política de privacidade a qualquer momento, mediante comunicação aos seus Usuários nesta página. É altamente recomendável que esta página seja consultada várias vezes em relação à última modificação descrita na parte inferior. Se o Usuário não concorda com qualquer das alterações da Política de Privacidade, o Usuário deve cessar o uso deste serviço (este Aplicativo) e pode solicitar ao Controlador de Dados que apague os Dados Pessoais. Salvo disposição em contrário, a atual política de privacidade se aplica a todos os Dados Pessoais dos Usuários que o Controlador de Dados tiver.
            Informações sobre esta política de privacidade
            O Controlador de Dados é responsável por esta política de privacidade, elaborada a partir dos módulos fornecidos pela Iubenda e hospedados nos servidores da Iubenda.
            Definições e referências jurídicas

            Última atualização: 11 de maio de 2017""",
            },
            "images": [],
        },
        {
            "post": {
                "id": 23,
                "title": "Temaki",
                "status": "draft",
                "created": datetime.datetime(2018, 4, 9, 21, 54,tzinfo=timezone),
                "categories": [],
                "body": "",
            },
            "images": [
                {"file": "23.1VID_30770613_164918_460.mp4", "description": None}
            ],
        },
        {
            "post": {
                "id": 24,
                "title": "Making Of",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 0,tzinfo=timezone),
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
                "id": 25,
                "title": "Urban Interventions",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 1,tzinfo=timezone),
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
                "id": 26,
                "title": "Ônibus Hacker",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 2,tzinfo=timezone),
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
                "id": 27,
                "title": "CulturaDigital.br Festival",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 3,tzinfo=timezone),
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
                "id": 28,
                "title": "Campus Party Brazil",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 4,tzinfo=timezone),
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
                "id": 29,
                "title": "AiR – Mobile Media Art",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 5,tzinfo=timezone),
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
                "id": 30,
                "title": "BaixoCentro Festival",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 6,tzinfo=timezone),
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
                "id": 31,
                "title": "Algo a Mais?",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 7,tzinfo=timezone),
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
                "id": 32,
                "title": "FISL",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 8,tzinfo=timezone),
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
                "id": 33,
                "title": "Janelas Digitais",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 9,tzinfo=timezone),
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
                "id": 34,
                "title": "Virada Cultural",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 10,tzinfo=timezone),
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
                "id": 35,
                "title": "GAS Station",
                "status": "published",
                "created": datetime.datetime(2011, 11, 25, 17, 11,tzinfo=timezone),
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

    Post.objects.filter(id__in=range(0, 36)).delete()
    PostImage.objects.filter(id__in=range(0, 50)).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_posts, reverse_code=remove_initial_posts),
    ]
