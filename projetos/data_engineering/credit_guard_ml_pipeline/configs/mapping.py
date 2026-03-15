import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
SILVER_DATA_DIR = os.path.join(BASE_DIR, "data", "silver")

#metadata silver
FULL_METADATA_MAP = {
    # Identificação Básica
    'cnpj': {'alias': 'NRCNPJ', 'type': 'str'},
    'razao_social': {'alias': 'NMRAZSOC', 'type': 'str'},
    'nome_fantasia': {'alias': 'NMFANT', 'type': 'str'},
    'capital_social': {'alias': 'VLCPTSOC', 'type': 'float64'},
    'identificador_matriz_filial': {'alias': 'IDMTZFIL', 'type': 'int64'},
    'descricao_identificador_matriz_filial': {'alias': 'DSIDMTZFIL', 'type': 'str'},
    
    # Localização
    'uf': {'alias': 'SGUF', 'type': 'str'},
    'cep': {'alias': 'NRCEP', 'type': 'str'},
    'pais': {'alias': 'NMPAIS', 'type': 'str'},
    'codigo_pais': {'alias': 'CDPAIS', 'type': 'str'},
    'municipio': {'alias': 'NMMUN', 'type': 'str'},
    'codigo_municipio': {'alias': 'CDMUN', 'type': 'str'},
    'codigo_municipio_ibge': {'alias': 'CDMUNIBGE', 'type': 'int64'},
    'bairro': {'alias': 'NMBRR', 'type': 'str'},
    'logradouro': {'alias': 'NMLGR', 'type': 'str'},
    'numero': {'alias': 'NREND', 'type': 'str'},
    'complemento': {'alias': 'DSCPL', 'type': 'str'},
    'descricao_tipo_de_logradouro': {'alias': 'DSTIPLGR', 'type': 'str'},
    'nome_cidade_no_exterior': {'alias': 'NMCDEXT', 'type': 'str'},
    
    # Contato
    'email': {'alias': 'DSEML', 'type': 'str'},
    'ddd_fax': {'alias': 'NRFAX', 'type': 'str'},
    'ddd_telefone_1': {'alias': 'NRTEL1', 'type': 'str'},
    'ddd_telefone_2': {'alias': 'NRTEL2', 'type': 'str'},
    
    # Classificação e Natureza
    'cnae_fiscal': {'alias': 'CDCNAEFISC', 'type': 'int64'},
    'cnae_fiscal_descricao': {'alias': 'DSCNAEFISC', 'type': 'str'},
    'natureza_juridica': {'alias': 'DSNATJUR', 'type': 'str'},
    'codigo_natureza_juridica': {'alias': 'CDNATJUR', 'type': 'int64'},
    'porte': {'alias': 'DSPORTE', 'type': 'str'},
    'codigo_porte': {'alias': 'CDPORTE', 'type': 'int64'},
    'qualificacao_do_responsavel': {'alias': 'CDQUALRESP', 'type': 'int64'},
    'ente_federativo_responsavel': {'alias': 'NMENTEFED', 'type': 'str'},
    
    # Situação Cadastral
    'situacao_cadastral': {'alias': 'CDSITCAD', 'type': 'int64'},
    'descricao_situacao_cadastral': {'alias': 'DSSITCAD', 'type': 'str'},
    'data_situacao_cadastral': {'alias': 'DTSITCAD', 'type': 'str'},
    'motivo_situacao_cadastral': {'alias': 'CDMOTSITCAD', 'type': 'int64'},
    'descricao_motivo_situacao_cadastral': {'alias': 'DSMOTSITCAD', 'type': 'str'},
    'situacao_especial': {'alias': 'DSSITESPEC', 'type': 'str'},
    'data_situacao_especial': {'alias': 'DTSITESPEC', 'type': 'str'},
    'data_inicio_atividade': {'alias': 'DTINIATV', 'type': 'str'},
    
    # Simples Nacional e MEI (Campos que causaram o erro)
    'opcao_pelo_simples': {'alias': 'FLSIMPLES', 'type': 'str'}, # Booleano na API vira str aqui para segurança
    'data_opcao_pelo_simples': {'alias': 'DTOPTSIMPLES', 'type': 'str'},
    'data_exclusao_do_simples': {'alias': 'DTEXCSIMPLES', 'type': 'str'},
    'opcao_pelo_mei': {'alias': 'FLMEI', 'type': 'str'},
    'data_opcao_pelo_mei': {'alias': 'DTOPTMEI', 'type': 'str'},
    'data_exclusao_do_mei': {'alias': 'DTEXCMEI', 'type': 'str'},
    
    # QSA (Quadro de Sócios e Administradores)
    'qsa_pais': {'alias': 'QSANMPAIS', 'type': 'str'},
    'qsa_nome_socio': {'alias': 'QSANMSOC', 'type': 'str'},
    'qsa_codigo_pais': {'alias': 'QSACDPAIS', 'type': 'str'},
    'qsa_faixa_etaria': {'alias': 'QSADSFAIXETAR', 'type': 'str'},
    'qsa_cnpj_cpf_do_socio': {'alias': 'QSANRDOC', 'type': 'str'},
    'qsa_qualificacao_socio': {'alias': 'QSADSQUAL', 'type': 'str'},
    'qsa_codigo_faixa_etaria': {'alias': 'QSACDFAIXETAR', 'type': 'int64'},
    'qsa_data_entrada_sociedade': {'alias': 'QSADTENT', 'type': 'str'},
    'qsa_identificador_de_socio': {'alias': 'QSAIDSOC', 'type': 'int64'},
    'qsa_cpf_representante_legal': {'alias': 'QSANRCPFREP', 'type': 'str'},
    'qsa_nome_representante_legal': {'alias': 'QSANMREP', 'type': 'str'},
    'qsa_codigo_qualificacao_socio': {'alias': 'QSACDQUAL', 'type': 'int64'},
    'qsa_qualificacao_representante_legal': {'alias': 'QSADSQUALREP', 'type': 'str'},
    'qsa_codigo_qualificacao_representante_legal': {'alias': 'QSACDQUALREP', 'type': 'int64'},
    'qsa_tipo_representante_legal': {'alias': 'QSADSTIPOREP', 'type': 'str'},
    'qsa_cnpj_cpf_representante_legal': {'alias': 'QSANRCPFREP', 'type': 'str'},
    
    # Secundários e Tributário
    'cnaes_secundarios_codigo': {'alias': 'CDCNAESEC', 'type': 'int64'},
    'cnaes_secundarios_descricao': {'alias': 'DSCNAESEC', 'type': 'str'},
    'regime_tributario_ano': {'alias': 'TRIANO', 'type': 'int64'},
    'regime_tributario_cnpj_da_scp': {'alias': 'TRICNJSCP', 'type': 'str'},
    'regime_tributario_forma_de_tributacao': {'alias': 'TRIFORMA', 'type': 'str'},
    'regime_tributario_quantidade_de_escrituracoes': {'alias': 'TRIQTDESCRIT', 'type': 'int64'}
}

RENAME_QSA = {
    'pais': 'qsa_pais', 'nome_socio': 'qsa_nome_socio', 'codigo_pais': 'qsa_codigo_pais',
    'faixa_etaria': 'qsa_faixa_etaria', 'cnpj_cpf_do_socio': 'qsa_cnpj_cpf_do_socio',
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