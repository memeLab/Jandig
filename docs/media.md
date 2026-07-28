# Dicas para produzir mídia

Este documento contém orientações técnicas e boas práticas para a
produção de mídia (imagens, animações, vídeos e modelos 3D) usada em
Obras de realidade aumentada e mista na Jandig. Muitas dessas
orientações também podem ser úteis para produzir conteúdo para outras
plataformas.

Além de produzir uma versão considerando as limitações a seguir,
recomendamos que seja produzida uma versão "ideal", em maior qualidade,
que pode ser utilizada em ambientes controlados e/ou no futuro (quanto
essas limitações forem diminuindo).

## Formatos suportados

Ao enviar um Objeto, os formatos aceitos atualmente são:

- **GIF** — animações simples, com boa compatibilidade.
- **PNG** — imagem estática (sem animação).
- **MP4** e **WebM** — vídeos, incluindo suporte a transparência no
  WebM. Recomendado para animações mais longas ou com mais detalhe, já
  que vídeo comprime muito melhor que GIF.
- **GLB** — modelo 3D. **Disponível apenas para Exposições MR** (o
  aplicativo de Realidade Mista para Meta Quest). Obras AR (o app
  mobile, baseado em Marcadores) não aceitam Objetos em GLB.

Também é possível anexar uma **audiodescrição** opcional ao Objeto, nos
formatos MP3, OGG ou WAV, para tornar a Obra mais acessível.

## Detalhes

Utilize o mínimo de detalhes e de elementos pequenos que for possível,
pois eles podem não ser identificados pelo público.

Uma maneira de testar aqui é salvar as imagens do storyboard em
300x300px e ver se é possível identificar todos os elementos. É
importante lembrar que o público pode ver o conteúdo à distância, de
modo que ele fique bem pequeno na tela do telefone.

## Quantidade de cores (GIF)

A recomendação é diminuir o máximo possível, de maneira a não
comprometer as cores originais.

Para otimizar esses valores, recomendamos minimizar o uso de degradês e
evitar transições em fade.

Uma técnica para planejar esse uso antes de produzir a animação, é
exportar as imagens do storyboard em GIF com diferentes quantidades de
cores.

## Resolução

Como o conteúdo é majoritariamente visualizado em telas de smartphone, e
muitas vezes à distância, recomendamos criar o conteúdo em torno de
300x300px a 400x400px. Resoluções maiores que isso raramente trazem
ganho perceptível de qualidade no dispositivo, mas aumentam bastante o
tamanho do arquivo e o tempo de carregamento.

Para modelos GLB (exclusivos de Exposições MR no Meta Quest), a
resolução relevante é a das texturas do modelo — prefira texturas
otimizadas e comprimidas em vez de texturas em altíssima resolução.

## Framerate (GIF e vídeo)

Não existe um número fixo ideal — o recomendado é testar e usar a menor
taxa de quadros que ainda pareça fluida para a animação em questão.
Taxas de quadros mais baixas reduzem o tamanho do arquivo e o tempo de
carregamento, então vale a pena reduzir gradualmente até perceber que a
qualidade começa a ficar comprometida.

## Loop

Para criar a ilusão de continuidade, a animação (GIF ou vídeo) deve
estar em loop. Ou seja, a transição do último ao primeiro frame deve ser
imperceptível.

## Tempo de duração

Quanto mais curto o conteúdo, melhor. Isso permite melhor qualidade de
imagem e garante que o público assista a todo o material. Recomendamos
até 15 segundos de duração para animações e vídeos.

## Tamanho de arquivo

Este é o parâmetro mais rígido: arquivos menores carregam mais rápido e
consomem menos dados móveis do público. Como referência (quanto menor,
melhor):

- **GIF**: ideal até 500 kB, no máximo 1 MB.
- **MP4 / WebM**: por comprimir melhor que GIF, é possível manter boa
  qualidade com arquivos de até 1-2 MB para clipes curtos em loop.
- **PNG**: ideal até 300 kB, já que é uma imagem estática.
- **GLB**: como é usado no app do Meta Quest (geralmente em Wi-Fi),
  dados móveis pesam menos, mas o desempenho do dispositivo continua
  importando — prefira modelos otimizados (poucos polígonos, texturas
  comprimidas).

Essa limitação existe principalmente pelas seguintes razões:

- Não temos controle da velocidade de conexão do público quando acessar
  o conteúdo, o que pode fazer com que o download de todas as Obras
  demore.
- Não queremos onerar o plano de dados do público.
- Arquivos menores necessitam de menor quantidade de processamento,
  tornando a plataforma compatível com um maior número de dispositivos.

## Conclusão

Para chegar a um resultado ótimo, o ideal é testar os parâmetros em
conjunto (resolução, cores, framerate e duração).

Um processo recomendado é exportar com os parâmetros bem reduzidos (por
exemplo, poucas cores, resolução baixa, framerate baixo) e também com
uma versão de qualidade mais alta, e comparar. A partir daí, ajuste um
parâmetro por vez, reduzindo até perceber o ponto em que a qualidade
começa a ficar comprometida.

Se, mesmo depois de reduzir todos os parâmetros para o mínimo aceitável,
o arquivo ainda estiver grande, continue ajustando em combinações
diferentes até chegar a um resultado ótimo. Lembre-se também de manter
uma versão em alta resolução para uso em ambientes controlados e/ou
futuro.

Caso você use Adobe Media Encoder, há um tutorial que foi desenvolvido
pela UEMG para [download em
PDF](https://github.com/memeLab/ARte/blob/develop/docs/Tutorial%20de%20Exporta%C3%A7%C3%A3o%20em%20GIF.pdf).
