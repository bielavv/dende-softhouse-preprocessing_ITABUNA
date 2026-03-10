class Statistics:

    def __init__(self, dataset):

        if not isinstance(dataset, dict):
            raise TypeError("O dataset deve ser um dicionário")

        for coluna, valores in dataset.items():
            if not isinstance(valores, list):
                raise TypeError(f"Valores da coluna '{coluna}' devem ser uma lista")

        if dataset:
            tamanhos = [len(v) for v in dataset.values()]
            if len(set(tamanhos)) > 1:
                raise ValueError("Todas as colunas devem ter o mesmo número de elementos")

        for coluna, valores in dataset.items(): 
            if valores:
                primeiro_tipo = type(valores[0])
                for valor in valores:
                    if type(valor) != primeiro_tipo:
                         raise TypeError(f"coluna '{coluna}' tem tipos misturados")
    
        self.dataset = dataset

    def mean(self, column):

        if column not in self.dataset:
            raise KeyError(f"Coluna '{column}' não existe no dataset")
        
        dados = self.dataset[column]

        if len(dados) == 0:
            raise KeyError(f"Não é possivél calcular média de uma coluna vazia")

        for i, valor in enumerate(dados):
            if not isinstance(valor, (int, float)):
                raise TypeError(
                    f" Média só pode ser calculada em colunas numéricas. "
                    f"Coluna '{column}' na posição {i}: {repr(valor)} é {type(valor).__name__}"
                )

        return sum(dados) / len(dados)
    
    def median(self, column):

      if column not in self.dataset:
            raise KeyError(f"Coluna '{column}' não existe no dataset")
    
      dados = self.dataset[column]

      if len(dados) == 0:
            raise KeyError(f"Não é possivél verificar a mediana de uma coluna vazia")
      
      if column == "priority":
        ordem = {"baixa": 1, "media": 2, "alta": 3}
        dados_ordenados = sorted(dados, key=lambda x: ordem[x])

      else:
        dados_ordenados = sorted(dados)

      total_elementos = len(dados_ordenados)
      meio = total_elementos // 2

      if total_elementos % 2 == 1:
          return dados_ordenados[meio]

      esquerda = dados_ordenados[meio - 1]
      direita = dados_ordenados[meio] 

      if isinstance(esquerda, (int, float)) and isinstance(direita, (int, float)):

         return (esquerda + direita) / 2
      
      else:

          return esquerda
          
    def mode(self, column):

      if column not in self.dataset:
            raise KeyError(f"Coluna '{column}' não existe no dataset")
    
      dados = self.dataset[column]

      if len(dados) == 0:
            raise KeyError(f"Não é possivél verificar a moda de uma coluna vazia")
      
      contagem = {}
      for valor in dados:
           if valor in contagem:
                contagem[valor] += 1
           else:
               contagem[valor] = 1

      maior_contagem = max(contagem.values())

      modas = []
      for valor, freq in contagem.items():
       if freq == maior_contagem:
        modas.append(valor)


      return modas
    
    def variance(self, column):

      if column not in self.dataset:
            raise KeyError(f"Coluna '{column}' não existe no dataset")
    
      dados = self.dataset[column]

      if len(dados) == 0:
            raise KeyError(f"Não é possivél verificar a variância de uma coluna vazia")
      
      for i, valor in enumerate(dados):
       if not isinstance(valor, (int, float)):
        raise TypeError(
            f"Variância só pode ser calculada em colunas numéricas. "
            f"Coluna '{column}' na posição {i}: {repr(valor)} é {type(valor).__name__}"
        )

      media = self.mean(column)
      soma_quadrados = sum((x - media) ** 2 for x in dados) 
      return soma_quadrados / len(dados)

    def stdev(self, column):

      if column not in self.dataset:
        raise KeyError(f"Coluna '{column}' não existe no dataset")
    
      dados = self.dataset[column]

      if len(dados) == 0:
         raise KeyError(f"Não é possivél verificar o desvio padrão de uma coluna vazia")

      for i, valor in enumerate(dados):
        if not isinstance(valor, (int, float)):
         raise TypeError(
            f"Variância só pode ser calculada em colunas numéricas. "
            f"Coluna '{column}' na posição {i}: {repr(valor)} é {type(valor).__name__}"
        )
      variancia = self.variance(column)
      return round(variancia ** 0.5, 6)

    def covariance(self, column_a, column_b):

        if column_a not in self.dataset:
          raise KeyError(f"Coluna '{column_a}' não existe no dataset")
        if column_b not in self.dataset:
          raise KeyError(f"Coluna '{column_b}' não existe no dataset")
        
        dados_a = self.dataset[column_a]
        dados_b = self.dataset[column_b]

        if len(dados_a) != len(dados_b):
         raise ValueError("Colunas devem ter o mesmo número de elementos para covariância")

        if len(dados_a) == 0:
          raise KeyError(f"Não é possivél verificar a covariância de uma coluna vazia")

        for i in range(len(dados_a)):
            if not isinstance(dados_a[i], (int, float)):
                raise TypeError(
            f"Covariância requer colunas numéricas. "
            f"Coluna '{column_a}' na posição {i}: {repr(dados_a[i])} é {type(dados_a[i]).__name__}"
        )
            if not isinstance(dados_b[i], (int, float)):
                 raise TypeError(
            f"Covariância requer colunas numéricas. "
            f"Coluna '{column_b}' na posição {i}: {repr(dados_b[i])} é {type(dados_b[i]).__name__}"
        )
            
        media_a = self.mean(column_a)
        media_b = self.mean(column_b)

        soma_produtos = sum((a - media_a) * (b - media_b) for a, b in zip(dados_a, dados_b))
        return soma_produtos / len(dados_a)

    def itemset(self, column):

        if column not in self.dataset:
          raise KeyError(f"Coluna '{column}' não existe no dataset")
        
        dados = self.dataset[column]

        conjunto_unico = set(dados)

        return conjunto_unico

    def absolute_frequency(self, column):


        if column not in self.dataset:
            raise KeyError(f"Coluna '{column}' não existe no dataset")

        dados = self.dataset[column]


        if len(dados) == 0:
          raise KeyError(f"Não é possivél verificar a frequencia absoluta de uma coluna vazia")
        
        frequencias = {}

        for item in dados:
            if item in frequencias:
                frequencias[item] += 1
            else:
                frequencias[item] = 1

        return frequencias

    def relative_frequency(self, column):

        frequencia_absoluta = self.absolute_frequency(column)
        
        total_elementos = len(self.dataset[column])

        frequencias_relativas = {}
        for item, contagem in frequencia_absoluta.items():
            frequencias_relativas[item] = contagem / total_elementos
            
        return frequencias_relativas

    def cumulative_frequency(self, column, frequency_method='absolute'):

        if frequency_method == 'relative':
            frequencias_base = self.relative_frequency(column)
        else:
            frequencias_base = self.absolute_frequency(column)

        if column == "priority":
            ordem_manual = {"baixa": 1, "media": 2, "alta": 3}
            itens_ordenados = sorted(frequencias_base.keys(), key=lambda x: ordem_manual.get(x, 0))
        else:
            itens_ordenados = sorted(frequencias_base.keys())

        frequencias_acumuladas = {}
        soma_atual = 0
        
        for item in itens_ordenados:
            soma_atual += frequencias_base[item]

            frequencias_acumuladas [item] = round(soma_atual, 4) if frequency_method == 'relative' else soma_atual

        return frequencias_acumuladas 

    def conditional_probability(self, column, value1, value2):
        
        if column not in self.dataset:
            raise KeyError(f"Coluna '{column}' não existe no dataset")
        
        dados = self.dataset[column]
        
        contagem_b = 0  
        contagem_b_a = 0

        for i in range(len(dados) - 1):
            if dados[i] == value2:
                contagem_b += 1 

                if dados[i + 1] == value1:
                    contagem_b_a += 1
    
        if contagem_b == 0:
            return 0.0 
            
        return contagem_b_a / contagem_b

    def quartiles(self, column):
        

        if column not in self.dataset:
            raise KeyError(f"Coluna '{column}' não existe no dataset")
        
        valores = self.dataset[column]

        if len(valores) == 0:
            return {"Q1": None, "Q2": None, "Q3": None}
        

        for posicao, valor in enumerate(valores):
            if not isinstance(valor, (int, float)):
                raise TypeError(
                    f"Quartis só podem ser calculados em colunas numéricas. "
                    f"Coluna '{column}' na posição {posicao} contém '{valor}' que é {type(valor).__name__}"
                )
        

        valores_ordenados = sorted(valores)
        quantidade = len(valores_ordenados)

        posicao_q1 = (quantidade - 1) * 0.25
        indice_inferior_q1 = int(posicao_q1)
        fracao_q1 = posicao_q1 - indice_inferior_q1

        if indice_inferior_q1 + 1 < quantidade:
            valor_inferior_q1 = valores_ordenados[indice_inferior_q1]
            valor_superior_q1 = valores_ordenados[indice_inferior_q1 + 1]
            q1 = valor_inferior_q1 + fracao_q1 * (valor_superior_q1 - valor_inferior_q1)
        else:
            q1 = valores_ordenados[indice_inferior_q1]
    
        posicao_q2 = (quantidade - 1) * 0.50
        indice_inferior_q2 = int(posicao_q2)
        fracao_q2 = posicao_q2 - indice_inferior_q2

        if indice_inferior_q2 + 1 < quantidade:
            valor_inferior_q2 = valores_ordenados[indice_inferior_q2]
            valor_superior_q2 = valores_ordenados[indice_inferior_q2 + 1]
            q2 = valor_inferior_q2 + fracao_q2 * (valor_superior_q2 - valor_inferior_q2)
        else:
            q2 = valores_ordenados[indice_inferior_q2]

        posicao_q3 = (quantidade - 1) * 0.75
        indice_inferior_q3 = int(posicao_q3)
        fracao_q3 = posicao_q3 - indice_inferior_q3
        
        if indice_inferior_q3 + 1 < quantidade:
            valor_inferior_q3 = valores_ordenados[indice_inferior_q3]
            valor_superior_q3 = valores_ordenados[indice_inferior_q3 + 1]
            q3 = valor_inferior_q3 + fracao_q3 * (valor_superior_q3 - valor_inferior_q3)
        else:
            q3 = valores_ordenados[indice_inferior_q3]
        

        return {"Q1": q1, "Q2": q2, "Q3": q3}

    def histogram(self, column, bins):

        if column not in self.dataset:
            raise KeyError(f"Coluna '{column}' não existe no dataset")
        
        dados = self.dataset[column]

        if len(dados) == 0:
            return {}

        for i, valor in enumerate(dados):
            if not isinstance(valor, (int, float)):
                raise TypeError(
                    f"Histograma requer coluna numérica. "
                    f"Coluna '{column}' posição {i}: {repr(valor)} é {type(valor).__name__}"
                )
        
        if bins <= 0:
            raise ValueError("Número de intervalos (bins) deve ser positivo")
        
        valor_minimo = min(dados)
        valor_maximo = max(dados)
        
        if valor_minimo == valor_maximo:
            return {(valor_minimo, valor_maximo): len(dados)}

        amplitude = (valor_maximo - valor_minimo) / bins

        intervalos = []
        for i in range(bins):
            limite_inferior = valor_minimo + i * amplitude
            limite_superior = valor_minimo + (i + 1) * amplitude
            intervalos.append((limite_inferior, limite_superior))

        histograma = {intervalo: 0 for intervalo in intervalos}
    
        for valor in dados:
            for i, (lim_inf, lim_sup) in enumerate(intervalos):
                if i == bins - 1:
                    if lim_inf <= valor <= lim_sup:
                        histograma[(lim_inf, lim_sup)] += 1
                        break
                elif lim_inf <= valor < lim_sup:
                    histograma[(lim_inf, lim_sup)] += 1
                    break
        
        return histograma