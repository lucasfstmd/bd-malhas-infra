from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import polars as pl
from sqlalchemy import create_engine
import os
from datetime import datetime
import clickhouse_connect
import re

base_dir_executor = '/opt/airflow/dags/bridgefiles/Executor'

# Configurações padrão do DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def sanitize_column_name(name):
    # Remove caracteres especiais e espaços, mantendo apenas letras, números e underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', str(name))
    # Garante que o nome da coluna começa com uma letra
    if sanitized[0].isdigit():
        sanitized = 'col_' + sanitized
    return sanitized


# Função para carregar dados do CSV para o banco de dados
def load_csv_to_db():
    # Diretório base onde os arquivos são salvos
    base_dir = f"{base_dir_executor}/persistencia/dados-ceos/notas-fiscais"

    # Obtém a data atual no formato necessário
    data_atual = datetime.now().strftime("%d-%m-%Y")
    nome_arquivo = f"nfe_saida_{data_atual}.txt"

    # Caminho completo do arquivo
    csv_path = os.path.join(base_dir, nome_arquivo)

    # Verifica se o arquivo existe
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    # Define os nomes das colunas conforme o formato do arquivo
    colunas = [
        'nrChaveAcesso', 'nroNFe', 'serie', 'dataEmissao', 'horaEmissao', 'situacao', 'tipoOperacao',
        'valorTotaldaNota', 'notaReferenciada', 'noRazaoSocialEmit', 'cpfCnpjEmitente', 'ieEmitente',
        'enderecoEmitente', 'bairroDistritoEmitente', 'cepEmitente', 'municipioEmitente', 'codigoMunEmitente',
        'foneFaxEmitente', 'ufEmitente', 'paisEmitente', 'noRazaoSocialDestinatario', 'cpfCnpjDestinatario',
        'ieDestinatario', 'enderecoDestinatario', 'bairroDistritoDestinatario', 'cepDestinatario',
        'municipioDestinatario', 'codigoMunicDest', 'foneFaxDestinatario', 'ufDestinatario', 'paisDestinatario',
        'nroFatura', 'vencimentoFatura', 'valorFatura', 'placaVeiculoReboque', 'ufPlaca', 'nomeTransportadora',
        'ieTransportadora', 'cnpjTransportadora', 'cpfTransportadora', 'modalidadeFrete', 'baseCalculoICMS',
        'valorICMS', 'baseCalculoICMSSubstituicao', 'valorICMSSubstituicao', 'valorTotalDosProdutos',
        'valorFrete', 'valorSeguro', 'valorDesconto', 'valorOutrasDespesasAcessorias', 'valorIPI',
        'valorTotalICMSUFDestinatario', 'valorTotalICMSUFRemetente', 'valorBCICMSUFDestinatario',
        'aliquotaInternaUFDestinatario', 'aliquotaInterestadualUFEnv', 'percProvPartilhaUF',
        'percICMSFCPUFDestinatario', 'valorICMSFCPUFDestinatario', 'valorICMSPartilhaUFDest',
        'valorICMSPartilhaUFRemet', 'nrItem', 'codProd', 'descricaoProdutoOuServicos', 'ncmProd',
        'cstProd', 'cfopProd', 'unidProdTrib', 'unidProdCom', 'quantProdTrib', 'quantProdCom',
        'valorUnitProdTrib', 'valorUnitProdCom', 'valorTotalProd', 'valorDescontoItem', 'valorOutrasItem',
        'valorFreteItem', 'valorSeguroItem', 'bcICMSProd', 'valorICMSProd', 'aliqICMSProd', 'bcICMSSTProd',
        'valorICMSSTProd', 'aliqICMSSTProd', 'valorIPIProd', 'aliqIPIProd', 'valorPMCProd', 'codEAN',
        'infoAdicionalItem', 'tipoOperacaoVeicNovo', 'tipoPinturaVeicNovo', 'cnpjConcessionariaEntrega',
        'ufEntrega', 'chassiVeiculo', 'informacoesAdicionaisFisco', 'informacoesComplementares',
        'codigoProdutoANP', 'percGlpDerivadoDoPetroleo', 'percGasNaturalNacional', 'percGasNaturalImportado',
        'valorDePartida', 'codif', 'qtCombustivelTempAmbiente', 'ufDeConsumo', 'vlDoServicoRetido',
        'bcRetencaoTransporte', 'aliquotaRetencaoTransporte', 'valorIcmsRetidoTransporte', 'infCTeVinculado',
        'infMDFeVinculado', 'infPagamento', 'vlPagamento', 'cdReceitaPagamento', 'bcICMSCTe', 'aliquotaCTe',
        'vlICMSCTe', 'vlServicoCTe', 'qtdeVolumes', 'pesoLiquido', 'pesoBruto', 'naturezaOperacao',
        'emailDestinatario', 'ipEmitente', 'aliqCreditoSN', 'vlCreditoSN', 'protocolo', 'dataSaiEnt',
        'horaSaiEnt', 'inscEstSubsTrib', 'finalidadeNFe', 'vlServ', 'vbCalcISSQN', 'vISS',
        'enderecoTransportadora', 'municipioTransportadora', 'ufTransportadora', 'especieTransportadora',
        'marcaTransportadora', 'nrLacre', 'regNacTranspCargaANTT', 'inscMunicipal', 'cUF', 'cNF',
        'cMunFG', 'cnae', 'nrIpTransmissor', 'nrPortaCon'
    ]

    # Lê o arquivo CSV usando Polars com configurações específicas
    df = pl.read_csv(
        csv_path,
        separator='|',
        has_header=True,
        columns=colunas,
        infer_schema_length=0,  # Desativa a inferência de schema
        dtypes={col: pl.String for col in colunas},  # Força todos os campos como string
        null_values=['', 'NULL', 'null', ' ']  # Define valores que devem ser tratados como nulos
    )

    # Substitui valores nulos por uma string vazia
    df = df.fill_null(strategy="zero")

    # Configuração da conexão com o ClickHouse
    client = clickhouse_connect.get_client(
        host='10.120.8.186',
        port=8123,
        user='gaecoClk',
        password='gaeco_clickhouse'
    )

    # Converte o DataFrame Polars para uma lista de tuplas
    data = df.to_numpy().tolist()

    # Cria a tabela se não existir
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS pandora.carga_nfe_teste (
        nrChaveAcesso String,
        {', '.join([f'{sanitize_column_name(col)} Nullable(String)' for col in colunas if col != 'nrChaveAcesso'])}
    ) ENGINE = MergeTree()
    ORDER BY nrChaveAcesso
    SETTINGS allow_nullable_key=1
    """

    try:
        # Tenta dropar a tabela se ela existir
        client.command('DROP TABLE IF EXISTS pandora.carga_nfe_teste')
        # Cria a tabela novamente
        client.command(create_table_query)

        # Insere os dados usando insert_rows
        client.insert('pandora.carga_nfe_teste', data, column_names=[sanitize_column_name(col) for col in colunas])

        print(f"Dados carregados com sucesso. Total de registros: {len(data)}")
    except Exception as e:
        print(f"Erro ao executar operação no ClickHouse: {str(e)}")
        raise


# Criação do DAG
with DAG(
        dag_id='carga_nfe_atf',
        default_args=default_args,
        description='Carga de dados de NF-e no ClickHouse',
        schedule_interval=None,
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['clickhouse', 'nfe', 'etl', 'minio']
) as dag:
    # Tarefa para executar o JAR
    executar_jar = BashOperator(
        task_id='executar_jar',
        bash_command=f"cd {base_dir_executor} && java -jar executor.jar",
        dag=dag,
    )

    # Tarefa para carregar dados no banco
    carregar_dados = PythonOperator(
        task_id='carregar_dados',
        python_callable=load_csv_to_db,
        dag=dag,
    )

    # Definição do fluxo de tarefas
    executar_jar >> carregar_dados
