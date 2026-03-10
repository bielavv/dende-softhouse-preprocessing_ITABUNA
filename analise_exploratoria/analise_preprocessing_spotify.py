"""
ANÁLISE DE PRÉ-PROCESSAMENTO NO DATASET SPOTIFY - VERSÃO OBJETIVA
"""
import sys
import os
import copy

pasta_principal = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pasta_principal)

from dende_preprocessing import Preprocessing
from dende_statistics import Statistics

def carregar_spotify():
    """Carrega o dataset Spotify"""
    import csv
    
    nome_arquivo = 'spotify_data_clean.csv'
    dados = {}
    
    with open(nome_arquivo, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        colunas = reader.fieldnames
        
        for coluna in colunas:
            dados[coluna] = []
        
        for linha in reader:
            for coluna in colunas:
                valor = linha[coluna]
                
                try:
                    if coluna in ['track_popularity', 'artist_popularity', 
                                  'artist_followers', 'album_total_tracks', 
                                  'track_duration_min']:
                        if valor == '' or valor == 'N/A':
                            dados[coluna].append(None)
                        elif '.' in valor:
                            dados[coluna].append(float(valor))
                        else:
                            dados[coluna].append(int(valor))
                    else:
                        dados[coluna].append(valor)
                except:
                    dados[coluna].append(valor)
    
    print(f"Dataset carregado: {len(dados['track_id'])} músicas")
    return dados

def analisar_preprocessing():
    """Aplica técnicas de pré-processamento no Spotify"""
    
    print("=" * 60)
    print("ANÁLISE DE PRÉ-PROCESSAMENTO - SPOTIFY")
    print("=" * 60)
    
    # 1. CARREGAR DADOS
    dados_originais = carregar_spotify()
    dados_trabalho = copy.deepcopy(dados_originais)
    prep = Preprocessing(dados_trabalho)
    
    total_linhas = len(dados_trabalho['track_id'])
    print(f"\n1. DATASET ORIGINAL: {total_linhas} linhas")
    
    # 2. ANÁLISE DE VALORES NULOS
    print("\n2. VALORES NULOS")
    
    colunas_numericas = ['track_popularity', 'artist_popularity', 
                         'artist_followers', 'album_total_tracks', 
                         'track_duration_min']
    
    colunas_categoricas = ['explicit', 'album_type']
    
    print("   Colunas numéricas:")
    for coluna in colunas_numericas:
        if coluna in dados_trabalho:
            qtd = sum(1 for v in dados_trabalho[coluna] if v is None)
            if qtd > 0:
                print(f"     - {coluna}: {qtd} nulos ({qtd/total_linhas*100:.1f}%)")
    
    print("   Colunas categóricas:")
    for coluna in colunas_categoricas:
        if coluna in dados_trabalho:
            qtd = sum(1 for v in dados_trabalho[coluna] if v is None)
            if qtd > 0:
                print(f"     - {coluna}: {qtd} nulos ({qtd/total_linhas*100:.1f}%)")
    
    # 3. TRATAMENTO DE NULOS
    print("\n3. TRATAMENTO DE NULOS")
    
    # fillna em colunas numéricas
    prep.fillna(columns=set(colunas_numericas), value=0)
    
    # Verificar resultado
    nulos_restantes = 0
    for coluna in colunas_numericas:
        qtd = sum(1 for v in dados_trabalho[coluna] if v is None)
        nulos_restantes += qtd
    
    if nulos_restantes == 0:
        print("   - fillna(value=0): todos os nulos numéricos preenchidos")
    else:
        print(f"   - Ainda restam {nulos_restantes} nulos")
    
    # 4. ESCALONAMENTO MIN-MAX
    print("\n4. ESCALONAMENTO MIN-MAX")
    
    stats_antes = Statistics(dados_trabalho)
    
    print("   ANTES:")
    for coluna in colunas_numericas[:2]:
        if coluna in dados_trabalho:
            valores = [v for v in dados_trabalho[coluna] if v is not None]
            if valores:
                print(f"     {coluna}: min={min(valores):.2f}, max={max(valores):.2f}")
    
    prep.scale(columns=set(colunas_numericas), method='minMax')
    
    print("   DEPOIS (0 a 1):")
    for coluna in colunas_numericas[:2]:
        if coluna in dados_trabalho:
            valores = [v for v in dados_trabalho[coluna] if v is not None]
            if valores:
                print(f"     {coluna}: min={min(valores):.2f}, max={max(valores):.2f}")
    
    # 5. CODIFICAÇÃO LABEL ENCODING
    print("\n5. LABEL ENCODING")
    
    # Criar novo dataset para encoding
    dados_encode = copy.deepcopy(dados_originais)
    prep_encode = Preprocessing(dados_encode)
    
    print("   ANTES:")
    for coluna in colunas_categoricas:
        if coluna in dados_encode:
            valores_unicos = set(dados_encode[coluna])
            print(f"     {coluna}: {len(valores_unicos)} categorias")
    
    prep_encode.encode(columns=set(colunas_categoricas), method='label')
    
    print("   DEPOIS (valores numéricos):")
    for coluna in colunas_categoricas:
        if coluna in dados_encode:
            print(f"     {coluna}: {dados_encode[coluna][:5]}")
    
    # 6. DEMONSTRAÇÃO ONE-HOT ENCODING
    print("\n6. ONE-HOT ENCODING")
    
    dados_onehot = {
        'album_type': ['album', 'single', 'album', 'compilation', 'single'],
        'explicit': ['TRUE', 'FALSE', 'TRUE', 'FALSE', 'TRUE']
    }
    
    prep_onehot = Preprocessing(dados_onehot)
    print("   Original:")
    print(f"     album_type: {dados_onehot['album_type']}")
    print(f"     explicit: {dados_onehot['explicit']}")
    
    prep_onehot.encode(columns={'album_type', 'explicit'}, method='oneHot')
    
    print("   Após One-Hot (novas colunas):")
    colunas_onehot = [c for c in prep_onehot.dataset.keys() if '_' in c]
    for coluna in sorted(colunas_onehot)[:3]:
        print(f"     {coluna}: {prep_onehot.dataset[coluna]}")
    
    # 7. RESUMO
    print("\n" + "=" * 60)
    print("RESUMO DAS OPERAÇÕES")
    print("=" * 60)
    print("✓ Identificação de valores nulos")
    print("✓ Preenchimento de nulos (fillna)")
    print("✓ Escalonamento Min-Max")
    print("✓ Label Encoding")
    print("✓ One-Hot Encoding")
    print("\nDataset pronto para modelagem!")

if __name__ == "__main__":
    analisar_preprocessing()

    