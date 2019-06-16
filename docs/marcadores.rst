Dicas para produzir marcadores
==============================

Esse documento contém orientações técnicas, estéticas e boas práticas
para a produção de marcadores de realidade aumentada Jandig.

Bordas
------

As bordas são os elementos gráficos que engatilham o reconhecimento do
objeto associado a cada marcador. Por esse motivo, não se deve cobri-las
e elas devem sempre ser vistas completamente pela câmera. Colocar o dedo
sobre uma das bordas ou aproximar demais a câmera do marcador
inviabiliza o reconhecimento, por exemplo. Essa característica deve
sempre ser levada em consideração na produção e aplicação dos
marcadores.

Utilizamos, por padrão, 20% de largura de borda nos marcadores Jandig.
Ou seja, para um marcador com 10 centímetros de largura, teremos uma
borda de 2 cm de largura.

A imagem central do marcador não deve tocar as bordas. A distância
mínima dessa imagem para a margem interna da borda deve ser de 2% da
largura total do marcador.

Embora pequenas massas de texto (nome da exposição, url do app) possam
ser aplicadas sobre a borda sem prejuízo ao reconhecimento da obra, é
recomendado que a altura deste texto jamais ultrapasse ¼ da largura
total da borda.

[inserir imagem de marcador]

Simetria
~~~~~~~~

Considerando que a visualização do objeto depende da posição do marcador
em relação à câmera, evitamos utilizar imagens com simetria tanto no
eixo vertical quanto no horizontal. Esta prática visa evitar que o
sistema de reconhecimento se confunda quanto à orientação em que deve
exibir a imagem.

Cores e gradientes
~~~~~~~~~~~~~~~~~~

Para garantir maior fidelidade tanto no reconhecimento pelo sistema,
quanto nas infinitas possibilidades de aplicação dos marcadores, não
utilizamos cores ou gradientes nas imagens centrais. A única cor
utilizada é preto 100%, sem a utilização de tons.

Impressão e afins
~~~~~~~~~~~~~~~~~

Reflexos, inclusive sobre as bordas, podem impedir que os seus
marcadores sejam reconhecidos como tal. Para que sejam mais facilmente
identificados pelo sistema, devem-se utilizar tintas e materiais opacos
na sua produção.

É importante que as margens externas e internas da borda estejam sempre
bem delimitadas. No caso de adesivos ou de aplicação em fundo mais
escuros, garanta uma margem branca ao redor borda preta. Essa reserva de
espaço deve ter, ao menos, 3% da largura total do marcador (ver imagem).

Iluminação
----------

A qualidade e a cor da iluminação do ambiente podem influenciar na
leitura dos marcadores. Para uma boa visualização, prefira uma
iluminação distribuída, que não gere reflexos e evite utilizar
iluminação de coloração muito âmbar.

Adesivos
~~~~~~~~

Embora marcadores consigam ser reconhecidos até em formatos muito
pequenos, costumamos produzir adesivos de marcadores Jandig com 5 x 5
cm. Essa dimensão associa bom rendimento com boa legibilidade de todos
os elementos, inclusive texto.
