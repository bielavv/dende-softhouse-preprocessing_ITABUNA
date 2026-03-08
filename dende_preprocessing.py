from dende_statistics import Statistics
from typing import Dict, List, Set, Any

class MissingValueProcessor:
    """
    Processa valores ausentes (representados como None) no dataset.
    """
    def __init__(self, dataset: Dict[str, List[Any]]):
        self.dataset = dataset

    def _get_target_columns(self, columns: Set[str]) -> List[str]:
        """Retorna as colunas a serem processadas. Se 'columns' for vazio, retorna todas as colunas."""
        return list(columns) if columns else list(self.dataset.keys())

    def isna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Retorna um novo dataset contendo apenas as linhas que possuem
        pelo menos um valor nulo (None) em uma das colunas especificadas.
        """
        target_cols = self._get_target_columns(columns)
        num_rows = len(next(iter(self.dataset.values())))
        subset = {col: [] for col in self.dataset.keys()}
        
        for i in range(num_rows):
            if any(self.dataset[col][i] is None for col in target_cols):
                for col in self.dataset.keys():
                    subset[col].append(self.dataset[col][i])
        return subset

    def notna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Retorna um novo dataset contendo apenas as linhas que não possuem
        valores nulos (None) em nenhuma das colunas especificadas.
        """
        target_cols = self._get_target_columns(columns)
        num_rows = len(next(iter(self.dataset.values())))
        subset = {col: [] for col in self.dataset.keys()}
        
        for i in range(num_rows):
            if all(self.dataset[col][i] is not None for col in target_cols):
                for col in self.dataset.keys():
                    subset[col].append(self.dataset[col][i])
        return subset

    def fillna(self, columns: Set[str] = None, value: Any = 0) -> Dict[str, List[Any]]:
        """
        Preenche valores nulos (None) nas colunas especificadas com um valor fixo.
        Modifica o dataset da classe.
        """
        target_cols = self._get_target_columns(columns)
        for col in target_cols:
            self.dataset[col] = [value if x is None else x for x in self.dataset[col]]
        return self.dataset

    def dropna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Remove as linhas que contêm valores nulos (None) nas colunas especificadas.
        Modifica o dataset da classe.
        """
        target_cols = self._get_target_columns(columns)
        num_rows = len(next(iter(self.dataset.values())))
        indices_validos = [i for i in range(num_rows) 
                          if all(self.dataset[col][i] is not None for col in target_cols)]
        
        for col in self.dataset.keys():
            self.dataset[col] = [self.dataset[col][i] for i in indices_validos]
        return self.dataset


class Scaler:
    """
    Aplica transformações de escala em colunas numéricas do dataset.
    """
    def __init__(self, dataset: Dict[str, List[Any]], stats_obj: Statistics = None):
        self.dataset = dataset
        self.stats = stats_obj

    def _get_target_columns(self, columns: Set[str]) -> List[str]:
        return list(columns) if columns else list(self.dataset.keys())

    def minMax_scaler(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Aplica a normalização Min-Max nas colunas especificadas. Modifica o dataset.
        """
        target_cols = self._get_target_columns(columns)
        for col in target_cols:
            dados = self.dataset[col]
            v_min, v_max = min(dados), max(dados)
            diff = v_max - v_min
            self.dataset[col] = [(x - v_min) / diff if diff != 0 else 0.0 for x in dados]
        return self.dataset

    def standard_scaler(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        """
        Aplica a padronização Z-score nas colunas especificadas. Modifica o dataset.
        """
        target_cols = self._get_target_columns(columns)
        for col in target_cols:
            mu = self.stats.mean(col)
            sigma = self.stats.stdev(col)
            self.dataset[col] = [(x - mu) / sigma if sigma != 0 else 0.0 for x in self.dataset[col]]
        return self.dataset


class Encoder:
    """
    Aplica codificação em colunas categóricas.
    """
    def __init__(self, dataset: Dict[str, List[Any]]):
        self.dataset = dataset

    def label_encode(self, columns: Set[str]) -> Dict[str, List[Any]]:
        """
        Converte cada categoria em uma coluna em um número inteiro.
        Modifica o dataset.
        """
        for col in columns:
            categorias = sorted(list(set(self.dataset[col])))
            mapping = {val: i for i, val in enumerate(categorias)}
            self.dataset[col] = [mapping[v] for v in self.dataset[col]]
        return self.dataset

    def oneHot_encode(self, columns: Set[str]) -> Dict[str, List[Any]]:
        """
        Cria novas colunas binárias para cada categoria (One-Hot Encoding).
        Modifica o dataset adicionando e removendo colunas.
        """
        for col in list(columns):
            categorias = sorted(list(set(self.dataset[col])))
            original = self.dataset.pop(col)
            for cat in categorias:
                self.dataset[f"{col}_{cat}"] = [1 if x == cat else 0 for x in original]
        return self.dataset


class Preprocessing:
    """
    Classe principal que orquestra as operações de pré-processamento de dados.
    """
    def __init__(self, dataset: Dict[str, List[Any]]):
        self.dataset = dataset
        self._validate_dataset_shape()
        
        # Tentativa inicial de criar Statistics (pode falhar se houver nulos)
        try:
            self.statistics = Statistics(self.dataset)
        except:
            self.statistics = None

        self.missing_values = MissingValueProcessor(self.dataset)
        self.scaler = Scaler(self.dataset, self.statistics)
        self.encoder = Encoder(self.dataset)

    def _validate_dataset_shape(self):
        """Valida se todas as colunas têm o mesmo comprimento."""
        if not self.dataset: return
        lengths = [len(v) for v in self.dataset.values()]
        if len(set(lengths)) > 1:
            raise ValueError("Todas as colunas devem ter o mesmo comprimento.")

    def isna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        return self.missing_values.isna(columns)

    def notna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        return self.missing_values.notna(columns)

    def fillna(self, columns: Set[str] = None, value: Any = 0) -> Dict[str, List[Any]]:
        self.missing_values.fillna(columns, value)
        self._update_stats()
        return self.dataset

    def dropna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        self.missing_values.dropna(columns)
        self._update_stats()
        return self.dataset

    def _update_stats(self):
        """Atualiza a instância de Statistics após limpeza de dados."""
        self.statistics = Statistics(self.dataset)
        self.scaler.stats = self.statistics

    def scale(self, columns: Set[str] = None, method: str = 'minMax') -> Dict[str, List[Any]]:
        if method == 'minMax':
            return self.scaler.minMax_scaler(columns)
        elif method == 'standard':
            return self.scaler.standard_scaler(columns)
        else:
            raise ValueError(f"Método de escalonamento '{method}' não suportado.")

    def encode(self, columns: Set[str], method: str = 'label') -> Dict[str, List[Any]]:
        if method == 'label':
            return self.encoder.label_encode(columns)
        elif method == 'oneHot':
            return self.encoder.oneHot_encode(columns)
        else:
            raise ValueError(f"Método de codificação '{method}' não suportado.")