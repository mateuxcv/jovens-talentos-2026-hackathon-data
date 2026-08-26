# Estratégia para o Hackathon Seazone

## Você

Quero que você me ajude a pensar na solução para esse desafio da Seazone, o desafio esta aqui https://github.com/seazonetech/jovens-talentos-202é-hackathon-data e a documentação esta aqui https://seazone-tech.github.io/jovens-talentos-202é-hackathon-data/ eu quero que primeiro você entenda realmente o desafio, os dados que eles disponibilizaram e principalmente o que eles estão esperando como entrega, não quero que você resolva o desafio ainda porque eu quero usar essa conversa como parte do meu processo de construção da solução, então quero que você me ajude a desenvolver a ideia e explorar as possibilidades comigo, sem simplesmente assumir que tudo que eu falar esta certo. Uma ideia que eu comecei a pensar é criar uma espécie de Mesa de Convicção para transformar a análise dos dados em uma experiência de decisão de investimento. A ideia ainda esta bem inicial, seria uma aplicação web onde diferentes agentes especializados analisariam o mesmo conjunto de evidências mas com perspectivas diferentes, pensei inicialmente em um Analista de Mercado que tentaria identificar os melhores perfis e localizações, um Analista de Aquisição que cruzaria isso com Os precos dos imóveis a venda e tentaria entender o retorno, um Auditor Cético que teria justamente a função de tentar encontrar problemas nas conclusões como outliers, amostras pequenas, vieses ou premissas frágeis e por fim um Lider de Investimento que receberia esses pareceres e tomaria a decisão final. Eu imaginei que isso poderia acontecer em algumas rodadas, primeiro cada agente constrdi seu parecer de forma independente, depois existe uma etapa de contesta¢ao e por fim uma decisão consólidada. Mas uma coisa que eu considero importante é que eu não quero fazer aqueles agentes que simplesmente ficam conversando entre si sO para parecer que existe uma arquitetura de agentes. Eu gostaria que os calculos fossem feitos deterministicamente em Python e que os agentes trabalhassem principalmente em cima das evidências produzidas pelos dados, então interpretar, questionar, comparar hipóteses e chegar em uma recomendação, mas o numero em si não deveria ser inventado pelo LLM. Também pensei que o resultado final poderia ir além de simplesmente dizer compre X. Gostaria que a aplicação pudesse mostrar a tese de investimento, as evidências que sustentam a tese, os argumentos contrarios, o nivel de confianga, uma shortlist de imóveis do VivaReal e principalmente em quais condições a recomendação mudaria. Por exemplo, se a análise indicar que studios ou apartamentos de um quarto no Centro são a melhor oportunidade, eu gostaria que o sistema também conseguisse mostrar algo como essa recomendação deixa de ser a melhor opção se o preço de aquisi¢ao aumentar determinado percentual, se a receita projetada cair ou se outra região superar determinado retorno, mas eu não quero inventar esses números, isso teria que ser calculado a partir dos dados e de premissas explicitamente definidas. Outra coisa que eu estou considerando é que a Seazone aparentemente tem uma ambigao maior de internacionalizacao, então talvez a propria arquitetura da ideia pudesse ser pensada como algo que não fica preso a Itapema, Itapema seria o primeiro mercado analisado mas o sistema poderia futuramente receber outros mercados e aplicar o mesmo processo de decisão. Eu não quero inventar conclusões sobre mercados internacionais sem dados, mas talvez exista uma maneira interessante de mostrar essa capacidade futura. Só que eu ainda não sei se essa é uma boa ideia. Pode ser que eu esteja criando complexidade desnecessaria, que agentes não façam sentido, que CrewAl seja exagero ou que exista uma forma muito mais interessante de transformar essa ideia em uma entrega. Quero que você me ajude a avaliar essas possibilidades e pensar em qual seria a melhor forma de transformar isso em um produto final para a Seazone. Não quero elogios automaticos nem quero que você simplesmente concorde comigo. Se existir uma versão melhor da ideia, quero que você proponha e explique por qué. Principalmente quero descobrir qual deveria ser o produto final que eu entregaria para a Seazone e não apenas qual código eu deveria escrever. Quero que você pense em como tornar a ideia realmente diferenciada, como evitar que pareca apenas agentes encenando uma conversa, qual seria o verdadeiro valor de negocio, qual poderia ser o grande momento de impacto da demonstra¢ao, o que deveria ser calculado por código e o que poderia ser feito por IA, se CrewAl realmente agrega alguma coisa, como transformar a contestacao dos agentes em algo baseado em evidências, como apresentara recomendação final e como fazer tudo isso caber realisticamente no tempo do desafio. Também quero que você considere que o desafio pede uma recomendação de investimento para Itapema e deixa algumas coisas propositalmente abertas para avaliar como o candidato pensa e toma uma decisão. Entao eu não quero que você simplesmente tente encontrar uma resposta qualquer nos dados, quero construir uma metodologia defensavel. E eu também quero levar em consideragao que eles pedem o histórico das conversas com IA no ai-log, então nosso processo precisa mostrar iteracao, exploragao e tomada de decisão e não apenas o resultado final. Não quero que você comece escrevendo código agora e também não quero que você monte a solução completa agora. Primeiro quero discutir a ideia, o produto e a estratégia da entrega. Comeca entendendo profundamente o desafio e depois me ajude a avaliar a ideia atual, o que vale manter, o que vale mudar e o que provavelmente não vale a pena, e depois a gente vai refinando até chegar em uma definição muito clara de qual é o produto que eu quero entregar. 
## IA

Essa é uma análise estratégica de alto nivel sobre o seu desafio, a sua ideia da Mesa de Convicção e como transformar tudo isso em uma entrega extraordinaria no hackathon da Seazone. 

#### 1. Entendimento Profundo do Desafio e da Avaliagao 

Primeiro, vamos olhar para o que a Seazone realmente esta medindo: 

- e Não é um teste de software puro / codificagao complexa: O prompt oficial diz explicitamente: "Não é um teste de programagao. Você não precisa ser dev. Precisa pensar bem e usar IA como ferramenta de trabalho." 

- ¢ Os Critérios de Avaliagao: 

   1. Raciocinio e qualidade da análise (45%): Defesa da tese de investimento, critérios de decisão sólidos, clareza sobre o ROle posição fundamentada sobre a tese preliminar interna (se a aposta de compactos no Centro se sustenta ou não). 

   2. Uso de IA/ ai-log (30%): Senso critico com a IA, iteração, questionamento do que a IA gera, validagao dos resultados. 

   3. Comúnicagao / Video de 3 minutos (25%): Sintese, clareza executiva e defesa da decisão. 

- ¢ Otempo disponivel: E um hackathon de 1 dia (das 09h as 09h do dia seguinte). 

#### 2. Avaliagao Critica da sua Ideia: "Mesa de Convicção" 

Sua ideia de uma Mesa de Convicção com multiplos agentes (Analista de Mercado, Analista de Aquisi¢ao, Auditor Cético e Lider de Investimento) é brilhante no conceito, mas carrega armadilhas perigosas de execução se não for desenhada com o escopo correto. 

##### O que é EXCELENTE na sua ideia (Valores a manter) 

1. O Auditor Cético: Esta é a virada de chave mais forte do seu projeto. A maioria dos candidatos vai rodar um código, aceitar os dados limpos ou com ruido, plotar um grafico e dizer "comprem studios no Centro". Criar uma persona/camada analitica focada em estressar as premissas, buscar viés de amostragem, identificar receitas inflacionadas por pouca amostra e desafiar a tese atende perfeitamente ao que a Seazone quer (senso critico). 

2. Análise de Sensibilidade e Ponto de Ruptura (Stress -t esting): A sua ideia de mostrar "Essa recomendag¢ao deixa de ser a melhor se o preço subir X% ou a receita cair Y%" é ouro puro para tomada de decisão imobiliaria real. Isso eleva a entrega de um trabalho escolar para um relatório de investimento de nivel de Private Equity. 

3. Métricas Deterministicas em Python: LLMs são péssimas calculadoras e inventam números com facilidade. Fazer a matemática pesada (mediana de diária, taxa de ocupacgao estimada, cap rate, preço/m², ROI) via scripts Python deterministicos e usar a IA apenas para sintetizar, questionar e ponderar sobre essas evidências exatas é a arquitetura técnica correta. 

##### O que é PERIGOSO ou pode te prejudicar (O que vale adaptar/simplificar) 

1. Aarmadilha do CrewAl / Agentes conversando sozinhos: 

- Problema: Frameworks como CrewAl ou Autogen frequentemente entram em loops de conversas genéricas, gastam tokens, demoram para executar e produzem relatórios prolixos cheios de "fluff" (falar muito sem dizer nada). 

- © Visão dos avaliadores: Se a Seazone vir um log de agentes trocando elogios ou frases genéricas de mercado, a impressão sera de "teatro de IA" e falta de substancia. 

- Solugao: Em vez de uma simulação assincrona de conversa entre LLMs, use Pipelines de Prompting Estruturado ou Multi - Agent Chain sequencial. Cada agente tem um papel estrito sobre uma tabela de fatos calculada via Python: 

   - = Passo 1 (Python): Gera a Tabela Fato de Métricas Fin/Imobiliarias por Bairro/Tipologia e Shortlist do VivaReal. 

   - = Passo 2 (Agente 1 - Mercado): Interpreta demanda e receita potencial. 

   - = Passo 3 (Agente 2 - Aquisi¢ao): Cruza com cap rate e preço de compra do VivaReal. 

   - = Passo 4 (Agente 3 - Auditor Cético): Desafia as duas visões anteriores apontando fragilidades dos dados (ex: pouca amostragem em determinado bairro, sazonalidade não ajustada). 

   - = Passo 5 (Agente 4 - Lider de Investimento): Harmoniza o debate, aplica a matriz de risco e solta a tese final + condigdes de invalidação. 

###### 2. Internacionalizagao / Expans@o para outros mercados: 

- Cuidado: Se você investir tempo tentando deixar a ferramenta genérica para aceitar "qualquer cidade do mundo", corre o risco de não aprofundar na análise real de Itapema (que vale 45% da nota). 

- Como apresentar sem gastar escopo: Apresente a arquitetura como Engine de Decisão Agnostica a Mercado. Mostre no código/UI que os dados de entrada entram em um schema padronizado (Data Pipeline), e que Itapema é o Market #01. Mencione essa modularidade no relatório e no video de 3 minutos como um diferencial de produto ("pronto para escala nacional/internacional"). 

### 3. O Produto Final Perfeito para a Seazone 

Em vez de entregar apenas um dashboard comum ou um código Jupyter Notebook, o seu produto final deve ser: 

### "Seazone Investment Decision Engine (IDE) — Mesa de Convicção" 

Uma aplicação web interativa (feita em Streamlit ou Reflex/Gradio, simples de rodar com pip install ou docker) acompanhada por um Relatorio Executivo Tese de Investimento em Markdown no repositório. 

##### Como a experiência do usuário/avaliador funcionaria na App: 

- 1. Painel de Premissas de Investimento (Entradas Deterministicas): 

   - eo O usuário (Lider da Seazone) ajusta varidveis de negócio (ex: Custo de Financiamento/WACC, Taxa de Vacância Esperada, Custo de Gestão Seazone, Desconto Médio em Negociagao VivaReal). 

2. O Painel "Mesa de Convicção" (O Coragao da App): 

- Exibe a tese consólidada com abas ou cards claros para cada "Visão de Especialista" (alimentados com m²tricas reais vindas do Python): 

   - <mark>=</mark> |) Tese de Oportunidade (Mercado & Aquisição): Onde estão as maiores assimetrias de retorno em Itapema. 

   - = Q Auditoria de Riscos & Ceticismo: Alertas automaticos (ex: "Atengao: A alta rentabilidade calculada para o bairro Meia Praia em studios é baseada em apenas 4 anúncios no Airbnb — risco de amostragem alto"). 

©<br>

   - = © Fronteira de Ruptura (Stress Test): Grafico interativo ou tabela mostrando: "Se o preço m²dio de aquisi¢ao do m² subir mais de 8.5% no Centro, a tese migra para Meia Praia 2 quartos". 

   - « ® Shortlist VivaReal com Tese de Ativos: Lista filtrada de imdveis reais 4 venda que batem exatamente com o perfil étimo sugerido. 

3. Posicionamento Claro sobre a Tese da Seazone: 
- Um badge destacado: [ TESE INTERNA VALIDADA] ou [ TESE INTERNA REFUTADA] com justificativa quantitativa e qualitativa irrefutavel. 

4. Divisão do Trabalho: O que é Python vs. O que é IA 

|Componente|Responsavel|O que faz exatamente|
|---|---|---|
|Limpeza e Join de Dados|Python (Pandas)|Une Details, Price_AV, Mesh_Ids e VivaReal por geolocalizaçãoe listing.|

|Componente|Responsavel|O que fazexatamente|
|---|---|---|
|Calculo de<br>Receita/Diaria/Ocupação|Python<br>y|Calcula receita anual estimada por imdvel/região/tipologia (ex: medianade<br>precos no Price_AV, percentual de dias ocupados).|
|P<br>Calculo de ROI /Cap Rate|Python|Cruza receita de locagao (Airbnb) com preço pedido de venda (VivaReal) na<br>mesma regido e tipologia.|
|Stress Testing (Análise de<br>sue<br>Sensibilidade)|Python|Simula variagdes na receita (-10%, -20%) e no preço de venda (+5%, +10%)<br>f<br>=<br>:<br>para acharo ponto de inflexao de cada categoria.|
|Sintese dosAgentes &<br>Perspectivas|IA(LLM via<br>Prompting)|Pegaa tabela de fatos/estatisticas do Python e redige os pareceres com<br>persona (Auditor, Analista deAquisi¢ao, etc.).|
|Veredito Executivo &Resumo<br>para Video|IA|Consólida os pareceresem uma justificativa de decisão executivaem linguagem<br>natural.|
|5.O"MomentoUau"naDemon|stragao(Video|de3Minutos)|

Seu video de 3 minutos deve ser dividido com precisão cirurgica: 

1. 0:0o - 0:45 | O Veredito: Apresente de cara a decisão: "Analisamos o mercado de Itapema e [validamos/refutamos] a tese de compactos no Centro. A nossa recomendação de alocação de capital é [X] com retorno estimado de [Y]%." 

- 2. 0:45 - 1:45 | A Mesa de Convicção e o Ceticismo de Dados: Mostre a aplicação rodando. Destaque o Auditor Cético: "Não olhamos apenas para as m²dias simples. Nosso pipeline identificou que a receita do Centro estava distorcida por [X fator] e aplicou um stress test que provou..." 

- 3. 1:45 - 2:3o | Uso Real de IA e Método de Trabalho: Explique como usou a |[A como copiloto analitico, mostrando como os prompts testaram hipóteses e como o ai - log registra esse processo de refinamento. 

4. 2:3o - 3:0o | Escala e Próximos Passos (Se tivesse +1 semana): Explique a arquitetura agndéstica de mercado pronta para expansão nacional/internacional. 

### é. Como isso se reflete no ai -1 log/ (Sua nota de IA) 

- A Seazone quer ver a sua iteragado e senso critico com a IA. O ai -1 log (que inclui conversas como esta nossa!) mostrara: 

   - 1. Você questionando as análises iniciais. 

   - 2. Você desafiando a IA a não inventar dados e exigindo código deterministico em Python. 

   - 3. Você refinando as m²tricas de investimento e testando a tese dos compactos no Centro. 

##### Próximos Passos da nossa Discussão 

- Antes de partirmos para qualquer detalhe técnico ou conceitual mais profundo, quero saber o que você achou desta estrutura¢ao: 

   - 1. Faz sentido para você essa abordagem de Mesa de Convicção baseada em um Pipeline Sequencial Determinado (onde o Python faz o calculo num²rico e a IA atua na interpretagao, critica e síntese)? 

   2. O que você acha de definir a entrega como uma web app interativa em Streamlit contendo o Dashboard da Mesa de Convicção + o relatório executivo no README? 

   3. Queremos comegar explorando os dados reais de Itapema (via Python) para descobrir o que os números estado revelando antes de fecharmos as personas da Mesa de Convicção? 
## Você

Gostei da direção, mas antes de decidir qualquer coisa eu quero continuar explorando o produto e não entrar ainda na implementagao. Quero que você olhe para essa proposta da Mesa de Convicção principalmente do ponto de vista do objetivo do desafio e da experiência que eu vou entregar para a Seazone. Quero entender se realmente precisamos de quatro agentes, se existe algum papel que pode ser eliminado ou combinado, e principalmente se a ideia de agentes é realmente o melhor elemento da solução ou se estamos colocando multiagente so porque parece interessante. Também quero tomar cuidado para não transformar a entrega em um dashboard técnico cheio de m²tricas que não ajuda ninguém a tomar uma decisão. Para mim o mais importante é que no final fique muito claro qual decisão de investimento estamos recomendando, por que estamos recomendando, quais evidências sustentam essa decisão, quais são os riscos e em que condições essa decisão mudaria. Quero que você pense comigo sobre qual seria a experiência ideal de quem esta avaliando isso e qual seria o momento da demonstragao em que eles realmente entenderiam o valor da solução. Também quero discutir se uma aplicação web é realmente necessaria, se Streamlit faz sentido ou se deveríamos ter algo mais simples, e quanto de tecnologia é suficiente para demonstrar o uso de IA sem deixar o projeto técnico demais. Não quero que você comece a escrever código nem fechar a arquitetura. Primeiro quero que a gente defina muito bem qual é o produto, qual problema ele resolve e qual seria a experiência de ponta a ponta. E sempre que você sugerir alguma funcionalidade, quero que você relacione isso com o objetivo e os critérios do desafio, porque eu não quero construir coisas interessantes que não aumentem a qualidade da entrega. Comega então avaliando essa proposta do ponto de vista do produto e da experiência do avaliador e me faça as perguntas que você considera necessárias para a gente chegar nessa defini¢gao. 
## IA

Analisar a Mesa de Convicção soba otica de produto, experiência do usuário (no caso, o time da Seazone avaliando seu teste) e valor de negócio é o passo mais correto antes de encostar em qualquer linha de código. 

Abaixo esta a avaliação da ideia sob a lente dos critérios do desafio (45% Análise/Negécio, 30% IA/Log, 25% Comúnicagao). 

1. Avaliagdo Critica do Produto: Precisamos de Agentes ou E "Teatro"? 

Se colocarmos agentes apenas para simular dialogos, corremos o risco de parecer que estamos forçando uma arquitetura da moda que adiciona latência e poluição textual. 

O real valor dos papéis não é o "dialogo", mas o choque de perspectivas sobre a mesma evidência. Em comités de investimento imobiliario reais, o time não quer ler 1o paginas de conversa; ele quer ver Tesee Contraponto. 

##### Enxugando a Mesa: De 4 Agentes para 2 Camadas Analiticas (Ou 2 Perfis Claros) 

Podemos simplificar brutalmente a experiência mantendo 100% da inteligéncia e eliminando a gordura. Em vez de quatro personas separadas (Mercado, Aquisição, Cético, Lider), o produto funciona muito melhor com 2 Forças Opostas e 1 Sintese Decisoria: 

   - 1. A Tese do Oportunista (Growth/Yield): Junta Mercado + Aquisição. O foco é responder: Onde esta a maior assimetria de receita e retorno projetado em Itapema? 

   - 2. O Auditor de Risco (Cético/Compliance): O foco é responder: Por que esse numero pode ser uma ilusão? (Procura amostragem baixa, distorções de outliers de luxo na Meia Praia, vacância não calculada, viés de seasonality). 

- 3. A Matriz de Decisão & Invalidação (O Veredito Final): Une as duas pontas em uma recomendação executiva clara: Compre X sob as condigoées Y, e abandonea tese se Z acontecer. 

- Isso elimina o risco do "teatro de agentes" e foca no que a Seazone quer: Tomada de decisado defensavel com senso critico. 2. A Experiéncia Ideal do Avaliador e o "Momento Uau" O avaliador da Seazone vai abrir seu video e/ou seu repositório. Ele nado quer navegar por dezenas de abas com graficos de dispersão genéricos. Ele quer responder em 3o segundos as perguntas de negoécio. O Fluxo da Experiéncia Ideal (User Journey do Avaliador): 1. Primeira Tela (O Veredito Direto): ° Posigao clara sobre a tese interna: [ TESE INTERNA CONFIRMADA] ou [ TESE INTERNA REFUTADA J. o Arecomendação objetiva: "A alocação ideal em Itapema para a Seazone hoje é X (ex: 2 quartos a Y metros da praia na Meia Praia / Centro)." 

   - 2. O Momento Uau — A Análise de Ruptura (Stress Test Dinamico): 

      - © O avaliador vé uma barra/slider interativo ou matriz que mostra: "Esta recomendaçãoé valida até que..." 

      - Exemplo: "Se o preço por m² no Centro subir mais de 7.2%, a tese migra automáticamente para Bairro X." Isso prova que você entende de estratégia de alocação de capital, nado apenas de plotar histograma. 

##### 3. A Aba de Ceticismo de Dados (Auditoria com IA): 

#### o Uma seção mostrando exatamente onde os dados do Airbnb/VivaReal são frágeis 
- comoa IA identificou esses riscos sem 

"inventar" estatisticas. 

#### 3. Precisa de Web App (Streamlit) ou Algo Mais Simples? 

Para o formato do desafio (Tak e- home de 1 dia), Streamlit faz total sentido se for mantido ULTRA simples, pelas seguintes razées: 

- ¢ Para o Avaliador: E muito mais impactante interagir com uma ferramenta de decisão visual no video de 3 minutos do que narrar um relatório estático em PDF/Jupyter Notebook. 

- e Para a Nota de Comúnicagao (25%): Mostrar uma aplicação limpa e orientada a decisão no video passa uma sensagao imediata de produto pronto (production-ready thinking). 

- O limite seguro: A app deve ser apenas uma UI de Entrega da Recomendagdo (Decision Board), e NAO um painel BI genérico para o usuário ficar explorando filtros infinitos. A app deve conduzir a narrativa da sua decisão. 

Se por questão de tempo a App virar um gargalo, o produto pode ser 100% entregue em um README.md perfeitamente estruturado e visual com relatórios gerados, mas o Streamlit traz um diferencial competitivo forte se usado como vitrine do resultado. 

4. Perguntas Fundamentais para Definirmos o Produto Para avancarmos e desenharmosa estrutura exata do produto sem gastar energia com o que não gera nota, preciso entender a sua visão sobre estes 4 pontos: 

1. Sobre o Papel dos Agentes/IA: Você concorda em simplificar a "Mesa de Convicção" para esse modelo de Tese vs. Ceticismo/Auditoria, onde a IA é usada estritamente para questionar os dadose sintetizar argumentos em vez de simular multiplos papéis conversando? 

2. Sobre a Tese da Seazone (Compactos no Centro): Como você enxerga o objetivo da entrega: você quer que o produto seja uma ferramenta que testa e responde diretamente a essa tese preliminar da Seazone, usando o mercado de Itapema como prova de conceito? 

3. Sobre o Formato Final: Você prefere mirar em uma App Streamlit leve focada em apresentar a decisão + o relatório executivo no README.md, ou prefere focar toda a energia analitica no README.md/Notebook e deixar a interface de lado? 

4. Sobre a Dinamica do Video: Na sua visão, o que você gostaria de destacar nos 3 minutos do video para garantir a pontuagao maxima em comúnicação? 
## Você

1. Sim, vai ser bem mais objetivo e trara um valor de uso mais rápido. Uma outra coisa é que podemos pensar também na jornada. 2. Isso, seria o principal fator, mas que não va se limitar apenas a essa cidade, precisa ser algo que seja flexivel e expansivel para outros mercados 3. Streamlit, facil, objetivo e com uma jornada que vai trazer valor mais rápido. 4. Esque¢a o video por hora. 
## IA

A decisão de simplificar a arquitetura para duas forças opostas (Tese vs. Auditoria de Risco) com a Sintese Decisoria e adotar uma aplicação leve em Streamlit é o caminho mais maduro para essa entrega. Ela elimina a gordura conceitual e foca 100% no valor de negoécio e na jogabilidade da decisão. 

Como o foco atual é definir o produto, a jornada e o valor de negocio de ponta a ponta (sem focar no video nem no código neste momento), aqui esta a proposta detalhada do produto final: 

##### Nome do Produto: Seazone Investment Decision Engine (IDE) 

Proposito: Transformar dados brutos de mercado (Short - stay e Venda) em uma tese de alocação de capital defensavel, estressada por riscos e pronta para tomada de decisão executiva. 

### A Jornada da Experiéncia do Produto (User Journey na Streamilit) 

A aplicação no Streamlit nado deve ser um dashboard estático nem um mar de graficos soltos. Ela deve funcionar como uma esteira de tomada de decisão em 4 etapas bem definidas: 

[ 1. Matriz de Premissas ] > [ 2. Veredito & Tese ] > [ 3. Estresse & Invalidacao ] > [ 4. Shortlist Prática ] 

##### Etapa 1: A Matriz de Premissas de Negocio (Entrada Dinamica) 

- ¢ O que o usuário vé: Uma barra lateral (sidebar) clean com as variáveis reais da operação Seazone que afetam o ROI. 

- e Variáveis ajustaveis: 

   - Taxa de Gestão Seazone (ex: 20%). 

   - Custo de Oportunidade / WACC (ex: 10% a.a. ). 

   - Taxa de Desconto na Negociagao Imobiliaria (ex: 5% a 10% do valor do VivaReal). 

   - © Sazonalidade/Vacância projetada. 

- e Por que isso existe: Prova que a análise não é um calculo estático congelado; ela se adapta aos parametros financeiros da empresa em tempo real. 

##### Etapa 2: A Mesa de Convicção (O Coragao da Decisão) 

A tela principal abre imediatamente com a decisão executiva, dividida em dois blocos em confronto: 

- e Coluna A —A Tese de Oportunidade (O Crescimento): 

   - Posicionamento explícito sobre a tese preliminar: [TESE CONFIRMADA] ou [ TESE REFUTADA ]. 

   - Apresentagao da combinação vencedora em Itapema (ex: Tipologia + Bairro + Faixa de Metragem). 

   - Retorno Esperado (Cap Rate / Yield Anual) calculado deterministicamente por Python. 

- ¢ Coluna B — O Auditor de Risco (A Camada Cética da IA): 

   - AlAanalisa a Tabela Fato e aponta as fragilidades dos dados sem inventar números. 

   - Alertas do Auditor: \dentificagao de viés de amostragem (ex: poucos listings na região X), distorgao por outliers de altissimo padrão, ou dependência excessiva de picos de alta temporada. 

##### Etapa 3: A Fronteira de Invalidação (Ponto de Ruptura) 

Em vez de apenas dizer "compre X", esta etapa responde: "Sob quais condigées essa decisão deixa de ser a melhor?" 

- e Análise de Sensibilidade: Exibição clara do ponto de inflexao. 

   - Exemplo: "A tese do Centro se mantém superior enquanto o valor m²dio do m2 de aquisicao for inferior a R$ X. Se o preço subir acima desse limite, a tese migra automáticamente para Meia Praia (2 quartos)." 

- e Cenários de Estresse: O que acontece com a recomendação se a receita m²dia diária cair 10% ou 20%? 

Etapa 4: A Shortlist de Ativos do VivaReal (Execugao Prática) 

- ¢ Tabela interativa com os imoveis reais filtrados do dataset do VivaReal que atendem exatamente aos critérios da tese vencedora. 

- e Exibição das m²tricas calculadas por imdvel (Preço do Anuncio, Preço/m² Estimado, Receita Projetada no Airbnb e Cap Rate Estimado). 

#### Flexibilidade e Expansão para Outros Mercados (Agnosticismo de Arquitetura) 

Para garantir que a solução não parega uma ferramenta "engessada" em Itapema sem criar complexidade desnecessaria, a arquitetura do produto deve ser desenhada sob o conceito de Market - Agnostic Engine: 

- 1. Schema de Dados Padronizado (Data Contract): A Engine não consome os arquivos do Itapema diretamente no código principal. Existe uma camada de ingestdo que transforma os CSVs de qualquer cidade em 3 schemas padrão: listings f lat, pricing h istory 
- sales _m arket. 

2. Seletor de Mercado na UI: No topo da aplicacao, existe um seletor com "Itapema (SC) — Ativo" e a opgao de selecionar ou fazer upload do dataset de um "Novo Mercado" (com um estado placeholder demonstrando a capacidade de expansão). 

3. Prompting Estruturado Agnéstico: A camada de IA recebe as tabelas consólidadas com parametros genéricos ({cidade}, {bairro}, {metricas}), permitindo que a exata mesma lógica de contestagdo e auditoria rode para Sao Paulo, Rio de Janeiro ou mercados internacionais se dados similares forem fornecidos. 

#### Mapeamento do Produto vs. Critérios de Avaliagao do Hackathon 

|Elemento do Produto|Critério Atendido|Impacto naAvaliagao|
|---|---|---|
|Ponto de Invalidação & Auditoria<br>Cética|Raciocinio & Qualidade da<br>Análise (45%)|Demonstra maturidade de Senior/PE na tomada de decisão<br>de capital.|
|Resposta DiretaaTese Interna|Raciocinio8Qualidade da<br>Análise (45%)|Cumpre o requisito explícitododesafio sobreoscompactos<br>no Centro.|
|Separar Calculos (Python) de<br>Interpretagao (IA)|_<br>5<br>Uso RealdeIA/ ai-log (30%)|Evita alucinagées da IAe mostra uso de IApara raciocinio<br>qualitativoavangado.|
|Jornadaem StreamlitDirecionada a<br>Decisão|Comúnicagao(25%)|Permite passar uma visão clara eexecutivaem poucos<br>cliques e visualizagées.|
|ProximoPassonaEstruturagao|||

Agora que o formato do produto, a jornada da experiência e o modelo de negócio estão alinhados: 

Faz sentido comegarmos a analisar os dados reais de Itapema via Python (nos 5 arquivos disponibilizados) para descobrir o que os números dizem de fato sobre a tese dos compactos no Centro e identificar onde estado os riscos e vieses dos dados? 
## Você

entendi essa proposta mas antes de comegar a analisar os dados eu quero pensar um pouco mais na definição do produto porque não quero sair implementando uma coisa que ainda não esta muito bem definida a estrutura das quatro etapas parece fazer sentido mas eu quero que você me ajude a questionar se realmente precisamos de todas elas e principalmente se cada parte realmente ajuda a responder o problema da Seazone ou se estamos colocando algumas coisas só porque parecem interessantes tecnicamente eu também fiquei pensando nessa questão das premissas ajustaveis porque não quero criar uma ferramenta onde a pessoa fica mudando os parametros até conseguir a recomendação que queria então precisamos pensar em como separaro que vem dos dados o que é uma premissa nossa e Oo que é uma limitagao da análise outra coisa que quero discutir é se faz sentido mostrar esses agentes para o usuário ou se seria melhor deixar isso mais transparente e simplesmente mostrar duas perspectivas uma defendendo a oportunidade e outra tentando encontrar os problemas dela porque eu quero que a IA esteja realmente ajudando na decisão mas sem transformar o produto numa demonstragao de agentes conversando entre si também quero entender melhor se a shortlist de imóveis do VivaReal realmente agrega valor para o objetivo do desafio ou se ela pode acabar tirando atengao da parte mais importante que é a recomendag¢ao de investimento então antes de ir para Python eu quero que a gente defina qual é exatamente a pergunta que o produto precisa responder qual decisão ele precisa entregar no final quais evidências são necessarias para sustentar essa decisão e como seria a experiência de alguém da Seazone usando isso na prática não quero cdédigo ainda e também não quero fechar a arquitetura agora quero primeiro chegar numa definição bem clara do produto e principalmente quero garantir que a gente esta construindo algo que resolve o desafio e não só uma aplicacao bonita e tecnicamente interessante depois disso a gente pode olhar os dados e descobrir como transformar essa ideia em algo concreto 
## IA

Essa é a postura exata de quem consiréi produto de alto nivel: Questionar o excesso de engenharia antes de encostar nos dados. 

Vamos dissecar e enxugar a ideia, cortando tudo o que é "perfumaria técnica" e garantindo que cada elemento sirva exclusivamente para responder ao desafio da Seazone. 

#### 1. Qual é a Pergunta Central que o Produto Precisa Responder? 

A Seazone é uma operadora de aluguel por temporada (short - stay) e gestora de patrim²nio. A pergunta exata que a diretoria faz não é "me dé um grafico bonito de Itapema", mas sim: 

"Onde devemos alocar capital em Itapema para obter o melhor retorno ajustado ao risco na operação de short -s tay, e a tese dos compactos no Centro é a nossa melhor aposta?" 

A Decisão Final que o Produto Precisa Entregar: 

O produto precisa sair da análise com uma Declaragao de Alocagao de Capital: 

- 1. O Veredito do Centro: Se a tese preliminar da Seazone se sustenta (SIM / NAO) e 

a justificativa num²rica exata. 

   - 2. O Perfil Campeão: A combinação exata de atratividade: Bairro + Tipologia (ex: 2 quartos) + Faixa de Área (m²) + Faixa de Preço de Compra. 

- 3. O Ponto de Invalidação (Gatilho de Decisão): O limite exato em que essa oportunidade deixa de ser a melhor (ex: "Se o m² passar de R$ X, migre para a opgao B"). 

- 2. Questionando as 4 Etapas: O que Fica e o que E Excesso? 

Vamos aplicar um filtro rigido em cada etapa proposta anteriormente para ver se ela ajuda a tomar a decisão ou se é apenas "distração técnica”: 

A. Premissas Ajustaveis: Devem existir? 

   - e Oseu receio é 100% correto: Se o usuário puder mudar os parametros até achar o resultado que quer, a análise perde a rigidez e vira um "brinquedo de simulação". 

   - e Asolução: Premissas Fixas e Transparentes com Trava. Os dados determinam o resultado (preço do m², receita do Airbnb). As premissas operacionais (ex: taxa de gestão da Seazone de 20%, custo de capital de 10%) devem ser padrão de mercado (Default) e ficar visiveis como “"Premissas do Modelo”, não como controles para o usuário alterar a decisão. Isso garante integridade analitica. 

- B. Posigado sobre os Agentes: Exibir "Agentes" ou Perspectivas? 
- Decisão de Produto: Eliminar o termo "Agentes" da Interface. 

   - ¢ Mostrar avatares ou didlogos de "Agente 1" vs "Agente 2" passa uma sensacao de teatro e demonstragao de tecnologia. 

   - ¢ O que colocar no lugar: Duas seções analiticas diretas e sóbrias: 

      - Tese de Oportunidade (O Lado Positivo): Onde os dados mostram maior assimetria de retorno. 

      - Auditoria de Riscos (O Ceticismo dos Dados): Onde a IA aponta fragilidades do dataset (ex: baixa amostragem, viés de proprietario, outliers). 

   - e A|lAtrabalha nos bastidores gerando essas análises em cima de tabelas consólidadas, mas o usuário só enxerga Análise de Tese vs. Análise de Risco. 

- C. A Shortlist do VivaReal: Agrega Valor ou Trava a Narrativa? 

   - e A Avaliagado: A Seazone perguntou no desafio: "Se a Seazone fosse investir hoje, o que você compraria e por qué?" 

   - ¢ AConclusão: A shortlist agrega valor, mas NAO pode ser uma tabela gigante de compras. Ela deve funcionar como a "Prova de Vida da Tese" (3 a 5 imoveis reais do dataset que exemplificam a tese em prática). Ela serve para provar que a oportunidade recomendada não é tedrica, mas sim algo que existe para comprar no mercado hoje. 

##### 3. As Evidéncias Essenciais para Sustentar a Decisão 

Para a decisão ser defensavel (atendendo aos 45% do critério do desafio), a aplicação precisa apresentar apenas 4 evidências fundamentais: 

1. Evidéncia de Receita (Airbnb): Quanto cada perfil de imdével realmente fatora por ano (Mediana de Diaria x Taxa de Ocupação Estimada). 

2. Evidéncia de Custo de Aquisição (VivaReal): Quanto custa comprar esse imdvel na mesma localização/tipologia (Preço Médio e Preço/ m*)2. 

- 3. Evidéncia de Retorno (Yield / Cap Rate): O indicador financeiro direto: Receita reco Liguida de Aquisição Anual 

   - reco de Aquisição 

- 4. Evidéncia de Amostragem (Confiabilidade): Quantos imóveis sustentam aquele numero (para evitar tomar decisóes com base em 2 apartamentos atipicos). 

#### 4. A Experiéncia de Uso na Prática (O Fluxo Enxuto) 

A aplicação deixa de ser um "dashboard interativo de filtros" e passa a ser um Relatorio Interativo de Decisão (Decision Executive 

Summary). 

Ao abrir a ferramenta, a pessoa da Seazone vivencia esta jornada: 

[ Tese Interna: Confirmada ou Refutada? ] 

- v 

- [ A Recomendação de Alocacdo (Bairro + Perfil + Retorno Esperado) ] v 

- [ Análise Concreta: Tese de Oportunidade VS. Risco de Dados ] v 

- [ Ponto de Ruptura (Em quais condições essa recomendacdo muda) ] v 

- [ Exemplo Pratico de Aquisicao (3 a 5 imóveis reais do VivaReal) ] 

Essa estrutura resolve o desafio com precisão cirurgica: 

- ¢ E objetiva: Responde diretamente o que comprar e onde investir. 

- ¢ E honesta: Aponta as limitagdes dos dados e não esconde riscos. 

- ¢ E acionavel: Entrega a recomendacdo pronta com amostra real. 

- ¢ E madura: Usa IA para auditagem e síntese analitica, sem encenar conversas infantis de agentes. 

##### Validagao da Definigao de Produto 

713 

##### Com essa estrutura simplificada: 

1. Conseguimos responder com clareza todas as 4 perguntas oficiais do desafio da Seazone. 

- 2. Eliminamos a complexidade desnecessaria de simular agentes conversando. 

- 3. Garantimos que a IA seja usada para pensar, criticar e sintetizar, e nado para inventar m²tricas. 

Faz sentido fecharmos essa definição de produto e partirmos para a exploragao dos dados reais em Python, para descobrirmos a verdade oculta sobre Itapema e ver se a tese dos compactos no Centro se sustenta? 
## Você

Você recebeu uma base de dados do mercado imobiliario de Itapema (SC) — dados reais de anúncios de Airbnb e de venda (VivaReal). Com base neles, entregue uma recomendação de investimento para a Seazone, respondendo: Qual o melhor perfil de imóvel para investir na cidade? (tipologia, n° de quartos, tipo de anúncio) Qual a melhor localização em termos de receita? Quais caracteristicas explicam as melhores receitas? Se a Seazone fosse investir hoje, o que você compraria e por qué? Faga uma estimativa simples de retorno e defenda a decisão. 
## IA

1. Perfil Ideal de Im²vel para Investir 

- ¢ Tipologia & Estrutura: Apartamentos de 2 Quartos (éo a 85 m7). 

- ¢ Tipo de Anuncio: Espaco Inteiro (Entire Place) com Reserva Instantanea (ca n_ instan t_b ook = True). 

- e¢ Posigdo sobre a Tese da Seazone (Studios/1Q no Centro): Refutada. 

   - © Studios e 1 dormitdrio tem um ticket de compra desproporcionalmente alto no Centro (mediana de R$ 93o. 00o para ~53m², a R$ 20.1é8/m7) frente a uma diária mediana de R$ 433,50. Isso gera um Gross Yield de 8,51% a.a.. 

   - Ja os apartamentos de 2 quartos no Centro ou Morretes entregam a melhor relagao custo/beneficio. No Centro, um 2Q tem preco mediano de R$ 1.105.00o (R$ 12.989/m7?) e diária de R$ 557,0o (Gross Yield de 9,20% a.a.). Em Morretes, 2Q geram 11,13% a.a. de Gross Yield (Preço de compra: R$ 75o. 00o | ADR: R$ 457,50). 

### 2. Melhor Localizagao em Termos de Receita 

- ¢ Volume e Faturamento Absoluto: Meia Praia. Concentra a maior liquidez da cidade (2. 8éo anúncios e ADR mediana de R$ é85 em 3Q), mas possui alto preço por m2? de venda (R$ 14. 923/m² a R$ 18. 555/m²). 

- e Melhor Eficiéncia de Alocagao (Cap Rate / Yield): Centro (Segmento Consólidagao) e Morretes (Segmento Yield Alto). 

   - eo Centro: Apresenta maior nota de satisfação (3,é2/5) e densidade de avaliações (14,8 reviews/anúncio), garantindo ocupação mais estavel no ano. 

   - Morretes: Entrega maior taxa de retorno sobre o capital investido (Cap Rate bruto > 11% a. a. em 2Q), servindo como excelente opção para expansão com menor ticket de entrada. 

#### 3. Caracteristicas que Explicam as Melhores Receitas 

- 1. Capacidade de Hospedes / Densidade por Dormitorio: Im²veis que comportam entre 4 e é hóspedes (tipico de 2 quartos com sofa - cama) capturam o publico de familias e grupos, multiplicando a disposição a pagar a diária. 

2. Atributos de Experiéncia e Profissionalizagao: Anuncios com i s_ professional e ca n_ instant _b ook ativos registram taxas de conversão substancialmente maiores. 

- 3. Vaga de Garagem e Ar Condicionado (Amenities): Essenciais no litoral catarinense durante a alta temporada. 

- 4. Proximidade Mar vs. Ticket de Aquisição: Imdveis na quadra do mar tém diárias mais elevadas, mas quando o valor do m2 ultrapassa R$ 18.000, o retorno percentual (Yield) cai significativamente. 

#### 4. Recomendagao Direta de Compra e Estimativa de Retorno 

###### Imovel Selecionado no VivaReal 

- e Link / 1D: Anuncio ID 2729245113 (ou equivalente no Centro). 

- e Localizagao: Centro, Itapema - SC. 

- e Perfil: 1 a 2 quartos | 7o m² de área util | Com vaga de garagem. 

- e Valor de Pedida: R$ é94. 000,0o (Preco/m²: ~R$ 9.914/m², bem abaixo da mediana de R$ 15. 789/m² do Centro). 

Demonstrativo Financeiro Simples (Projegao Anual) 

- e Preço de Aquisição: R$ é94. 000,0o 

- ¢ Capex Inicial / Enxoval (Seazone Standards): R$ 3o. 000,0o 

- ¢ Investimento Total contabilizado: R$ 724.000,0o 

- ¢ Diaria Média Estimada (ADR Conservadora): R$ 480,0o 

- ¢ Taxa de Ocupação Média Projetada: 52% (19o dias ocupados/ano) 

### ¢ Receita Bruta Anual: 19o x R$ 480,0o = R$ 91.200,00/ano 

- ¢ Custos Operacionais Estimados (Taxa Seazone 20% + Condominio + IPTU): R$ 27.3é0,0o 

- ¢ Receita Líquida Operacional (NOI): R$ é3.840,00/ano 
- Cap Rate Liquido: 8,82% a. a. (Net Yield em relagao ao investimento total). 
## Você

Perfeito. Agora, qual stack? Simplicidade aqui, porém, entregando o que fechamos. A ideia aqui é focar no negocio e nas regras dele, essa que deve ser a estrela principal não a tecnologia. 
## IA

Para garantir que o foco permanega 100% no negocio, nas regras de decisão e no raciocinio estratégico, a escolha da stack deve seguir um único mandamento: zero fricgao de infraestrutura, execução local imediata e maxima transparéncia para o avaliador. 

A tecnologia servira exclusivamente como o palco simples e robusto para a regra de negocio brilhar. 

### A Stack Recomendada: "Lean & High Impact" 

Camada Tecnologia Por que essa escolha? (Foco no Negocio)<br>Linguagem / Linguagem nativa do ecossistema de dados. Todo o calculo financeiro, consólidagao do<br>Core Python 3. 10+ dataset e lógica. de negócioie rodam em códigooe puro e auditavel.we<br>Motor de Pandas & NumP Garantem o processamento deterministico. Fazem o agrupamento, calculam medianas,<br>Dados y Gross Yield, Cap Rate e os pontos de ruptura sem nenhuma intervengao de LLM.<br>Transforma o código Python na aplicação web em pouquíssimas linhas. Não exige<br>Interface / Ul Streamlit HTML/CSS/JS, roda com um único comando (streamlit run app.py) e entrega uma UX<br>limpa e executiva.<br>Orquestracao/ OpenAl API/ Anthropic Chamada de API direta, sem frameworks intermediarios. Recebe o contexto em<br>IA 4 ¢ APIpens(via SDK nativo)nrop JSON/DataFramebaixissimaroar latência.~ do Python e devolve a síntese analitica (Tese vs. Auditoria) com<br>: os Para gerar graficos interativos simples e elegantes (ex: a Fronteira de Invalidação / Análise<br>Visualização Plotly Express de Sensibilidade).<br>Por que NAO usar Frameworks de Agentes (ex: CrewAl, AutoGen, LangChain)?<br>1. Evita o "Teatro": Frameworks de multiplos agentes tendem a adicionar complexidade desnecessaria, gastar tempo em logs extensos e<br>criar dependências dificeis de depurar em um desafio take-home.<br>2. Previsibilidade: Com chamadas diretas via SDK (usando system prompts bem definidos para o papel de "Auditor Cético" e "Analista de<br>Tese"), você controla exatamente a entrada de dados e impede quea IA alucine ou fuja da regra de negécio.<br>3. Legibilidade no ai - log/: Seu processo de desenvolvimento fica transparente, mostrando que você usoua IA para construir uma lógica<br>sólida, e não que montou uma "caixa - preta" complexa.<br>AArquitetura de Pastas e Arquivos (Simplicidade Absoluta)<br>O repositório do desafio ficara extremamente limpoe facil de rodar por qualquer pessoa da Seazone:<br>jt202é - seu - nome/<br>data/ # Os 5 CSVs originais do desafio<br>Details _I tapema.csv<br>Price AV_Itapema.csv<br>lL eee<br>src/ # A Inteligéncia de Negdécio<br>engine. py # Calculos deterministicos (Medianas, Yield, Ruptura)<br>prompts.py # Prompts das perspectivas (Tese e Auditoria)<br>a i_ client.py # Integracdo com a API de LLM<br>app.py # A UI em Streamlit (Apenas layout e componentes)<br>ai - log/ # Histórico completo das conversas em markdown/texto<br>'_ README.md # O Relatdério Executivo + Instruções para rodar<br>requirements.txt # Dependéncias leves (streamlit, pandas, plotly, openai)<br>

### Como essa Stack Impulsiona a Experiéncia do Avaliador 
- Pronto em 1 comando: O avaliador precisa apenas clonar o repositório e rodar streamlit run app.py. 

   - ¢ Zero tempo perdido em setup: Nenhuma necessidade de configurar bancos de dados complexos, Docker multinivel ou servidores web pesados. 

   - ¢ Foco no que importa: Todo o esforgo de engenharia fica concentrado dentro de engine. py (as regras de negocio de alocação de capital da Seazone) e no visual direto ao ponto do Streamlit. 

- Essa estrutura é suficiente para demonstrar dominio técnico, garantir rigor analitico e manter a tese de investimento como a grande estrela da entrega. 
## Você

Agora crie um prompt explicando toda a lógica de negócio que definimos aqui e a stack. Eu vou mandar para a IA que vai executar.

## IA

O prompt a seguir deve ser entregue ao seu copiloto de IA, como Claude Code ou OpenCode. Ele traz todo o alinhamento de produto, a lógica de negócio refinada, os achados numéricos de Itapema e a stack simplificada para iniciar a construção do projeto. 

#### Prompt para a IA de Execugao 

Você é um Engenheiro de Software Sénior e Analista Financeiro/Imobilidrio especialista em produtos de decisão. Sua m 

#### 1. OBJETIVO DO PRODUTO E VISAO GERAL Vamos construir o **Seazone Investment Decision Engine (IDE) — Mesa de Convicção**. Não queremos um dashboard genérico de graficos ou uma simulação teatral de agentes conversando. O produto é uma **ap 

O foco absoluto deve ser a **lógica de negócio e as regras de alocação de investimento**, e nado a complexidade de en 
### 2. CONCLUSOES DE NEGOCIO E TESE DE ITAPEMA (FATOS CALCULADOS) 

A análise deterministica ja realizada nos dados revela as seguintes definicdes de negócio que o sistema deve incorpo 

1. **Posicdo sobre a Tese Interna (Compactos/Studios no Centro):** **REFUTADA.** * *Evidéncia:* Studios/1Q no Centro possuem ticket de aquisi¢do desproporcionalmente alto (mediana de R$ 930.00o 

2. **Perfil Campeão Recomendado:** **Apartamentos de 2 Quartos (éo a 85 m²).** * *Evidéncia:* No Centro, o 2Q tem preco mediano de R$ 1.105.00o (R$ 12.989/m²) com ADR de R$ 557,0o (Gross Yield 

3. **Melhores Localizacdes por Estratégia:** * **Meia Praia:** Liquidez e volume absoluto de faturamento, mas com ticket de m² elevado. * **Centro:** Melhor equilibrio de satisfa¢do dos hóspedes, consisténcia de demanda e liquidez executiva. * **Morretes:** Maior rentabilidade percentual (Cap Rate / Yield alto) com menor ticket de entrada. 

4. **Caracteristicas Explicativas:** Alta densidade de hóspedes (4 a é pessoas), vaga de garagem, ar condicionado e 

### 3. A STACK TECNICA (LEAN & HIGH IMPACT) Utilizaremos uma stack simples, previsivel e sem sobrecarga de infraestrutura: 

* **_inguagem:** Python 3.10+ 

* **Motor de Dados:** “pandas e ~numpy’ para todos os calculos deterministicos (Yield, Cap Rate, Medianas e Análise * **Interface (UI):** ~streamlit> para criar uma UX de relatorio executivo limpa. * **Visualizacdo:** ~plotly.express para graficos interativos leves. * **Camada de IA (Sintese e Auditoria):** Chamadas diretas a API de LLM (sem frameworks pesados como CrewAI, AutoGen 

### 4. ARQUITETURA DO PROJETO E ESTRUTURA DE PASTAS Organize o repositório exatamente assim: 

jt202é - seu - nome/ data/ # CSVs originais do desafio [— Details _I tapema.csv Pric e_ A V_ Itapema.csv Host s_ id s_ Itapema.csv Mes h_ Id s_D ata _I tapema.csv VivaReal _I tapema.csv src/ # Regras e Logica de Negdcio [— engine. py # Processamento deterministico (Pandas, Joins, Métricas) [= prompts.py # Prompts do Analista de Tese e do Auditor Cético a i_ client.py # Integracdo simples com a API de LLM app.py # Aplicacdo Streamlit (Interface Executiva) ai - log/ # Historico exportado das sessões de IA (.md/.txt) README.md # Relatorio Executivo final + Como rodar requirements.txt # Dependéncias leves 

### 5. JORNADA DA APLICACAO (STREAMLIT UX) A interface no “app.py deve ser organizada em 4 etapas diretas: 

1. **Painel de Premissas Operacionais (Sidebar):** * Exibir premissas fixas e transparentes com defaults de mercado: Taxa de Gestdo Seazone (20%), Custo de Oportuni 

2. **A Mesa de Convicção (Veredito Direto & Choque de Visões):** * **Posicao Clara:** Badge visivel ~[ TESE DO CENTRO: REFUTADA ]° e a recomendacao oficial de alocação de capital * **Tese de Oportunidade:** Visdo focada no retorno e na assimetria de receita gerada por codigo. * **Auditoria de Riscos (Ceticismo com IA):** Andalise gerada por LLM que aponta fragilidades do dataset (ex: viés 

3. **Análise de Sensibilidade / Ponto de Invalidacdo:** * Grafico interativo em Plotly mostrando: *"A recomenda¢cao do Centro (2Q) se mantém superior até que o valor m²di 

4. **Shortlist Prática de Aquisicdo:** * Tabela com 3 a 5 imdveis reais do ~VivaReal _I tapema.csv’ que casam perfeitamente com a tese (ex: ID ~ 2729245113 
### é. REGRAS DE EXECUCAO DA IA * **NUNCA deixe a LLM inventar números.** Todos os cdalculos de diária mediana, receita estimada, preco por m² e Cap * A LLM atuara estritamente na **interpretacao analitica, redação do parecer do Auditor Cético e consólidação do ver * Mantenha o código limpo, comentado e focado na clareza da tomada de decisão. 

Por favor, confirme se você compreendeu a arquitetura, as regras de negocio e a estrutura do produto. Em seguida, pr 
## Você

ah esqueci add o git que vamos usar: https://github.com/mateuxcv/jovens-talentos-202é-hackathon-data 
## IA

Ótima adicdo. Ter o repositório correto mapeado garante que o projeto fique exatamente alinhado coma estrutura oficial do desafio. 

Aqui esta o prompt atualizado com o repositério [https: //github. com/mateuxcv/jovens - talentos - 202é -h ackathon -d ata] (https: //github.com/mateuxcv/jovens -t alentos -2 02é -h ackathon -d ata) incluido na seção de contexto e entrega, pronto para enviar a sua IA de execucao: 

#### Prompt para a IA de Execugao (Atualizado) 

Você é um Engenheiro de Software Sénior e Analista Financeiro/Imobilidrio especialista em produtos de decisão. Sua m 

##4# 1. OBJETIVO DO PRODUTO E VISAO GERAL Vamos construir o **Seazone Investment Decision Engine (IDE) — Mesa de Convicção**. Não queremos um dashboard genérico de graficos ou uma simulação teatral de agentes conversando. O produto é uma **ap 

O projeto utilizara como base e referéncia de entrega o repositodrio oficial: ©@ **Repository:** https://github.com/mateuxcv/jovens - talentos -2 02é -h ackathon -d ata 

O foco absoluto deve ser a **lógica de negócio e as regras de alocação de investimento**, e não a complexidade de en 

##Ht 2. CONCLUSOES DE NEGOCIO E TESE DE ITAPEMA (FATOS CALCULADOS) 

A análise deterministica ja realizada nos dados revela as seguintes definicdes de negócio que o sistema deve incorpo 

1. **Posicdo sobre a Tese Interna (Compactos/Studios no Centro):** **REFUTADA.** * *Evidéncia:* Studios/1Q no Centro possuem ticket de aquisi¢do desproporcionalmente alto (mediana de R$ 930.00o 

2. **Perfil Campeão Recomendado:** **Apartamentos de 2 Quartos (é@ a 85 m²).** * *Evidéncia:* No Centro, o 2Q tem preco mediano de R$ 1.105.00o (R$ 12.989/m2) com ADR de R$ 557,0@ (Gross Yield 

3. **Melhores Localizacdes por Estratégia:** * **Meia Praia:** Liquidez e volume absoluto de faturamento, mas com ticket de m² elevado. * **Centro:** Melhor equilibrio de satisfacao dos hóspedes, consisténcia de demanda e liquidez executiva. * **Morretes:** Maior rentabilidade percentual (Cap Rate / Yield alto) com menor ticket de entrada. 

4. **Caracteristicas Explicativas:** Alta densidade de hóspedes (4 a é pessoas), vaga de garagem, ar condicionado e 

### 3. A STACK TECNICA (LEAN & HIGH IMPACT) Utilizaremos uma stack simples, previsivel e sem sobrecarga de infraestrutura: 

* **L_inguagem:** Python 3.10+ 

* **Motor de Dados:** “pandas e “numpy’ para todos os calculos deterministicos (Yield, Cap Rate, Medianas e Análise * **Interface (UI):** ~streamlit> para criar uma UX de relatorio executivo limpa. * **Visualizacao:** ~plotly.express para graficos interativos leves. * **Camada de IA (Sintese e Auditoria):** Chamadas diretas a API de LLM (sem frameworks pesados como CrewAI, AutoGen 

### 4. ARQUITETURA DO PROJETO E ESTRUTURA DE PASTAS Organize o repositório exatamente assim: 

jt202é - seu - nome/ data/ # CSVs originais do desafio L— Details I tapema.csv Pric e_ A V_ Itapema.csv Hosts _i ds _ Itapema.csv Mes h_ Id s_D ata _I tapema.csv _ VivaReal _I tapema.csv src/ # Regras e Logica de Negdcio |— engine. py # Processamento deterministico (Pandas, Joins, Métricas) = prompts. py # Prompts do Analista de Tese e do Auditor Cético a i_ client.py # Integracao simples com a API de LLM app.py # Aplicacdo Streamlit (Interface Executiva) 

## [— ai - log/ 

[— ai - log/ # Historico exportado das sessGées de IA (.md/.txt) = README.md # Relatorio Executivo final + Como rodar requirements.txt # Dependéncias leves 

### 5. JORNADA DA APLICACAO (STREAMLIT UX) 

A interface no “app.py deve ser organizada em 4 etapas diretas: 

1. **Painel de Premissas Operacionais (Sidebar):** 

- Exibir premissas fixas e transparentes com defaults de mercado: Taxa de Gestdo Seazone (20%), Custo de Oportuni 

- 2. **A Mesa de Convicção (Veredito Direto & Choque de Visões):** * **Posicao Clara:** Badge visivel ~[ TESE DO CENTRO: REFUTADA ]> e a recomendação oficial de aloca¢dao de capital * **Tese de Oportunidade:** Visão focada no retorno e na assimetria de receita gerada por codigo. * **Auditoria de Riscos (Ceticismo com IA):** Andalise gerada por LLM que aponta fragilidades do dataset (ex: viés 

- 3. **Análise de Sensibilidade / Ponto de Invalidacao:** * Grafico interativo em Plotly mostrando: *"A recomenda¢ado do Centro (2Q) se mantém superior até que o valor m²di 

- 4. **Shortlist Prática de Aquisicdo:** * Tabela com 3 a 5 imóveis reais do ~VivaRea l_ Itapema.csv que casam perfeitamente com a tese (ex: ID ~ 2729245113 

d#4H# é. REGRAS DE EXECUCAO DA IA * **NUNCA deixe a LLM inventar números.** Todos os calculos de diária mediana, receita estimada, preco por m² e Cap * A LLM atuara estritamente na **interpretacdo analitica, reda¢cao do parecer do Auditor Cético e consólidação do ver * Mantenha o codigo limpo, comentado e focado na clareza da tomada de decisão. 

Por favor, confirme se você compreendeu a arquitetura, as regras de negócio e a estrutura do produto. Em seguida, pr 
## Você

Certo, agora precisamos dar uma olhada nessa painel do Streamlit. O Ideal é que seja uma mostragem de negócio não parecer um dashboard comum. melhore esse prompt 
## IA

Aqui esta uma versão aprimorada do prompt, com foco explícito em Design de Produto Executivo, UX de Decisão de Negocio e Storytelling Visual, para evitar a todo custo a aparéncia de um "dashboard genérico de BI" (cheio de graficos soltos e cards flutuantes sem contexto). 

### Prompt Aprimorado para a IA de Execugao (Foco na UX do Streamlit) 

Você é um Engenheiro de Software Sénior e Lead Product Designer especialista em interfaces executivas de tomada de d 

Sua missão agora é construir o arquivo “app.py em Streamlit para o **Seazone Investment Decision Engine (IDE) — Mes 
**DIRETRIZ DE DESIGN DE PRODUTO (CRITICO): ** A interface NAO PODE parecer um dashboard comum de BI (cheio de cards de KPI aleatérios, graficos de pizza e tabelas 

### 1. PRINCIPIOS DE DESIGN & UX (BUSINESS - FIRST) 

1. **Hierarquia Visual Direta:** O resultado final (A Decisão) deve ser a primeira coisa visivel, e ndo escondida no 2. **Design Limpo e Profissional:** Use espacamentos bem definidos, tipografia clara, containers/cards com bordas di 3. **Sem Fluff Técnico:** Evite exibir termos de céddigo na UI (como nomes de colunas do DataFrame ~bedrooms _ca t~> ou 4. **Sem Filtros Infinitos:** A UI nado deve ser uma ferramenta de exploracdo livre; ela deve ser uma **vitrine da te 

dHHE 2. ESTRUTURA VISUAL E NARRATIVA DA APLICAGAO (~app.py>) 

A pagina deve ser estruturada em 4 blocos de experiência sequencial: 

@}<br>

#### @} BLOCO 1: O VEREDITO DA TESE (Header Executivo) * **Cabeçalho:** Titulo sdébrio: *Seazone Investment Decision Engine | Mercado Itapema (SC)*. 

* **Badge de Posicao Estratégica (Grande Destaque Visual):** * ~[ >é TESE INTERNA REFUTADA: Compactos no Centro não oferecem o melhor retorno ajustado ao risco ]~ * **Card da Recomendacdo Oficial:** * Exibir com clareza a decisado de alocação de capital: **Apartamentos de 2 Quartos (éo - 85m²) no Centro ou Morretes 
### BLOCO 2: A MESA DE CONVICCAO (Choque Visual de Perspectivas) Crie um layout em **2 colunas bem separadas** (usando ~st.columns’) para contrastar as visdes: 

©<br>

* **Coluna da Esquerda: © Tese de Oportunidade (Growth & Yield)** * Apresenta os números que sustentam o investimento (ADR mediana, liquidez da regido, demanda por 2Q). * *Fonte:* Calculos deterministicos da “engine.py. 

@<br>

- **Coluna da Direita: @ Auditoria de Riscos (o Ceticismo dos Dados)** * Apresenta os pontos de aten¢do identificados pela LLM sobre os dados (ex: amostragem em determinados bairros, de * *Fonte:* Retorno do ~a i_ client.py baseado na Tabela Fato. 

«2%<br>

#HHHE «2% BLOCO 3: ANALISE DE SENSIBILIDADE & FRONTEIRA DE INVALIDACAO (Interactive Stress Test) 

* **Objetivo:** Mostrar sob quais condi¢des a recomendação deixa de ser a melhor. 

* **Componente Visual:** Um grafico limpo Plotly (*Line Chart* ou *Waterfall Chart*) mostrando a curva de retorno em * **Caixa de Insight Executivo:** 

* *"A tese de 2Q no Centro se mantém superior até que o valor de aquisic¢do suba **X%**. Acima desse limiar, a aloc 

@<br>

#### @ BLOCO 4: PROVA DE VIDA DA TESE (Shortlist Prdtica VivaReal) * **Objetivo:** Provar que a tese tem execucdo real no mercado hoje. * **Componente Visual:** Uma tabela estilizada com 3 a 5 imóveis selecionados a dedo do dataset do VivaReal que aten * **Colunas visiveis:** Bairro | Tipologia | Área ($m*2$) | Preco Pedido | Cap Rate Liquido Estimado | Link Direto. 

### 3. BARRA LATERAL (SIDEBAR) — PREMISSAS DE NEGOCIO Crie uma sidebar recolhível com o titulo **"Premissas do Modelo Financeiro"**: * Taxa de Gestão Seazone (Default: ~20%) * Custo de Oportunidade / WACC (Default: ~10.0% a.a.°) * Desconto Médio em Negociacdo Imobilidria (Default: ~5.0%) * Taxa de Ocupacdo Média Projetada (Default: ~52.0%) 

*Nota: Alterar esses parametros deve recalcular instantaneamente os indicadores do dashboard via ~engine.py.* 

### 4. INSTRUCOES DE IMPLEMENTACAO TECNICA (STREAMLIT) 

* Utilize ~st.set _p age _ config’ com layout “wide” e titulo profissional. * Use ~st.metric’ com deltas visuais para exibir retornos comparativos. 

* Utilize ~st.markdown com CSS customizado leve (~<div style="...">°) apenas para criar os cards de destaque (Vered * Garanta tratamento de erros caso os arquivos de dados ou a chave de API não estejam configurados localmente. 

Por favor, apresente a proposta de código para o ‘app.py seguindo estritamente essa visão de produto executivo e st
