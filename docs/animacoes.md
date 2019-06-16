# Dicas para produzir animações
Esse documento contém orientações técnicas e boas práticas para a produção de animações em realidade aumentada para o Jandig. Muitas dessas orientações podem ser utilizadas para produzir conteúdo para outras plataformas.

Além de produzir uma versão considerando as limitações a seguir, recomendamos que seja produzida uma versão “ideal”, que pode ser utilizada em ambientes controlados e/ou no futuro (quanto essas limitações vão diminuir).

### Formato de arquivo
Atualmente, o único formato de arquivo suportado é GIF.

### Detalhes
Utilize o mínimo de detalhes e de elementos pequenos que for possível, pois eles podem não ser identificados pelo público.

Uma maneira de testar aqui é salvar as imagens do storyboard em 300x300px e ver se é possível identificar todos os elementos. É importante lembrar que o público pode ver a animação à distância, de modo que ela fique bem pequena na tela do telefone.

### Quantidade de cores
A recomendação é diminuir o máximo possível, de maneira a não comprometer as cores originais.

Para otimizar esses valores, recomendamos minimizar o uso de degradês e evitar transições em fade.

Uma técnica para planejar esse uso antes de produzir a animação, é exportar as imagens do storyboard em GIF com diferentes quantidades de cores.

### Resolução
Para aumentar a compatibilidade de dispositivos, limitamos a resolução do quadro de exibição (que aparece em tela cheia no smartphone) em 640x480 pixels. Como a animação só vai aparecer em um trecho desse quadro, recomendamos a criação do conteúdo em 300x300px.

Caso haja um problema na visualização de detalhes, pode-se chegar até a 400x400px, mas atualmente o ganho de uma resolução maior é quase imperceptível (enquanto onera bastante o tamanho do arquivo).

### Framerate
A taxa de frames (medida em frames por segundo, ou quadros por segundo) recomendada é de, no máximo, 12 fps.

### Loop
Para criar a ilusão de continuidade, a animação deve estar em loop. Ou seja, a transição do último ao primeiro frame deve ser imperceptível.

### Tempo

Quanto mais curta a animação, melhor. Isso vai permitir melhor qualidade de imagens e garantir que o público assista todo o material. Até o momento, a animação mais longa feita para o Jandig tem aproximadamente 20 segundos. A recomendação é que tenha até 15 segundos.

### Tamanho de arquivo

Enquanto os parâmetros a seguir têm flexibilidade quanto às orientações, esse é o mais rígido. Os arquivos devem ter idealmente até 500 kB e no máximo com 1 MB. Esse é um fator decisivo na escolha de obras a serem incluídas em uma exposição, quanto menor, melhor.

Essa limitação existe principalmente pelas seguintes razões:
- Não temos controle da velocidade de conexão do público quando acessar o conteúdo, o que pode fazer com que o download de todas as obras demore.
- Não queremos onerar o plano de dados do público.
- Arquivos menores são mais leves necessitam de menor quantidade de processamento, tornando a plataforma compatível com um maior número de telefones.

### Conclusão

Para se chegar a um resultado ótimo o ideal é testar os parâmetros em conjunto.

Um processo recomendado é exportar com limitando ao máximo os parâmetros (8 cores, 200x200px, 5 fps) e com também com as recomendações mínimas de limitação (256 cores, 300x300px, 12 fps) e comparar.

A partir daí, modificar com parâmetro por vez a partir das limitações mínimas, reduzindo só o framerate/resolução/cores para ver qual o mínimo que funciona bem.

Se, após reduzir os 3 ao mínimo que funciona bem o arquivo ainda estiver grande, continuar diminuindo os parâmetros em combinações diferentes para até chegar a um resultado ótimo.
Lembre-se também de manter a versão em alta resolução. Aqui a recomendação é salvar com 1000x1000px e 24 fps.

Caso você use Adobe Media encoder, há um tutorial que foi desenvolvido pela UEMG para [download em PDF](https://github.com/memeLab/ARte/blob/develop/docs/Tutorial%20de%20Exporta%C3%A7%C3%A3o%20em%20GIF.pdf).
