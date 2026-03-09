from dende_statistics import Statistics
from typing import Dict, List, Set, Any

class MissingValueProcessor:
    def __init__(self, dataset: Dict[str, List[Any]]):
        self.dataset = dataset

    def _get_target_columns(self, columns: Set[str]) -> List[str]:
        return list(columns) if columns else list(self.dataset.keys())

    def isna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        target_cols = self._get_target_columns(columns)
        num_rows = len(next(iter(self.dataset.values())))
        subset = {col: [] for col in self.dataset.keys()}
        for i in range(num_rows):
            if any(self.dataset[col][i] is None for col in target_cols):
                for col in self.dataset.keys():
                    subset[col].append(self.dataset[col][i])
        return subset

    def notna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        target_cols = self._get_target_columns(columns)
        num_rows = len(next(iter(self.dataset.values())))
        subset = {col: [] for col in self.dataset.keys()}
        for i in range(num_rows):
            if all(self.dataset[col][i] is not None for col in target_cols):
                for col in self.dataset.keys():
                    subset[col].append(self.dataset[col][i])
        return subset

    def fillna(self, columns: Set[str] = None, value: Any = 0) -> Dict[str, List[Any]]:
        target_cols = self._get_target_columns(columns)
        for col in target_cols:
            self.dataset[col] = [value if x is None else x for x in self.dataset[col]]
        return self.dataset

    def dropna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        target_cols = self._get_target_columns(columns)
        num_rows = len(next(iter(self.dataset.values())))
        indices_validos = [i for i in range(num_rows) 
                          if all(self.dataset[col][i] is not None for col in target_cols)]
        for col in self.dataset.keys():
            self.dataset[col] = [self.dataset[col][i] for i in indices_validos]
        return self.dataset

class Scaler:
    def __init__(self, dataset: Dict[str, List[Any]], stats_obj: Statistics = None):
        self.dataset = dataset
        self.stats = stats_obj

    def _get_target_columns(self, columns: Set[str]) -> List[str]:
        return list(columns) if columns else list(self.dataset.keys())

    def minMax_scaler(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        target_cols = self._get_target_columns(columns)
        for col in target_cols:
            dados = self.dataset[col]
            v_min, v_max = min(dados), max(dados)
            diff = v_max - v_min
            self.dataset[col] = [(x - v_min) / diff if diff != 0 else 0.0 for x in dados]
        return self.dataset

    def standard_scaler(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        target_cols = self._get_target_columns(columns)
        
        for col in target_cols:
            # Em vez de validar o dataset todo, criamos uma Statistics 
            # apenas para a coluna que estamos mexendo agora.
            # Isso evita que o erro na coluna 'city' trave o cálculo da 'age'.
            col_stats = Statistics({col: self.dataset[col]})
            
            mu = col_stats.mean(col)
            sigma = col_stats.stdev(col)
            
            self.dataset[col] = [(x - mu) / sigma if sigma != 0 else 0.0 for x in self.dataset[col]]
            
        return self.dataset

class Encoder:
    def __init__(self, dataset: Dict[str, List[Any]]):
        self.dataset = dataset

    def label_encode(self, columns: Set[str]) -> Dict[str, List[Any]]:
        for col in columns:
            # Convertemos para str antes de ordenar para evitar erro de tipos mistos
            categorias = sorted(list(set(str(x) for x in self.dataset[col])))
            mapping = {val: i for i, val in enumerate(categorias)}
            # Aplicamos o mapeamento convertendo o valor atual para string também
            self.dataset[col] = [mapping[str(v)] for v in self.dataset[col]]
        return self.dataset

    def oneHot_encode(self, columns: Set[str]) -> Dict[str, List[Any]]:
        for col in list(columns):
            categorias = sorted(list(set(self.dataset[col])))
            original = self.dataset.pop(col)
            for cat in categorias:
                self.dataset[f"{col}_{cat}"] = [1 if x == cat else 0 for x in original]
        return self.dataset

class Preprocessing:
    def __init__(self, dataset: Dict[str, List[Any]]):
        self.dataset = dataset
        self._validate_dataset_shape()
        
        self.missing_values = MissingValueProcessor(self.dataset)
        self.scaler = Scaler(self.dataset)
        self.encoder = Encoder(self.dataset)
        
        try:
            self.statistics = Statistics(self.dataset)
            self.scaler.stats = self.statistics
        except:
            self.statistics = None

    def _validate_dataset_shape(self):
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
        self._update_stats_safely()
        return self.dataset

    def dropna(self, columns: Set[str] = None) -> Dict[str, List[Any]]:
        self.missing_values.dropna(columns)
        self._update_stats_safely()
        return self.dataset

    def _update_stats_safely(self):
        """Tenta atualizar estatísticas sem quebrar por causa de tipos mistos."""
        try:
            self.statistics = Statistics(self.dataset)
            self.scaler.stats = self.statistics
        except (TypeError, ValueError, KeyError):
            pass

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