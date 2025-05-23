-- Script para importar dados no novo banco de dados
-- Execute este script no novo banco de dados
-- Substitua os valores pelos dados exportados do banco original

-- Desabilitar verificação de chaves estrangeiras temporariamente
EXEC sp_MSforeachtable "ALTER TABLE ? NOCHECK CONSTRAINT all"

-- Importar dados para tabela categorias
-- Substitua os VALUES pelos dados exportados do banco original
SET IDENTITY_INSERT financas_pessoais.categorias ON;
INSERT INTO financas_pessoais.categorias (id, nome, tipo, descricao, data_criacao, ativo, categoria_pai_id, nivel)
VALUES 
    (1, 'Salário', 'R', 'Rendimentos de trabalho', '2023-01-01', 1, NULL, 1),
    -- Adicione mais linhas conforme necessário
    (2, 'Alimentação', 'D', 'Gastos com alimentação', '2023-01-01', 1, NULL, 1);
SET IDENTITY_INSERT financas_pessoais.categorias OFF;

-- Importar dados para tabela conta_dimensao
-- Substitua os VALUES pelos dados exportados do banco original
SET IDENTITY_INSERT financas_pessoais.conta_dimensao ON;
INSERT INTO financas_pessoais.conta_dimensao 
(id, nome, tipo, instituicao, agencia, conta_contabil, numero_banco, titular, nome_gerente, contato_gerente, data_criacao, ativo)
VALUES 
    (1, 'Conta Corrente', 'Corrente', 'Banco X', '1234', '12345-6', '001', 'Nome do Titular', 'Nome do Gerente', 'contato@banco.com', '2023-01-01', 1),
    -- Adicione mais linhas conforme necessário
    (2, 'Poupança', 'Poupança', 'Banco Y', '5678', '56789-0', '033', 'Nome do Titular', NULL, NULL, '2023-01-01', 1);
SET IDENTITY_INSERT financas_pessoais.conta_dimensao OFF;

-- Importar dados para tabela conta_saldos
-- Substitua os VALUES pelos dados exportados do banco original
SET IDENTITY_INSERT financas_pessoais.conta_saldos ON;
INSERT INTO financas_pessoais.conta_saldos 
(id, conta_dimensao_id, saldo_inicial, saldo_atual, data_criacao)
VALUES 
    (1, 1, 1000.00, 1500.00, '2023-01-01'),
    -- Adicione mais linhas conforme necessário
    (2, 2, 500.00, 750.00, '2023-01-01');
SET IDENTITY_INSERT financas_pessoais.conta_saldos OFF;

-- Importar dados para tabela meios_pagamento
-- Substitua os VALUES pelos dados exportados do banco original
SET IDENTITY_INSERT financas_pessoais.meios_pagamento ON;
INSERT INTO financas_pessoais.meios_pagamento 
(id, nome, descricao, conta_id, tipo, data_criacao, ativo)
VALUES 
    (1, 'Cartão de Crédito', 'Cartão principal', 1, 'Cartão de Crédito', '2023-01-01', 1),
    -- Adicione mais linhas conforme necessário
    (2, 'PIX', 'Transferência via PIX', NULL, 'PIX', '2023-01-01', 1);
SET IDENTITY_INSERT financas_pessoais.meios_pagamento OFF;

-- Importar dados para tabela metas
-- Substitua os VALUES pelos dados exportados do banco original
SET IDENTITY_INSERT financas_pessoais.metas ON;
INSERT INTO financas_pessoais.metas 
(id, nome, valor_alvo, valor_atual, data_inicio, data_fim, categoria_id, observacao, concluida, data_criacao)
VALUES 
    (1, 'Férias', 5000.00, 2500.00, '2023-01-01', '2023-12-31', 1, 'Meta para viagem de férias', 0, '2023-01-01'),
    -- Adicione mais linhas conforme necessário
    (2, 'Emergência', 10000.00, 3000.00, '2023-01-01', '2023-12-31', 1, 'Fundo de emergência', 0, '2023-01-01');
SET IDENTITY_INSERT financas_pessoais.metas OFF;

-- Importar dados para tabela transacoes
-- Substitua os VALUES pelos dados exportados do banco original
SET IDENTITY_INSERT financas_pessoais.transacoes ON;
INSERT INTO financas_pessoais.transacoes 
(id, descricao, valor, data_transacao, tipo, categoria_id, conta_id, observacao, data_criacao, meio_pagamento_id, descricao_pagamento, local_transacao)
VALUES 
    (1, 'Salário mensal', 5000.00, '2023-01-05', 'R', 1, 1, 'Salário de janeiro', '2023-01-05', NULL, NULL, NULL),
    -- Adicione mais linhas conforme necessário
    (2, 'Supermercado', 350.00, '2023-01-10', 'D', 2, 1, 'Compras da semana', '2023-01-10', 1, 'Cartão de crédito', 'Supermercado X');
SET IDENTITY_INSERT financas_pessoais.transacoes OFF;

-- Habilitar verificação de chaves estrangeiras novamente
EXEC sp_MSforeachtable "ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all"

PRINT 'Dados importados com sucesso!';