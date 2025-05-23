-- Scripts úteis para manutenção e consulta do banco de dados
-- Sistema de Finanças Pessoais

-- 1. Verificar estrutura das tabelas
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM 
    INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_SCHEMA = 'financas_pessoais'
ORDER BY 
    TABLE_NAME, ORDINAL_POSITION;

-- 2. Verificar chaves estrangeiras
SELECT 
    fk.name AS FK_Name,
    OBJECT_NAME(fk.parent_object_id) AS TableName,
    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS ColumnName,
    OBJECT_NAME(fk.referenced_object_id) AS ReferencedTableName,
    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS ReferencedColumnName
FROM 
    sys.foreign_keys AS fk
INNER JOIN 
    sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
INNER JOIN
    sys.tables AS t ON fk.parent_object_id = t.object_id
INNER JOIN
    sys.schemas AS s ON t.schema_id = s.schema_id
WHERE 
    s.name = 'financas_pessoais'
ORDER BY
    TableName, FK_Name;

-- 3. Recalcular saldos das contas
UPDATE cs
SET cs.saldo_atual = cs.saldo_inicial + ISNULL(
    (SELECT SUM(CASE WHEN t.tipo = 'R' THEN t.valor ELSE -t.valor END)
     FROM financas_pessoais.transacoes t
     WHERE t.conta_id = cd.id),
    0)
FROM financas_pessoais.conta_saldos cs
JOIN financas_pessoais.conta_dimensao cd ON cs.conta_dimensao_id = cd.id;

-- 4. Listar transações por período
SELECT 
    t.id,
    t.descricao,
    t.valor,
    t.data_transacao,
    t.tipo,
    c.nome AS categoria,
    cd.nome AS conta,
    mp.nome AS meio_pagamento,
    t.local_transacao,
    t.observacao
FROM 
    financas_pessoais.transacoes t
LEFT JOIN 
    financas_pessoais.categorias c ON t.categoria_id = c.id
LEFT JOIN 
    financas_pessoais.conta_dimensao cd ON t.conta_id = cd.id
LEFT JOIN 
    financas_pessoais.meios_pagamento mp ON t.meio_pagamento_id = mp.id
WHERE 
    t.data_transacao BETWEEN '2023-01-01' AND '2023-12-31'
ORDER BY 
    t.data_transacao DESC;

-- 5. Resumo de gastos por categoria
SELECT 
    c.nome AS categoria,
    SUM(t.valor) AS total_gasto
FROM 
    financas_pessoais.transacoes t
JOIN 
    financas_pessoais.categorias c ON t.categoria_id = c.id
WHERE 
    t.tipo = 'D' -- Despesas
    AND t.data_transacao BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY 
    c.nome
ORDER BY 
    total_gasto DESC;

-- 6. Resumo de receitas por categoria
SELECT 
    c.nome AS categoria,
    SUM(t.valor) AS total_receita
FROM 
    financas_pessoais.transacoes t
JOIN 
    financas_pessoais.categorias c ON t.categoria_id = c.id
WHERE 
    t.tipo = 'R' -- Receitas
    AND t.data_transacao BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY 
    c.nome
ORDER BY 
    total_receita DESC;

-- 7. Balanço mensal (receitas - despesas)
SELECT 
    FORMAT(t.data_transacao, 'yyyy-MM') AS mes,
    SUM(CASE WHEN t.tipo = 'R' THEN t.valor ELSE 0 END) AS total_receitas,
    SUM(CASE WHEN t.tipo = 'D' THEN t.valor ELSE 0 END) AS total_despesas,
    SUM(CASE WHEN t.tipo = 'R' THEN t.valor ELSE -t.valor END) AS saldo
FROM 
    financas_pessoais.transacoes t
WHERE 
    t.data_transacao BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY 
    FORMAT(t.data_transacao, 'yyyy-MM')
ORDER BY 
    mes;

-- 8. Verificar progresso das metas
SELECT 
    m.nome,
    m.valor_alvo,
    m.valor_atual,
    m.data_inicio,
    m.data_fim,
    c.nome AS categoria,
    CAST((m.valor_atual / m.valor_alvo) * 100 AS DECIMAL(5,2)) AS percentual_concluido,
    CASE 
        WHEN m.concluida = 1 THEN 'Concluída'
        WHEN GETDATE() > m.data_fim THEN 'Vencida'
        ELSE 'Em andamento'
    END AS status
FROM 
    financas_pessoais.metas m
LEFT JOIN 
    financas_pessoais.categorias c ON m.categoria_id = c.id
ORDER BY 
    m.data_fim;

-- 9. Listar meios de pagamento por conta
SELECT 
    mp.nome AS meio_pagamento,
    mp.tipo,
    cd.nome AS conta,
    cd.instituicao
FROM 
    financas_pessoais.meios_pagamento mp
LEFT JOIN 
    financas_pessoais.conta_dimensao cd ON mp.conta_id = cd.id
ORDER BY 
    cd.nome, mp.nome;

-- 10. Verificar categorias hierárquicas
WITH CategoriaHierarquia AS (
    SELECT 
        id,
        nome,
        categoria_pai_id,
        nivel,
        CAST(nome AS NVARCHAR(500)) AS caminho
    FROM 
        financas_pessoais.categorias
    WHERE 
        categoria_pai_id IS NULL
    
    UNION ALL
    
    SELECT 
        c.id,
        c.nome,
        c.categoria_pai_id,
        c.nivel,
        CAST(ch.caminho + ' > ' + c.nome AS NVARCHAR(500))
    FROM 
        financas_pessoais.categorias c
    JOIN 
        CategoriaHierarquia ch ON c.categoria_pai_id = ch.id
)
SELECT 
    id,
    nome,
    nivel,
    caminho
FROM 
    CategoriaHierarquia
ORDER BY 
    caminho;