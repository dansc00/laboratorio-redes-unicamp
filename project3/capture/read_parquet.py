# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt

# Ler o arquivo Parquet
file = 'capture.parquet'
df = pd.read_parquet(file, engine='pyarrow')

# Mostrar informações básicas
print(f"Quantidade total de registros: {len(df)}")
print("\nPrimeiros 10 registros:")
print(df.head(10))

print("\nTipos de dados por coluna:")
print(df.dtypes)

# Converter para datetime se ainda não estiver
df['timestamp'] = pd.to_datetime(df['timestamp'])
'''
# Criar gráfico de distribuição do tamanho dos pacotes por tipo de protocolo
plt.figure(figsize=(10, 6), dpi=300)

# Verificar se as colunas 'type' e 'size' existem e são válidas
if 'type' in df.columns and 'size' in df.columns:
    for t in df['type'].dropna().unique():
        subset = df[df['type'] == t]
        plt.hist(subset['size'], bins=50, alpha=0.6, label=str(t))

    plt.title("Distribuição do tamanho dos pacotes por tipo de protocolo")
    plt.xlabel("Tamanho do pacote (bytes)")
    plt.ylabel("Frequência")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Salvar o gráfico em alta qualidade
    output_file = "distribuicao_tamanho_pacotes.png"
    plt.savefig(output_file, dpi=300)
    print(f"Gráfico salvo como: {output_file}")
else:
    print("❌ As colunas 'type' ou 'size' não foram encontradas para gerar o gráfico.")
'''

def graficar_tcp(df, output_file='tcp_tamanho_distribuicao.png'):
    """
    Filtra apenas pacotes TCP e gera a distribuição do tamanho.

    Args:
        df (pd.DataFrame): DataFrame contendo as colunas 'type' e 'size'.
        output_file (str): Caminho do arquivo PNG de saída.
    """
    if 'type' not in df.columns or 'size' not in df.columns:
        print("❌ O DataFrame não contém as colunas necessárias.")
        return

    df_tcp = df[df['type'] == 'TCP']

    if df_tcp.empty:
        print("Nenhum pacote TCP encontrado no DataFrame.")
        return

    # Gerar gráfico
    plt.figure(figsize=(10, 6), dpi=300)
    plt.hist(df_tcp['size'], bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    plt.title("Distribuição do tamanho dos pacotes TCP")
    plt.xlabel("Tamanho do pacote (bytes)")
    plt.ylabel("Frequência")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(output_file, dpi=300)
    print(f"Gráfico TCP salvo como: {output_file}")


# Garantir que a coluna timestamp está no formato datetime, se necessário
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Chamar a função para gerar gráfico apenas para pacotes TCP
#graficar_tcp(df)
