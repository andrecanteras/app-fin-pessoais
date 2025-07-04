-- Script para adicionar campo descricao_pagamento na tabela gastos_recorrentes

-- Adicionar campo descricao_pagamento no esquema de produção
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais.gastos_recorrentes') AND name = 'descricao_pagamento')
BEGIN
    ALTER TABLE financas_pessoais.gastos_recorrentes ADD descricao_pagamento NVARCHAR(255) NULL
    PRINT 'Campo descricao_pagamento adicionado ao esquema de produção.'
END

-- Adicionar campo descricao_pagamento no esquema de desenvolvimento
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('financas_pessoais_dev.gastos_recorrentes') AND name = 'descricao_pagamento')
BEGIN
    ALTER TABLE financas_pessoais_dev.gastos_recorrentes ADD descricao_pagamento NVARCHAR(255) NULL
    PRINT 'Campo descricao_pagamento adicionado ao esquema de desenvolvimento.'
END

PRINT 'Campo descricao_pagamento adicionado com sucesso nas tabelas gastos_recorrentes!'