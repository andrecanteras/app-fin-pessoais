-- create_test_data.sql
-- Script para criar dados de teste

-- Inserir uma conta de teste se não existir
IF NOT EXISTS (SELECT TOP 1 * FROM financas_pessoais.contas)
BEGIN
    INSERT INTO financas_pessoais.contas (nome, tipo, saldo_inicial, saldo_atual, instituicao)
    VALUES ('Conta Corrente', 'Corrente', 1000.00, 1000.00, 'Banco do Brasil');
    
    PRINT 'Conta de teste inserida com sucesso.';
END
ELSE
BEGIN
    PRINT 'Contas já existem, nenhuma conta de teste foi inserida.';
END

-- Inserir algumas transações de teste
IF NOT EXISTS (SELECT TOP 1 * FROM financas_pessoais.transacoes)
BEGIN
    DECLARE @conta_id INT;
    SELECT @conta_id = id FROM financas_pessoais.contas WHERE nome = 'Conta Corrente';
    
    DECLARE @categoria_salario INT;
    DECLARE @categoria_alimentacao INT;
    DECLARE @categoria_moradia INT;
    
    SELECT @categoria_salario = id FROM financas_pessoais.categorias WHERE nome = 'Salário';
    SELECT @categoria_alimentacao = id FROM financas_pessoais.categorias WHERE nome = 'Alimentação';
    SELECT @categoria_moradia = id FROM financas_pessoais.categorias WHERE nome = 'Moradia';
    
    -- Inserir transações
    INSERT INTO financas_pessoais.transacoes (descricao, valor, data_transacao, tipo, categoria_id, conta_id, observacao)
    VALUES 
        ('Salário Mensal', 5000.00, DATEADD(day, -15, GETDATE()), 'R', @categoria_salario, @conta_id, 'Salário do mês'),
        ('Supermercado', 350.00, DATEADD(day, -10, GETDATE()), 'D', @categoria_alimentacao, @conta_id, 'Compras semanais'),
        ('Aluguel', 1200.00, DATEADD(day, -5, GETDATE()), 'D', @categoria_moradia, @conta_id, 'Aluguel do mês');
    
    -- Atualizar saldo da conta
    UPDATE financas_pessoais.contas
    SET saldo_atual = saldo_inicial + 
        (SELECT SUM(CASE WHEN tipo = 'R' THEN valor ELSE -valor END) 
         FROM financas_pessoais.transacoes 
         WHERE conta_id = @conta_id)
    WHERE id = @conta_id;
    
    PRINT 'Transações de teste inseridas com sucesso.';
END
ELSE
BEGIN
    PRINT 'Transações já existem, nenhuma transação de teste foi inserida.';
END
