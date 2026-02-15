import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
SILVER_DATA_DIR = os.path.join(BASE_DIR, "data", "silver")

#metadata silver
FULL_METADATA_MAP = {
    'cnpj': 'NRCNPJ',
    'razao_social': 'NMRAZSOC',
    'nome_fantasia': 'NMFANT',
    'capital_social': 'VLCPTSOC',
    'identificador_matriz_filial': 'IDMTZFIL',
    'descricao_identificador_matriz_filial': 'DSIDMTZFIL',
    'uf': 'SGUF',
    'cep': 'NRCEP',
    'pais': 'NMPAIS',
    'codigo_pais': 'CDPAIS',
    'municipio': 'NMMUN',
    'codigo_municipio': 'CDMUN',
    'codigo_municipio_ibge': 'CDMUNIBGE',
    'bairro': 'NMBRR',
    'logradouro': 'NMLGR',
    'numero': 'NREND',
    'complemento': 'DSCPL',
    'descricao_tipo_de_logradouro': 'DSTIPLGR',
    'nome_cidade_no_exterior': 'NMCDEXT',
    'email': 'DSEML',
    'ddd_fax': 'NRFAX',
    'ddd_telefone_1': 'NRTEL1',
    'ddd_telefone_2': 'NRTEL2',
    'cnae_fiscal': 'CDCNAEFISC',
    'cnae_fiscal_descricao': 'DSCNAEFISC',
    'natureza_juridica': 'DSNATJUR',
    'codigo_natureza_juridica': 'CDNATJUR',
    'porte': 'DSPORTE',
    'codigo_porte': 'CDPORTE',
    'qualificacao_do_responsavel': 'CDQUALRESP',
    'ente_federativo_responsavel': 'NMENTEFED',
    'situacao_cadastral': 'CDSITCAD',
    'descricao_situacao_cadastral': 'DSSITCAD',
    'data_situacao_cadastral': 'DTSITCAD',
    'motivo_situacao_cadastral': 'CDMOTSITCAD',
    'descricao_motivo_situacao_cadastral': 'DSMOTSITCAD',
    'situacao_especial': 'DSSITESPEC',
    'data_situacao_especial': 'DTSITESPEC',
    'data_inicio_atividade': 'DTINIATV',
    'opcao_pelo_simples': 'FLSIMPLES',
    'data_opcao_pelo_simples': 'DTOPTSIMPLES',
    'data_exclusao_do_simples': 'DTEXCSIMPLES',
    'opcao_pelo_mei': 'FLMEI',
    'data_opcao_pelo_mei': 'DTOPTMEI',
    'data_exclusao_do_mei': 'DTEXCMEI',
    'qsa_pais': 'QSANMPAIS',
    'qsa_nome_socio': 'QSANMSOC',
    'qsa_codigo_pais': 'QSACDPAIS',
    'qsa_faixa_etaria': 'QSADSFAIXETAR',
    'qsa_cnpj_cpf': 'QSANRDOC',
    'qsa_qualificacao_socio': 'QSADSQUAL',
    'qsa_codigo_faixa_etaria': 'QSACDFAIXETAR',
    'qsa_data_entrada_sociedade': 'QSADTENT',
    'qsa_identificador_de_socio': 'QSAIDSOC',
    'qsa_cpf_representante_legal': 'QSANRCPFREP',
    'qsa_nome_representante_legal': 'QSANMREP',
    'qsa_codigo_qualificacao_socio': 'QSACDQUAL',
    'qsa_qualificacao_representante_legal': 'QSADSQUALREP',
    'qsa_codigo_qualificacao_representante_legal': 'QSACDQUALREP',
    'cnaes_secundarios_codigo': 'CDCNAESEC',
    'cnaes_secundarios_descricao': 'DSCNAESEC',
    'regime_tributario_ano': 'TRIANO',
    'regime_tributario_cnpj_da_scp': 'TRICNJSCP',
    'regime_tributario_forma_de_tributacao': 'TRIFORMA',
    'regime_tributario_quantidade_de_escrituracoes': 'TRIQTDESCRIT'
}

RENAME_QSA = {
    'pais': 'qsa_pais', 'nome_socio': 'qsa_nome_socio', 'codigo_pais': 'qsa_codigo_pais',
    'faixa_etaria': 'qsa_faixa_etaria', 'cnpj_cpf_do_socio': 'qsa_cnpj_cpf',
    'qualificacao_socio': 'qsa_qualificacao_socio', 'codigo_faixa_etaria': 'qsa_codigo_faixa_etaria',
    'data_entrada_sociedade': 'qsa_data_entrada_sociedade', 'identificador_de_socio': 'qsa_identificador_de_socio',
    'cpf_representante_legal': 'qsa_cpf_representante_legal', 'nome_representante_legal': 'qsa_nome_representante_legal',
    'tipo_representante_legal': 'qsa_tipo_representante_legal', 'cnpj_cpf_representante_legal': 'qsa_cnpj_cpf_representante_legal',
    'codigo_qualificacao_socio': 'qsa_codigo_qualificacao_socio', 'qualificacao_representante_legal': 'qsa_qualificacao_representante_legal',
    'codigo_qualificacao_representante_legal': 'qsa_codigo_qualificacao_representante_legal'
}

RENAME_CNAE = {'codigo': 'cnaes_secundarios_codigo', 'descricao': 'cnaes_secundarios_descricao'}

RENAME_REGIME = {
    'ano': 'regime_tributario_ano', 'cnpj_da_scp': 'regime_tributario_cnpj_da_scp',
    'forma_de_tributacao': 'regime_tributario_forma_de_tributacao', 
    'quantidade_de_escrituracoes': 'regime_tributario_quantidade_de_escrituracoes'
}
