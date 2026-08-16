# Dicas para produzir marcadores

Esse documento contém orientações técnicas, estéticas e boas práticas
para a produção de marcadores de realidade aumentada Jandig.

Você não precisa criar um arquivo de marcador com bordas, margens ou
espessuras específicas. Basta enviar qualquer imagem (PNG ou JPG) na
página de upload de Marcador que a Jandig adiciona automaticamente a
borda preta necessária para o reconhecimento, e você já vê uma prévia do
resultado antes de salvar.

## Bordas

As bordas são os elementos gráficos que engatilham o reconhecimento do
objeto associado a cada marcador. Por esse motivo, não se deve cobri-las
e elas devem sempre ser vistas completamente pela câmera. Colocar o dedo
sobre uma das bordas ou aproximar demais a câmera do marcador
inviabiliza o reconhecimento, por exemplo. Essa característica deve
sempre ser levada em consideração na aplicação dos marcadores.

A borda preta é adicionada automaticamente pela plataforma ao redor da
imagem que você enviar, então não é preciso desenhá-la, medi-la ou
deixar margem para ela na sua imagem original.

Se a sua imagem tiver bordas escuras ou com baixo contraste em relação
ao preto, marque a opção "Adicionar borda interna" ao enviar o
marcador: ela insere um fino anel branco entre a imagem e a borda
preta, facilitando a identificação do limite entre os dois pela câmera.

## Formato quadrado

Os marcadores Jandig são sempre quadrados. Se você enviar uma imagem
retangular, ela será redimensionada para caber num quadrado, o que pode
distorcer o conteúdo (esticando-o na horizontal ou na vertical). Para
evitar distorções, prefira usar imagens já quadradas (largura igual à
altura).

## Simetria

Considerando que a visualização do objeto depende da posição do marcador
em relação à câmera, evitamos utilizar imagens com simetria tanto no
eixo vertical quanto no horizontal. Esta prática visa evitar que o
sistema de reconhecimento se confunda quanto à orientação em que deve
exibir a imagem.

## Cores e gradientes

Imagens coloridas e com gradientes são totalmente suportadas: o
reconhecimento compara a imagem central em cores, não apenas em preto e
branco. Para um reconhecimento mais confiável, procure manter um bom
contraste entre as cores da sua imagem e a borda preta ao redor dela.

## Impressão e afins

Reflexos, inclusive sobre as bordas, podem impedir que os seus
marcadores sejam reconhecidos como tal. Para que sejam mais facilmente
identificados pelo sistema, devem-se utilizar tintas e materiais opacos
na sua produção.

Ao baixar o marcador para impressão (versão "print"), ele já vem com uma
margem branca de segurança ao redor da borda preta, pronta para adesivos
ou aplicação sobre fundos escuros — não é necessário adicionar essa
margem manualmente.

## Iluminação

A qualidade e a cor da iluminação do ambiente podem influenciar na
leitura dos marcadores. Para uma boa visualização, prefira uma
iluminação distribuída, que não gere reflexos e evite utilizar
iluminação de coloração muito âmbar.

## Adesivos

Embora marcadores consigam ser reconhecidos até em formatos muito
pequenos, costumamos produzir adesivos de marcadores Jandig com 5 x 5
cm. Essa dimensão associa bom rendimento com boa legibilidade de todos
os elementos, inclusive texto.
