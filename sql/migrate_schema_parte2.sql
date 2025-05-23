-- Script para exportar dados do banco atual (bdMaterialEscolar)
-- Execute este script no banco bdMaterialEscolar

-- Exportar dados da tabela categorias
SELECT 
    id AS id_original,
    nome,
    tipo,
    descricao,
    data_criacao,
    ativo,
    categoria_pai_id,
    nivel
FROM 
    financas_pessoais.categorias
ORDER BY 
    id;

-- Exportar dados da tabela conta_dimensao
SELECT 
    id AS id_original,
    nome,
    tipo,
    instituicao,
    agencia,
    conta_contabil,
    numero_banco,
    titular,
    nome_gerente,
    contato_gerente,
    data_criacao,
    ativo
FROM 
    financas_pessoais.conta_dimensao
ORDER BY 
    id;

-- Exportar dados da tabela conta_saldos
SELECT 
    id AS id_original,
    conta_dimensao_id,
    saldo_inicial,
    saldo_atual,
    data_criacao
FROM 
    financas_pessoais.conta_saldos
ORDER BY 
    id;

-- Exportar dados da tabela meios_pagamento
SELECT 
    id AS id_original,
    nome,
    descricao,
    conta_id,
    tipo,
    data_criacao,
    ativo
FROM 
    financas_pessoais.meios_pagamento
ORDER BY 
    id;

-- Exportar dados da tabela metas
SELECT 
    id AS id_original,
    nome,
    valor_alvo,
    valor_atual,
    data_inicio,
    data_fim,
    categoria_id,
    observacao,
    concluida,
    data_criacao
FROM 
    financas_pessoais.metas
ORDER BY 
    id;

-- Exportar dados da tabela transacoes
SELECT 
    id AS id_original,
    descricao,
    valor,
    data_transacao,
    tipo,
    categoria_id,
    conta_id,
    observacao,
    data_criacao,
    meio_pagamento_id,
    descricao_pagamento,
    local_transacao
FROM 
    financas_pessoais.transacoes
ORDER BY 
    id;