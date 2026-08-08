/* lab-models.js — "os modelos, um a um": explicação didática de cada algoritmo
 * usado nas aulas do Lab de IA (como funciona · como usa os dados · como calcula).
 * Compartilhado por todas as aulas. Cada página declara sua lista:
 *     <div data-model-deepdive="linear,ridge,tree,rf,gb,knn,svr,mlp"></div>
 * e inclui <script src="/static/lab-models.js"></script>.
 * i18n: pt/en/es/fr — herda o idioma do painel via window.LABI18N.lang. */
(function () {
  const L = {
    como:  { pt: "Como funciona",     en: "How it works",        es: "Cómo funciona",      fr: "Comment ça marche" },
    dados: { pt: "Como usa os dados",  en: "How it uses the data", es: "Cómo usa los datos", fr: "Ce qu'il fait des données" },
    calc:  { pt: "Como calcula",       en: "How it computes",      es: "Cómo calcula",       fr: "Comment il calcule" },
  };

  // Todos recebem os MESMOS KPIs (coletados via E2/KPM). O que muda é o que cada
  // um FAZ com eles. Cada campo tem as 4 línguas (pt/en/es/fr).
  const M = {
    linear: {
      ic: "📈",
      nome: { pt: "Regressão Linear", en: "Linear Regression", es: "Regresión Lineal", fr: "Régression linéaire" },
      tag: { pt: "linear", en: "linear", es: "lineal", fr: "linéaire" },
      como: {
        pt: "Traça a “melhor reta” (ou plano) pela nuvem de pontos: prevê o alvo como uma <b>soma ponderada</b> dos KPIs — ŷ = β₀ + β₁·x₁ + … Cada peso β diz o quanto aquele KPI empurra o resultado.",
        en: "Fits the “best line” (or plane) through the point cloud: predicts the target as a <b>weighted sum</b> of the KPIs — ŷ = β₀ + β₁·x₁ + … Each weight β says how much that KPI pushes the result.",
        es: "Traza la “mejor recta” (o plano) por la nube de puntos: predice el objetivo como una <b>suma ponderada</b> de los KPIs — ŷ = β₀ + β₁·x₁ + … Cada peso β indica cuánto empuja ese KPI el resultado.",
        fr: "Ajuste la « meilleure droite » (ou plan) dans le nuage de points : prédit la cible comme une <b>somme pondérée</b> des KPI — ŷ = β₀ + β₁·x₁ + … Chaque poids β dit à quel point ce KPI pousse le résultat.",
      },
      dados: {
        pt: "Usa <b>todas</b> as amostras de treino de uma vez para achar os pesos que passam “no meio” dos pontos.",
        en: "Uses <b>all</b> training samples at once to find the weights that pass “through the middle” of the points.",
        es: "Usa <b>todas</b> las muestras de entrenamiento a la vez para hallar los pesos que pasan “por el medio” de los puntos.",
        fr: "Utilise <b>toutes</b> les données d'entraînement d'un coup pour trouver les poids qui passent « au milieu » des points.",
      },
      calc: {
        pt: "Escolhe os pesos que <b>minimizam a soma dos erros ao quadrado</b> (mínimos quadrados) — tem fórmula fechada, resolve num passo. É a mais interpretável: dá para ler o efeito de cada KPI.",
        en: "Picks the weights that <b>minimize the sum of squared errors</b> (least squares) — closed-form, solved in one step. The most interpretable: you can read each KPI's effect.",
        es: "Elige los pesos que <b>minimizan la suma de errores al cuadrado</b> (mínimos cuadrados) — fórmula cerrada, se resuelve en un paso. La más interpretable: se lee el efecto de cada KPI.",
        fr: "Choisit les poids qui <b>minimisent la somme des erreurs au carré</b> (moindres carrés) — formule fermée, résolue en une étape. La plus interprétable : on lit l'effet de chaque KPI.",
      },
    },
    ridge: {
      ic: "🧲",
      nome: { pt: "Ridge", en: "Ridge", es: "Ridge", fr: "Ridge" },
      tag: { pt: "linear regularizado", en: "regularized linear", es: "lineal regularizado", fr: "linéaire régularisé" },
      como: {
        pt: "É a Regressão Linear com um <b>freio</b>: penaliza pesos grandes para não “decorar” o ruído (regularização L2).",
        en: "Linear Regression with a <b>brake</b>: it penalizes large weights so it doesn't “memorize” noise (L2 regularization).",
        es: "Es la Regresión Lineal con un <b>freno</b>: penaliza pesos grandes para no “memorizar” el ruido (regularización L2).",
        fr: "La régression linéaire avec un <b>frein</b> : pénalise les gros poids pour ne pas « mémoriser » le bruit (régularisation L2).",
      },
      dados: {
        pt: "Mesmas amostras da linear, mas o ajuste é puxado para pesos menores e mais estáveis.",
        en: "Same samples as linear, but the fit is pulled toward smaller, more stable weights.",
        es: "Las mismas muestras que la lineal, pero el ajuste se lleva hacia pesos menores y más estables.",
        fr: "Mêmes données que la linéaire, mais l'ajustement tend vers des poids plus petits et stables.",
      },
      calc: {
        pt: "Minimiza <b>erro² + α·Σβ²</b>. O α é a força do freio: 0 = linear pura; alto = pesos encolhem. Ajuda quando os KPIs são correlacionados entre si.",
        en: "Minimizes <b>error² + α·Σβ²</b>. α is the brake strength: 0 = plain linear; high = weights shrink. Helps when KPIs are correlated with each other.",
        es: "Minimiza <b>error² + α·Σβ²</b>. α es la fuerza del freno: 0 = lineal pura; alto = los pesos encogen. Ayuda cuando los KPIs están correlacionados.",
        fr: "Minimise <b>erreur² + α·Σβ²</b>. α est la force du frein : 0 = linéaire pure ; élevé = les poids rétrécissent. Utile quand les KPI sont corrélés.",
      },
    },
    tree: {
      ic: "🌳",
      nome: { pt: "Árvore de Decisão", en: "Decision Tree", es: "Árbol de Decisión", fr: "Arbre de décision" },
      tag: { pt: "baseada em árvore", en: "tree-based", es: "basado en árbol", fr: "à base d'arbre" },
      como: {
        pt: "Faz uma sequência de perguntas sim/não sobre os KPIs (“SINR > 12?”), dividindo os dados em ramos até chegar a uma <b>folha</b> com a resposta.",
        en: "Asks a sequence of yes/no questions about the KPIs (“SINR > 12?”), splitting the data into branches until a <b>leaf</b> gives the answer.",
        es: "Hace una secuencia de preguntas sí/no sobre los KPIs (“¿SINR > 12?”), dividiendo los datos en ramas hasta una <b>hoja</b> con la respuesta.",
        fr: "Pose une suite de questions oui/non sur les KPI (« SINR > 12 ? »), divisant les données en branches jusqu'à une <b>feuille</b> qui donne la réponse.",
      },
      dados: {
        pt: "Usa as amostras para escolher, em cada nó, o KPI e o <b>limiar de corte</b> que melhor separam os casos. Não precisa normalizar.",
        en: "Uses the samples to choose, at each node, the KPI and the <b>split threshold</b> that best separate the cases. No scaling needed.",
        es: "Usa las muestras para elegir, en cada nodo, el KPI y el <b>umbral de corte</b> que mejor separan los casos. No requiere normalizar.",
        fr: "Utilise les données pour choisir, à chaque nœud, le KPI et le <b>seuil de coupe</b> qui séparent le mieux les cas. Pas besoin de normaliser.",
      },
      calc: {
        pt: "Em regressão, cada folha devolve a <b>média</b> do alvo dos exemplos que caíram nela; escolhe os cortes que mais reduzem a variância (na classificação, a impureza/Gini). Capta não linearidades e degraus, mas sozinha superajusta fácil.",
        en: "In regression, each leaf returns the <b>average</b> target of the examples that fell there; it picks the splits that most reduce variance (impurity/Gini in classification). Captures nonlinearities and steps, but alone it overfits easily.",
        es: "En regresión, cada hoja devuelve la <b>media</b> del objetivo de los ejemplos que cayeron allí; elige los cortes que más reducen la varianza (impureza/Gini en clasificación). Capta no linealidades y escalones, pero sola sobreajusta.",
        fr: "En régression, chaque feuille renvoie la <b>moyenne</b> de la cible des exemples qui y sont tombés ; elle choisit les coupes qui réduisent le plus la variance (impureté/Gini en classification). Capte les non-linéarités, mais seule elle surapprend vite.",
      },
    },
    rf: {
      ic: "🌲",
      nome: { pt: "Random Forest", en: "Random Forest", es: "Random Forest", fr: "Random Forest" },
      tag: { pt: "ensemble · bagging", en: "ensemble · bagging", es: "ensemble · bagging", fr: "ensemble · bagging" },
      como: {
        pt: "<b>Muitas árvores</b> treinadas em paralelo, cada uma vendo um sorteio aleatório dos dados e das features; a resposta final é a <b>média</b> (regressão) ou o <b>voto</b> (classificação).",
        en: "<b>Many trees</b> trained in parallel, each seeing a random draw of the data and features; the final answer is the <b>average</b> (regression) or the <b>vote</b> (classification).",
        es: "<b>Muchos árboles</b> entrenados en paralelo, cada uno viendo un sorteo aleatorio de datos y variables; la respuesta final es la <b>media</b> (regresión) o el <b>voto</b> (clasificación).",
        fr: "<b>Beaucoup d'arbres</b> entraînés en parallèle, chacun voyant un tirage aléatoire des données et des variables ; la réponse finale est la <b>moyenne</b> (régression) ou le <b>vote</b> (classification).",
      },
      dados: {
        pt: "Cada árvore usa uma reamostragem (bootstrap) das amostras — a diversidade entre elas reduz o erro.",
        en: "Each tree uses a resampling (bootstrap) of the data — the diversity between them reduces error.",
        es: "Cada árbol usa un remuestreo (bootstrap) de las muestras — la diversidad entre ellos reduce el error.",
        fr: "Chaque arbre utilise un rééchantillonnage (bootstrap) des données — leur diversité réduit l'erreur.",
      },
      calc: {
        pt: "Treina N árvores independentes e <b>agrega</b>. Robusto e preciso; a contrapartida é o tamanho (guarda todas as árvores — pode passar de vários MB).",
        en: "Trains N independent trees and <b>aggregates</b>. Robust and accurate; the trade-off is size (it stores every tree — can exceed several MB).",
        es: "Entrena N árboles independientes y <b>agrega</b>. Robusto y preciso; la contrapartida es el tamaño (guarda todos los árboles — puede superar varios MB).",
        fr: "Entraîne N arbres indépendants et <b>agrège</b>. Robuste et précis ; le compromis est la taille (il garde tous les arbres — plusieurs Mo possibles).",
      },
    },
    gb: {
      ic: "🚀",
      nome: { pt: "Gradient Boosting", en: "Gradient Boosting", es: "Gradient Boosting", fr: "Gradient Boosting" },
      tag: { pt: "ensemble · boosting", en: "ensemble · boosting", es: "ensemble · boosting", fr: "ensemble · boosting" },
      como: {
        pt: "Árvores <b>em sequência</b>: cada nova árvore corrige o <b>erro (resíduo)</b> que o conjunto das anteriores ainda comete.",
        en: "Trees <b>in sequence</b>: each new tree corrects the <b>error (residual)</b> the previous ones still make.",
        es: "Árboles <b>en secuencia</b>: cada nuevo árbol corrige el <b>error (residuo)</b> que aún cometen los anteriores.",
        fr: "Arbres <b>en séquence</b> : chaque nouvel arbre corrige l'<b>erreur (résidu)</b> que les précédents commettent encore.",
      },
      dados: {
        pt: "A cada rodada, dá mais atenção aos exemplos onde o modelo ainda erra mais.",
        en: "Each round, it pays more attention to the examples the model still gets most wrong.",
        es: "En cada ronda, presta más atención a los ejemplos donde el modelo aún falla más.",
        fr: "À chaque tour, il porte plus d'attention aux exemples où le modèle se trompe le plus.",
      },
      calc: {
        pt: "Soma as árvores passo a passo, cada uma escalada por uma <b>taxa de aprendizado</b>, seguindo o gradiente da perda. É o “primo” do XGBoost — costuma ser o mais preciso em dados tabulares como os KPIs.",
        en: "Adds trees step by step, each scaled by a <b>learning rate</b>, following the gradient of the loss. It's XGBoost's “cousin” — usually the most accurate on tabular data like KPIs.",
        es: "Suma los árboles paso a paso, cada uno escalado por una <b>tasa de aprendizaje</b>, siguiendo el gradiente de la pérdida. Es el “primo” de XGBoost — suele ser el más preciso en datos tabulares como los KPIs.",
        fr: "Ajoute les arbres pas à pas, chacun mis à l'échelle par un <b>taux d'apprentissage</b>, en suivant le gradient de la perte. C'est le « cousin » de XGBoost — souvent le plus précis sur des données tabulaires comme les KPI.",
      },
    },
    knn: {
      ic: "👥",
      nome: { pt: "k-NN (k vizinhos)", en: "k-NN (k neighbors)", es: "k-NN (k vecinos)", fr: "k-NN (k voisins)" },
      tag: { pt: "por vizinhança", en: "by proximity", es: "por vecindad", fr: "par voisinage" },
      como: {
        pt: "Para prever, olha os <b>k exemplos mais parecidos</b> (mais próximos em distância) e responde a média deles (regressão) ou a classe mais comum (classificação).",
        en: "To predict, it looks at the <b>k most similar examples</b> (nearest in distance) and returns their average (regression) or their most common class (classification).",
        es: "Para predecir, mira los <b>k ejemplos más parecidos</b> (más cercanos en distancia) y responde su media (regresión) o la clase más común (clasificación).",
        fr: "Pour prédire, il regarde les <b>k exemples les plus semblables</b> (les plus proches) et renvoie leur moyenne (régression) ou leur classe majoritaire (classification).",
      },
      dados: {
        pt: "Não “treina”: <b>guarda todas</b> as amostras e compara na hora da previsão. Por isso é sensível à escala — os KPIs entram padronizados.",
        en: "It doesn't “train”: it <b>stores every</b> sample and compares at prediction time. That's why it's scale-sensitive — KPIs go in standardized.",
        es: "No “entrena”: <b>guarda todas</b> las muestras y compara al predecir. Por eso es sensible a la escala — los KPIs entran estandarizados.",
        fr: "Il n'« entraîne » pas : il <b>stocke toutes</b> les données et compare au moment de la prédiction. D'où sa sensibilité à l'échelle — les KPI sont standardisés.",
      },
      calc: {
        pt: "Mede a <b>distância</b> (ex.: euclidiana) do caso novo a cada ponto, pega os k menores e agrega. Simples e intuitivo, mas fica lento quando há muitos dados.",
        en: "Measures the <b>distance</b> (e.g. Euclidean) from the new case to every point, takes the k smallest and aggregates. Simple and intuitive, but slow with lots of data.",
        es: "Mide la <b>distancia</b> (p. ej. euclidiana) del caso nuevo a cada punto, toma las k menores y agrega. Simple e intuitivo, pero lento con muchos datos.",
        fr: "Mesure la <b>distance</b> (ex. euclidienne) du nouveau cas à chaque point, prend les k plus petites et agrège. Simple et intuitif, mais lent avec beaucoup de données.",
      },
    },
    svr: {
      ic: "📐",
      nome: { pt: "SVR (RBF)", en: "SVR (RBF)", es: "SVR (RBF)", fr: "SVR (RBF)" },
      tag: { pt: "margem · kernel", en: "margin · kernel", es: "margen · kernel", fr: "marge · noyau" },
      como: {
        pt: "Ajusta uma função que passa dentro de um <b>“tubo” de tolerância</b> ao redor dos pontos; só os que ficam fora do tubo (os <b>vetores de suporte</b>) moldam o resultado.",
        en: "Fits a function that stays inside a <b>tolerance “tube”</b> around the points; only those outside the tube (the <b>support vectors</b>) shape the result.",
        es: "Ajusta una función que pasa dentro de un <b>“tubo” de tolerancia</b> alrededor de los puntos; solo los que quedan fuera (los <b>vectores de soporte</b>) moldean el resultado.",
        fr: "Ajuste une fonction qui reste dans un <b>« tube » de tolérance</b> autour des points ; seuls ceux hors du tube (les <b>vecteurs de support</b>) façonnent le résultat.",
      },
      dados: {
        pt: "Usa um <b>kernel</b> (RBF) para medir semelhança entre amostras, o que permite curvas sem criar coordenadas novas (“truque do kernel”).",
        en: "Uses a <b>kernel</b> (RBF) to measure similarity between samples, allowing curves without building new coordinates (the “kernel trick”).",
        es: "Usa un <b>kernel</b> (RBF) para medir la semejanza entre muestras, permitiendo curvas sin crear nuevas coordenadas (“truco del kernel”).",
        fr: "Utilise un <b>noyau</b> (RBF) pour mesurer la similarité entre données, ce qui permet des courbes sans créer de nouvelles coordonnées (« astuce du noyau »).",
      },
      calc: {
        pt: "Otimiza para caber o máximo de pontos no tubo com a função mais “lisa” possível; <b>C</b> (tolerância) e <b>γ</b> (flexibilidade) controlam o ajuste. Preciso, mas a inferência custa mais (compara com os vetores de suporte).",
        en: "Optimizes to fit as many points in the tube as possible with the “smoothest” function; <b>C</b> (tolerance) and <b>γ</b> (flexibility) tune it. Accurate, but inference costs more (it compares against the support vectors).",
        es: "Optimiza para meter el máximo de puntos en el tubo con la función más “suave”; <b>C</b> (tolerancia) y <b>γ</b> (flexibilidad) ajustan. Preciso, pero la inferencia cuesta más (compara con los vectores de soporte).",
        fr: "Optimise pour faire tenir un maximum de points dans le tube avec la fonction la plus « lisse » ; <b>C</b> (tolérance) et <b>γ</b> (flexibilité) règlent. Précis, mais l'inférence coûte plus (comparaison aux vecteurs de support).",
      },
    },
    mlp: {
      ic: "🧠",
      nome: { pt: "MLP · Rede Neural (a DNN do artigo)", en: "MLP · Neural Net (the paper's DNN)", es: "MLP · Red Neuronal (la DNN del artículo)", fr: "MLP · Réseau de neurones (le DNN de l'article)" },
      tag: { pt: "rede neural", en: "neural network", es: "red neuronal", fr: "réseau de neurones" },
      como: {
        pt: "Camadas de <b>neurônios</b>: cada um faz uma soma ponderada + uma função não linear (ReLU), empilhadas para aprender relações <b>curvas</b> entre KPIs e alvo.",
        en: "Layers of <b>neurons</b>: each does a weighted sum + a nonlinear function (ReLU), stacked to learn <b>curved</b> relations between KPIs and target.",
        es: "Capas de <b>neuronas</b>: cada una hace una suma ponderada + una función no lineal (ReLU), apiladas para aprender relaciones <b>curvas</b> entre KPIs y objetivo.",
        fr: "Des couches de <b>neurones</b> : chacun fait une somme pondérée + une fonction non linéaire (ReLU), empilées pour apprendre des relations <b>courbes</b> entre KPI et cible.",
      },
      dados: {
        pt: "Ajusta os pesos passando os dados <b>muitas vezes</b> (épocas), em mini-lotes; precisa de bastante dado e KPIs padronizados.",
        en: "Adjusts the weights by passing the data <b>many times</b> (epochs), in mini-batches; needs plenty of data and standardized KPIs.",
        es: "Ajusta los pesos pasando los datos <b>muchas veces</b> (épocas), en mini-lotes; necesita bastantes datos y KPIs estandarizados.",
        fr: "Ajuste les poids en passant les données <b>plusieurs fois</b> (époques), en mini-lots ; il faut beaucoup de données et des KPI standardisés.",
      },
      calc: {
        pt: "<b>Forward</b> (prevê) → mede o erro (MSE) → <b>backpropagation</b> ajusta cada peso na direção que reduz o erro (otimizador Adam). É a DNN <i>instance</i> do artigo (R² ~0,84): ótima com muitos dados, fraca com poucos.",
        en: "<b>Forward</b> (predict) → measure the error (MSE) → <b>backpropagation</b> nudges each weight toward less error (Adam optimizer). It's the paper's <i>instance</i> DNN (R² ~0.84): great with lots of data, weak with little.",
        es: "<b>Forward</b> (predice) → mide el error (MSE) → <b>backpropagation</b> ajusta cada peso hacia menos error (optimizador Adam). Es la DNN <i>instance</i> del artículo (R² ~0,84): excelente con muchos datos, débil con pocos.",
        fr: "<b>Forward</b> (prédit) → mesure l'erreur (MSE) → <b>rétropropagation</b> pousse chaque poids vers moins d'erreur (optimiseur Adam). C'est le DNN <i>instance</i> de l'article (R² ~0,84) : excellent avec beaucoup de données, faible avec peu.",
      },
    },
    logistic: {
      ic: "⚖️",
      nome: { pt: "Regressão Logística", en: "Logistic Regression", es: "Regresión Logística", fr: "Régression logistique" },
      tag: { pt: "linear · classificação", en: "linear · classification", es: "lineal · clasificación", fr: "linéaire · classification" },
      como: {
        pt: "Soma ponderada dos KPIs passada por uma <b>curva em “S”</b> (sigmoide/softmax) → vira a <b>probabilidade</b> de cada classe; vence a maior.",
        en: "A weighted sum of the KPIs passed through an <b>“S” curve</b> (sigmoid/softmax) → becomes the <b>probability</b> of each class; the highest wins.",
        es: "Suma ponderada de los KPIs pasada por una <b>curva en “S”</b> (sigmoide/softmax) → se vuelve la <b>probabilidad</b> de cada clase; gana la mayor.",
        fr: "Somme pondérée des KPI passée dans une <b>courbe en « S »</b> (sigmoïde/softmax) → devient la <b>probabilité</b> de chaque classe ; la plus grande gagne.",
      },
      dados: {
        pt: "Usa todas as amostras <b>rotuladas</b> para ajustar os pesos que melhor separam as classes.",
        en: "Uses all <b>labeled</b> samples to fit the weights that best separate the classes.",
        es: "Usa todas las muestras <b>etiquetadas</b> para ajustar los pesos que mejor separan las clases.",
        fr: "Utilise toutes les données <b>étiquetées</b> pour ajuster les poids qui séparent le mieux les classes.",
      },
      calc: {
        pt: "Minimiza a <b>log-perda</b> (máxima verossimilhança): os pesos que fazem as probabilidades previstas baterem com os rótulos. Interpretável e rápida — por isso é a que roda ao vivo no “Mexe”.",
        en: "Minimizes the <b>log-loss</b> (maximum likelihood): the weights that make predicted probabilities match the labels. Interpretable and fast — that's why it runs live in the sandbox.",
        es: "Minimiza la <b>log-pérdida</b> (máxima verosimilitud): los pesos que hacen que las probabilidades predichas coincidan con las etiquetas. Interpretable y rápida — por eso corre en vivo en el “Prueba”.",
        fr: "Minimise la <b>log-perte</b> (maximum de vraisemblance) : les poids qui font coïncider les probabilités prédites avec les étiquettes. Interprétable et rapide — d'où son exécution en direct.",
      },
    },
    nb: {
      ic: "🎲",
      nome: { pt: "Naive Bayes", en: "Naive Bayes", es: "Naive Bayes", fr: "Naive Bayes" },
      tag: { pt: "probabilístico", en: "probabilistic", es: "probabilístico", fr: "probabiliste" },
      como: {
        pt: "Usa o <b>Teorema de Bayes</b>: combina a probabilidade de cada classe com a de cada KPI, supondo (ingenuamente) que os KPIs são independentes.",
        en: "Uses <b>Bayes' Theorem</b>: combines each class's probability with each KPI's, (naively) assuming the KPIs are independent.",
        es: "Usa el <b>Teorema de Bayes</b>: combina la probabilidad de cada clase con la de cada KPI, suponiendo (ingenuamente) que los KPIs son independientes.",
        fr: "Utilise le <b>théorème de Bayes</b> : combine la probabilité de chaque classe avec celle de chaque KPI, en supposant (naïvement) les KPI indépendants.",
      },
      dados: {
        pt: "Estima, por classe, a <b>média e o desvio</b> de cada KPI (Gaussiano) a partir do treino.",
        en: "Estimates, per class, each KPI's <b>mean and spread</b> (Gaussian) from the training data.",
        es: "Estima, por clase, la <b>media y desviación</b> de cada KPI (Gaussiano) a partir del entrenamiento.",
        fr: "Estime, par classe, la <b>moyenne et l'écart</b> de chaque KPI (gaussien) à partir de l'entraînement.",
      },
      calc: {
        pt: "Multiplica as probabilidades de cada KPI dado a classe e escolhe a <b>classe mais provável</b>. Muito rápido; a suposição de independência limita quando os KPIs são correlacionados.",
        en: "Multiplies the probabilities of each KPI given the class and picks the <b>most likely class</b>. Very fast; the independence assumption limits it when KPIs are correlated.",
        es: "Multiplica las probabilidades de cada KPI dada la clase y elige la <b>clase más probable</b>. Muy rápido; la independencia limita cuando los KPIs están correlacionados.",
        fr: "Multiplie les probabilités de chaque KPI sachant la classe et choisit la <b>classe la plus probable</b>. Très rapide ; l'hypothèse d'indépendance limite quand les KPI sont corrélés.",
      },
    },
    svm: {
      ic: "📐",
      nome: { pt: "SVM (RBF)", en: "SVM (RBF)", es: "SVM (RBF)", fr: "SVM (RBF)" },
      tag: { pt: "margem · kernel", en: "margin · kernel", es: "margen · kernel", fr: "marge · noyau" },
      como: {
        pt: "Acha a fronteira que separa as classes com a <b>maior margem</b> possível; com kernel RBF, a fronteira pode ser <b>curva</b>.",
        en: "Finds the boundary that separates the classes with the <b>largest margin</b> possible; with an RBF kernel, the boundary can be <b>curved</b>.",
        es: "Halla la frontera que separa las clases con el <b>mayor margen</b> posible; con kernel RBF, la frontera puede ser <b>curva</b>.",
        fr: "Trouve la frontière qui sépare les classes avec la <b>plus grande marge</b> ; avec un noyau RBF, la frontière peut être <b>courbe</b>.",
      },
      dados: {
        pt: "Só os pontos na borda (os <b>vetores de suporte</b>) definem a fronteira; usa o kernel para medir semelhança.",
        en: "Only the border points (the <b>support vectors</b>) define the boundary; it uses the kernel to measure similarity.",
        es: "Solo los puntos del borde (los <b>vectores de soporte</b>) definen la frontera; usa el kernel para medir semejanza.",
        fr: "Seuls les points de bord (les <b>vecteurs de support</b>) définissent la frontière ; il utilise le noyau pour la similarité.",
      },
      calc: {
        pt: "Maximiza a margem penalizando os erros (<b>C</b>) e curvando a fronteira (<b>γ</b>). Forte em fronteiras complexas; a inferência é mais cara.",
        en: "Maximizes the margin while penalizing errors (<b>C</b>) and curving the boundary (<b>γ</b>). Strong on complex boundaries; inference is pricier.",
        es: "Maximiza el margen penalizando los errores (<b>C</b>) y curvando la frontera (<b>γ</b>). Fuerte en fronteras complejas; la inferencia cuesta más.",
        fr: "Maximise la marge en pénalisant les erreurs (<b>C</b>) et en courbant la frontière (<b>γ</b>). Forte sur les frontières complexes ; l'inférence coûte plus.",
      },
    },
    kmeans: {
      ic: "🎯",
      nome: { pt: "k-means", en: "k-means", es: "k-means", fr: "k-means" },
      tag: { pt: "clustering · centróide", en: "clustering · centroid", es: "clustering · centroide", fr: "clustering · centroïde" },
      como: {
        pt: "Escolhe <b>k centros</b> e agrupa cada ponto ao centro mais próximo; repete movendo os centros até estabilizar.",
        en: "Picks <b>k centers</b> and assigns each point to the nearest one; repeats, moving the centers until they stabilize.",
        es: "Elige <b>k centros</b> y asigna cada punto al más cercano; repite, moviendo los centros hasta estabilizar.",
        fr: "Choisit <b>k centres</b> et rattache chaque point au plus proche ; répète en déplaçant les centres jusqu'à stabilisation.",
      },
      dados: {
        pt: "Sem rótulo — usa só os KPIs para achar <b>grupos naturais</b> de células parecidas.",
        en: "No labels — uses only the KPIs to find <b>natural groups</b> of similar cells.",
        es: "Sin etiqueta — usa solo los KPIs para hallar <b>grupos naturales</b> de celdas parecidas.",
        fr: "Sans étiquette — utilise seulement les KPI pour trouver des <b>groupes naturels</b> de cellules semblables.",
      },
      calc: {
        pt: "Alterna (1) atribuir cada ponto ao centróide mais próximo e (2) recalcular o centróide como a <b>média</b> do grupo, minimizando a distância interna. Você precisa dizer o k.",
        en: "Alternates (1) assigning each point to the nearest centroid and (2) recomputing the centroid as the group's <b>average</b>, minimizing within-group distance. You must set k.",
        es: "Alterna (1) asignar cada punto al centroide más cercano y (2) recalcular el centroide como la <b>media</b> del grupo, minimizando la distancia interna. Debes indicar k.",
        fr: "Alterne (1) affecter chaque point au centroïde le plus proche et (2) recalculer le centroïde comme la <b>moyenne</b> du groupe, en minimisant la distance interne. Il faut fixer k.",
      },
    },
    dbscan: {
      ic: "🌐",
      nome: { pt: "DBSCAN", en: "DBSCAN", es: "DBSCAN", fr: "DBSCAN" },
      tag: { pt: "clustering · densidade", en: "clustering · density", es: "clustering · densidad", fr: "clustering · densité" },
      como: {
        pt: "Agrupa pontos que estão <b>densamente juntos</b>; quem fica isolado vira <b>ruído/anomalia</b>.",
        en: "Groups points that are <b>densely packed</b>; whatever is isolated becomes <b>noise/anomaly</b>.",
        es: "Agrupa puntos que están <b>densamente juntos</b>; lo que queda aislado se vuelve <b>ruido/anomalía</b>.",
        fr: "Regroupe les points <b>densément proches</b> ; ce qui reste isolé devient <b>bruit/anomalie</b>.",
      },
      dados: {
        pt: "Usa vizinhança — um raio <b>ε</b> e um mínimo de pontos — e <b>não</b> precisa dizer o número de grupos.",
        en: "Uses neighborhoods — a radius <b>ε</b> and a minimum number of points — and does <b>not</b> need the number of groups.",
        es: "Usa vecindad — un radio <b>ε</b> y un mínimo de puntos — y <b>no</b> necesita el número de grupos.",
        fr: "Utilise le voisinage — un rayon <b>ε</b> et un minimum de points — et n'a <b>pas</b> besoin du nombre de groupes.",
      },
      calc: {
        pt: "Expande um cluster a partir de pontos com vizinhos suficientes dentro de ε. Bom para formas irregulares e para achar outliers de graça.",
        en: "Grows a cluster from points with enough neighbors within ε. Good for irregular shapes and for finding outliers for free.",
        es: "Expande un clúster desde puntos con suficientes vecinos dentro de ε. Bueno para formas irregulares y para hallar outliers gratis.",
        fr: "Étend un cluster depuis les points ayant assez de voisins dans ε. Bon pour les formes irrégulières et pour trouver les valeurs aberrantes gratuitement.",
      },
    },
    agg: {
      ic: "🌿",
      nome: { pt: "Clustering Hierárquico", en: "Hierarchical Clustering", es: "Clustering Jerárquico", fr: "Clustering hiérarchique" },
      tag: { pt: "aglomerativo", en: "agglomerative", es: "aglomerativo", fr: "agglomératif" },
      como: {
        pt: "Começa com cada ponto sozinho e vai <b>juntando os pares mais próximos</b>, formando uma árvore (dendrograma).",
        en: "Starts with each point alone and keeps <b>merging the closest pairs</b>, building a tree (dendrogram).",
        es: "Empieza con cada punto solo y va <b>uniendo los pares más cercanos</b>, formando un árbol (dendrograma).",
        fr: "Part de chaque point seul et <b>fusionne les paires les plus proches</b>, formant un arbre (dendrogramme).",
      },
      dados: {
        pt: "Usa distâncias entre grupos (o critério de <b>ligação</b>) para decidir o que fundir.",
        en: "Uses distances between groups (the <b>linkage</b> criterion) to decide what to merge.",
        es: "Usa distancias entre grupos (el criterio de <b>enlace</b>) para decidir qué fusionar.",
        fr: "Utilise les distances entre groupes (le critère de <b>liaison</b>) pour décider quoi fusionner.",
      },
      calc: {
        pt: "A cada passo funde os 2 grupos mais próximos até sobrar o número desejado; dá para “cortar” a árvore em qualquer nível e escolher quantos grupos ver.",
        en: "At each step it merges the 2 closest groups until the desired number remains; you can “cut” the tree at any level and choose how many groups to see.",
        es: "En cada paso fusiona los 2 grupos más cercanos hasta el número deseado; puedes “cortar” el árbol a cualquier nivel y elegir cuántos grupos ver.",
        fr: "À chaque étape, il fusionne les 2 groupes les plus proches jusqu'au nombre voulu ; on peut « couper » l'arbre à tout niveau et choisir combien de groupes voir.",
      },
    },
    isoforest: {
      ic: "🚨",
      nome: { pt: "Isolation Forest", en: "Isolation Forest", es: "Isolation Forest", fr: "Isolation Forest" },
      tag: { pt: "detecção de anomalia", en: "anomaly detection", es: "detección de anomalías", fr: "détection d'anomalies" },
      como: {
        pt: "Árvores com <b>cortes aleatórios</b> que “isolam” cada ponto; anomalias são isoladas com <b>poucos cortes</b> (ficam mais sozinhas).",
        en: "Trees with <b>random cuts</b> that “isolate” each point; anomalies get isolated with <b>few cuts</b> (they stand more alone).",
        es: "Árboles con <b>cortes aleatorios</b> que “aíslan” cada punto; las anomalías se aíslan con <b>pocos cortes</b> (quedan más solas).",
        fr: "Des arbres à <b>coupes aléatoires</b> qui « isolent » chaque point ; les anomalies sont isolées en <b>peu de coupes</b> (plus seules).",
      },
      dados: {
        pt: "Sem rótulo — mede quão fácil é separar cada ponto do resto.",
        en: "No labels — measures how easy it is to separate each point from the rest.",
        es: "Sin etiqueta — mide qué tan fácil es separar cada punto del resto.",
        fr: "Sans étiquette — mesure la facilité à séparer chaque point du reste.",
      },
      calc: {
        pt: "Quanto <b>menor a profundidade média</b> para isolar um ponto, maior o escore de anomalia. Rápido e escala bem para muitos KPIs.",
        en: "The <b>lower the average depth</b> to isolate a point, the higher its anomaly score. Fast and scales well to many KPIs.",
        es: "Cuanto <b>menor la profundidad media</b> para aislar un punto, mayor su puntuación de anomalía. Rápido y escala bien con muchos KPIs.",
        fr: "Plus la <b>profondeur moyenne</b> pour isoler un point est faible, plus son score d'anomalie est élevé. Rapide et passe bien à l'échelle.",
      },
    },
    pca: {
      ic: "🧭",
      nome: { pt: "PCA", en: "PCA", es: "PCA", fr: "PCA" },
      tag: { pt: "redução de dimensão", en: "dimensionality reduction", es: "reducción de dimensión", fr: "réduction de dimension" },
      como: {
        pt: "Acha novas <b>direções</b> (componentes) que capturam a maior variação dos dados, resumindo muitos KPIs em poucos.",
        en: "Finds new <b>directions</b> (components) that capture the most variation in the data, summarizing many KPIs into a few.",
        es: "Halla nuevas <b>direcciones</b> (componentes) que capturan la mayor variación de los datos, resumiendo muchos KPIs en pocos.",
        fr: "Trouve de nouvelles <b>directions</b> (composantes) qui capturent le plus de variation, résumant beaucoup de KPI en quelques-uns.",
      },
      dados: {
        pt: "Usa a <b>covariância</b> entre os KPIs para achar os eixos de maior espalhamento.",
        en: "Uses the <b>covariance</b> between KPIs to find the axes of greatest spread.",
        es: "Usa la <b>covarianza</b> entre los KPIs para hallar los ejes de mayor dispersión.",
        fr: "Utilise la <b>covariance</b> entre KPI pour trouver les axes de plus grande dispersion.",
      },
      calc: {
        pt: "Calcula autovetores/autovalores da matriz de covariância e <b>projeta</b> os dados nos primeiros componentes (PC1, PC2…), preservando o máximo de variância. Não é preditor — é pré-processamento/visualização.",
        en: "Computes eigenvectors/eigenvalues of the covariance matrix and <b>projects</b> the data onto the first components (PC1, PC2…), preserving the most variance. Not a predictor — it's preprocessing/visualization.",
        es: "Calcula autovectores/autovalores de la matriz de covarianza y <b>proyecta</b> los datos en los primeros componentes (PC1, PC2…), preservando la máxima varianza. No es predictor — es preprocesamiento/visualización.",
        fr: "Calcule les vecteurs/valeurs propres de la matrice de covariance et <b>projette</b> les données sur les premières composantes (PC1, PC2…), en préservant le plus de variance. Pas un prédicteur — du prétraitement/de la visualisation.",
      },
    },
  };

  const CSS = `
  .mdd-wrap{display:flex;flex-direction:column;gap:8px;margin-top:12px}
  .mdd{border:1px solid var(--line,#dfe5ec);border-radius:10px;overflow:hidden;background:var(--card2,rgba(127,127,127,.03))}
  .mdd>summary{cursor:pointer;list-style:none;padding:11px 14px;display:flex;align-items:center;gap:9px;font-size:14px;user-select:none}
  .mdd>summary::-webkit-details-marker{display:none}
  .mdd>summary::after{content:"▸";margin-left:auto;color:var(--sub,#8b97a6);transition:transform .15s}
  .mdd[open]>summary::after{transform:rotate(90deg)}
  .mdd>summary:hover{background:rgba(127,127,127,.06)}
  .mdd-ic{font-size:17px}
  .mdd-tag{font-size:10.5px;letter-spacing:.4px;color:var(--sub,#8b97a6);border:1px solid var(--line,#dfe5ec);border-radius:20px;padding:1px 8px}
  .mdd-body{padding:2px 14px 12px 14px;display:flex;flex-direction:column;gap:8px;font-size:13px;line-height:1.5}
  .mdd-row{display:grid;grid-template-columns:150px 1fr;gap:10px;align-items:start}
  .mdd-k{font-size:11px;letter-spacing:.6px;text-transform:uppercase;color:var(--accent,#1f6fe5);font-weight:700;padding-top:2px}
  @media(max-width:560px){.mdd-row{grid-template-columns:1fr;gap:2px}}
  `;

  function lng() {
    try { if (window.LABI18N && window.LABI18N.lang && M.linear.nome[window.LABI18N.lang]) return window.LABI18N.lang; } catch (e) {}
    return "pt";
  }
  function tr(o, g) { return (o && (o[g] != null ? o[g] : o.pt)) || ""; }

  function card(k, g) {
    const m = M[k];
    if (!m) return "";
    return `<details class="mdd"><summary><span class="mdd-ic">${m.ic}</span>`
      + `<b>${tr(m.nome, g)}</b> <span class="mdd-tag">${tr(m.tag, g)}</span></summary>`
      + `<div class="mdd-body">`
      + `<div class="mdd-row"><span class="mdd-k">${L.como[g]}</span><span>${tr(m.como, g)}</span></div>`
      + `<div class="mdd-row"><span class="mdd-k">${L.dados[g]}</span><span>${tr(m.dados, g)}</span></div>`
      + `<div class="mdd-row"><span class="mdd-k">${L.calc[g]}</span><span>${tr(m.calc, g)}</span></div>`
      + `</div></details>`;
  }

  function render() {
    const hosts = document.querySelectorAll("[data-model-deepdive]");
    if (!hosts.length) return;
    if (!document.getElementById("mdd-css")) {
      const s = document.createElement("style");
      s.id = "mdd-css"; s.textContent = CSS; document.head.appendChild(s);
    }
    const g = lng();
    hosts.forEach(h => {
      const keys = (h.getAttribute("data-model-deepdive") || "")
        .split(",").map(s => s.trim()).filter(Boolean);
      // preserva quais <details> estavam abertos ao trocar de idioma
      const open = new Set([...h.querySelectorAll("details[open]")].map((d, i) => i));
      h.innerHTML = `<div class="mdd-wrap">${keys.map(k => card(k, g)).join("")}</div>`;
      [...h.querySelectorAll("details")].forEach((d, i) => { if (open.has(i)) d.open = true; });
    });
  }

  function boot() {
    render();
    try { if (window.LABI18N && window.LABI18N.onChange) window.LABI18N.onChange(render); } catch (e) {}
  }
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
