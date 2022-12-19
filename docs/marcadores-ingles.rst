Hints to produce Tags
==============================

This document contains tecnical, aesthetics and good practices guidelines to the production of Tags of augmented reality Jandig.

Borders
------

The borders are grafic elements that trigger the recognition of the object associated with each tag. For this reason, one should not cover them and them must always be 
seen completely by the camera. Put the finger over the border or approach the camera too close to the tag will derail the recognition, for example. This feature should 
be always taken into account in the production and application of the tags.

We use by default 20% of width from the border in the Jandig tags, that is in a tag with 10 centimeters of width, we will have a border of 2 centimeters of width.

The central image of the Tag should not touch the borders. The minimum distance of the imagen to the internal margin of the border should be 2% of the total width of 
the Tag.

Although little texts (exhibition name, app url)  can be applied over the border without prejudice in the recognition, is recomended the height of the text never 
overtake the total porcentage of the border.

.. image:: images/MarkerGuide.png
    :width: 320px
    :align: center

Symmetry
--------

Considering that the visualization of the object depends on the position of the Tag in relation of the camera, we avoid using images with symmetry vertical as well as 
horizantal. This rule aim avoid that the recognition system get confused about which orientation it must show the image.

Cores e gradientes
------------------

Para garantir infinitas possibilidades de aplicação dos marcadores, não
utilizamos cores ou gradientes nas imagens centrais. A única cor
utilizada é preto 100%, sem a utilização de tons.

Essa não é uma limitação do sistema. É possível utilizar qualquer imagem
como marcador, seguindo as outras recomendações nesse documento.

Impressão e afins
-----------------

Reflexos, inclusive sobre as bordas, podem impedir que os seus
marcadores sejam reconhecidos como tal. Para que sejam mais facilmente
identificados pelo sistema, devem-se utilizar tintas e materiais opacos
na sua produção.

É importante que as margens externas e internas da borda estejam sempre
bem delimitadas. No caso de adesivos ou de aplicação em fundo mais
escuros, garanta uma margem branca ao redor borda preta. Essa reserva de
espaço deve ter, ao menos, 3% da largura total do marcador.

Iluminação
----------

A qualidade e a cor da iluminação do ambiente podem influenciar na
leitura dos marcadores. Para uma boa visualização, prefira uma
iluminação distribuída, que não gere reflexos e evite utilizar
iluminação de coloração muito âmbar.

Adesivos
--------

Embora marcadores consigam ser reconhecidos até em formatos muito
pequenos, costumamos produzir adesivos de marcadores Jandig com 5 x 5
cm. Essa dimensão associa bom rendimento com boa legibilidade de todos
os elementos, inclusive texto.
