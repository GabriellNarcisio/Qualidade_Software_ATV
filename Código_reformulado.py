#!/usr/bin/env python3
"""
Sistema PharmAnalytics: Sistema para gerenciamento de farmácias e produtos.
Utiliza SQLite para armazenamento dos dados.
"""

import sqlite3


class BancoDeDados:
    """
    Gerencia a conexão e a criação das tabelas do banco de dados.
    """

    NOME_DB = 'pharmanalytics.db'

    @staticmethod
    def conectar() -> sqlite3.Connection:
        """
        Estabelece e retorna uma conexão com o banco de dados SQLite.
        """
        try:
            return sqlite3.connect(BancoDeDados.NOME_DB)
        except sqlite3.Error as e:
            print(f"Erro ao conectar com o banco de dados: {e}")
            return None

    @staticmethod
    def criar_tabelas() -> None:
        """
        Cria as tabelas necessárias se elas não existirem.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                # Tabela Pessoa
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS pessoa (
                        cpf INTEGER PRIMARY KEY
                    )'''
                )
                # Tabela Administrador
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS administrador (
                        email VARCHAR(100),
                        senha VARCHAR(50),
                        cod_pessoa INTEGER,
                        FOREIGN KEY (cod_pessoa) REFERENCES pessoa(cpf)
                    )'''
                )
                # Tabela Usuário
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS usuario (
                        cod_pessoa INTEGER PRIMARY KEY,
                        FOREIGN KEY (cod_pessoa) REFERENCES pessoa(cpf)
                    )'''
                )
                # Tabela Tel_Usuario
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS tel_usuario (
                        numero VARCHAR(20),
                        cod_usuario INTEGER,
                        FOREIGN KEY (cod_usuario) REFERENCES usuario(cod_pessoa)
                    )'''
                )
                # Tabela Farmácia
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS farmacia (
                        cod INTEGER PRIMARY KEY,
                        nome VARCHAR(100),
                        rua VARCHAR(100),
                        num INTEGER,
                        bairro VARCHAR(50),
                        cep VARCHAR(20),
                        hora_inicio VARCHAR(5),
                        hora_fim VARCHAR(5),
                        dia_funcionamento VARCHAR(20),
                        cod_admin INTEGER,
                        FOREIGN KEY (cod_admin) REFERENCES administrador(cod_pessoa)
                    )'''
                )
                # Tabela Tel_Farmácia
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS tel_farmacia (
                        numero VARCHAR(20),
                        cod_farmacia INTEGER,
                        FOREIGN KEY (cod_farmacia) REFERENCES farmacia(cod)
                    )'''
                )
                # Tabela Estoque
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS estoque (
                        cod INTEGER PRIMARY KEY,
                        quantidade INTEGER
                    )'''
                )
                # Tabela Produto
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS produto (
                        cod INTEGER PRIMARY KEY,
                        nome VARCHAR(100),
                        preco DOUBLE PRECISION,
                        cod_admin INTEGER,
                        cod_estoque INTEGER,
                        FOREIGN KEY (cod_admin) REFERENCES administrador(cod_pessoa),
                        FOREIGN KEY (cod_estoque) REFERENCES estoque(cod)
                    )'''
                )
                # Tabela Categoria_Produto
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS categoria_produto (
                        categoria VARCHAR(50),
                        cod_produto INTEGER,
                        FOREIGN KEY (cod_produto) REFERENCES produto(cod)
                    )'''
                )
                # Tabela Usuário_Produto
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS usuario_produto (
                        cod_usuario INTEGER,
                        cod_produto INTEGER,
                        FOREIGN KEY (cod_usuario) REFERENCES usuario(cod_pessoa),
                        FOREIGN KEY (cod_produto) REFERENCES produto(cod)
                    )'''
                )
                # Tabela Usuário_Farmácia
                cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS usuario_farmacia (
                        cod_usuario INTEGER,
                        cod_farmacia INTEGER,
                        FOREIGN KEY (cod_usuario) REFERENCES usuario(cod_pessoa),
                        FOREIGN KEY (cod_farmacia) REFERENCES farmacia(cod)
                    )'''
                )
                conn.commit()
            except sqlite3.Error as e:
                print(f"Erro ao criar tabelas: {e}")
            finally:
                conn.close()


class OperacoesAdministrador:
    """
    Operações relacionadas ao administrador do sistema.
    """
    admin_atual = None

    @staticmethod
    def cadastrar_administrador() -> None:
        """
        Realiza o cadastro de um novo administrador.
        Solicita CPF, e-mail e senha.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                cpf = int(input("CPF: "))
                email = input("E-mail: ")
                senha = input("Senha: ")
                cursor = conn.cursor()
                # Insere CPF na tabela pessoa
                cursor.execute('INSERT INTO pessoa (cpf) VALUES (?)', (cpf,))
                # Insere administrador na tabela administrador
                cursor.execute(
                    '''INSERT INTO administrador (email, senha, cod_pessoa)
                       VALUES (?, ?, ?)''', (email, senha, cpf)
                )
                conn.commit()
                print("Administrador cadastrado com sucesso!")
                # Autentica logo após o cadastro
                OperacoesAdministrador.autenticar_administrador()
            except sqlite3.IntegrityError:
                print("Erro: CPF já existe.")
            except sqlite3.Error as e:
                print(f"Erro ao cadastrar administrador: {e}")
            finally:
                conn.close()

    @staticmethod
    def autenticar_administrador() -> bool:
        """
        Autentica um administrador.
        Solicita CPF e senha.
        Retorna True se a autenticação for bem-sucedida.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                print("\nLOGIN")
                cpf = int(input("Digite o CPF: "))
                senha = input("Digite a senha: ")
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM administrador WHERE cod_pessoa = ? AND senha = ?',
                    (cpf, senha)
                )
                admin = cursor.fetchone()
                if admin:
                    OperacoesAdministrador.admin_atual = cpf
                    return True
                else:
                    print("Credenciais inválidas!")
                    return False
            except sqlite3.Error as e:
                print(f"Erro ao autenticar administrador: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def administrador_existe() -> bool:
        """
        Verifica se já existe ao menos um administrador cadastrado.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM administrador')
                count = cursor.fetchone()[0]
                return count > 0
            except sqlite3.Error as e:
                print(f"Erro ao verificar administradores: {e}")
                return False
            finally:
                conn.close()
        return False


class OperacoesUsuario:
    """
    Operações relacionadas ao cadastro de usuários.
    """

    @staticmethod
    def cadastrar_usuario() -> None:
        """
        Realiza o cadastro de um novo usuário.
        Solicita CPF e telefone.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                cpf = int(input("CPF: "))
                telefone = input("Telefone: ")
                cursor = conn.cursor()
                # Insere CPF na tabela pessoa
                cursor.execute('INSERT INTO pessoa (cpf) VALUES (?)', (cpf,))
                # Insere usuário na tabela usuario
                cursor.execute('INSERT INTO usuario (cod_pessoa) VALUES (?)', (cpf,))
                # Insere telefone na tabela tel_usuario
                cursor.execute(
                    'INSERT INTO tel_usuario (numero, cod_usuario) VALUES (?, ?)',
                    (telefone, cpf)
                )
                conn.commit()
                print("Usuário cadastrado com sucesso!")
            except sqlite3.IntegrityError:
                print("Já existe um usuário com este CPF.")
            except sqlite3.Error as e:
                print(f"Erro ao cadastrar usuário: {e}")
            finally:
                conn.close()


class OperacoesFarmacia:
    """
    Operações relacionadas ao gerenciamento de farmácias.
    """

    @staticmethod
    def cadastrar_farmacia() -> None:
        """
        Realiza o cadastro de uma nova farmácia.
        Solicita os dados da farmácia e os registra no banco.
        """
        if OperacoesAdministrador.admin_atual is None:
            print("É necessário estar autenticado como administrador para cadastrar farmácias.")
            return

        conn = BancoDeDados.conectar()
        if conn:
            try:
                codigo = int(input("Código da farmácia: "))
                nome = input("Nome da farmácia: ")
                telefone = input("Telefone: ")
                rua = input("Rua: ")
                numero = int(input("Número: "))
                bairro = input("Bairro: ")
                cep = input("CEP: ")
                hora_inicio = input("Horário de abertura (HH:mm): ")
                hora_fim = input("Horário de fechamento (HH:mm): ")
                dia_funcionamento = input("Dia(s) de funcionamento (ex: Segunda-Sexta): ")
                cursor = conn.cursor()
                # Insere dados na tabela farmacia
                cursor.execute(
                    '''INSERT INTO farmacia (cod, nome, rua, num, bairro, cep,
                       hora_inicio, hora_fim, dia_funcionamento, cod_admin)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (codigo, nome, rua, numero, bairro, cep, hora_inicio,
                     hora_fim, dia_funcionamento, OperacoesAdministrador.admin_atual)
                )
                # Insere telefone na tabela tel_farmacia
                cursor.execute(
                    'INSERT INTO tel_farmacia (numero, cod_farmacia) VALUES (?, ?)',
                    (telefone, codigo)
                )
                conn.commit()
                print("Farmácia cadastrada com sucesso!")
            except sqlite3.IntegrityError:
                print("Código da farmácia já existe.")
            except sqlite3.Error as e:
                print(f"Erro ao cadastrar farmácia: {e}")
            finally:
                conn.close()

    @staticmethod
    def atualizar_farmacia() -> None:
        """
        Atualiza os dados de uma farmácia cadastrada.
        Solicita os novos dados a partir do código informado.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                codigo = int(input("Código da farmácia a ser atualizada: "))
                nome = input("Novo nome da farmácia: ")
                telefone = input("Novo telefone: ")
                rua = input("Nova rua: ")
                numero = int(input("Novo número: "))
                bairro = input("Novo bairro: ")
                cep = input("Novo CEP: ")
                hora_inicio = input("Novo horário de abertura (HH:mm): ")
                hora_fim = input("Novo horário de fechamento (HH:mm): ")
                dia_funcionamento = input("Novo dia(s) de funcionamento: ")
                cursor = conn.cursor()
                cursor.execute(
                    '''UPDATE farmacia SET nome = ?, rua = ?, num = ?, bairro = ?,
                       cep = ?, hora_inicio = ?, hora_fim = ?, dia_funcionamento = ?
                       WHERE cod = ?''',
                    (nome, rua, numero, bairro, cep, hora_inicio, hora_fim,
                     dia_funcionamento, codigo)
                )
                cursor.execute(
                    'UPDATE tel_farmacia SET numero = ? WHERE cod_farmacia = ?',
                    (telefone, codigo)
                )
                if cursor.rowcount == 0:
                    print("Farmácia não encontrada.")
                else:
                    conn.commit()
                    print("Dados da farmácia atualizados com sucesso!")
            except sqlite3.Error as e:
                print(f"Erro ao atualizar farmácia: {e}")
            finally:
                conn.close()

    @staticmethod
    def excluir_farmacia() -> None:
        """
        Exclui uma farmácia a partir do código informado.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                codigo = int(input("Código da farmácia a ser excluída: "))
                cursor = conn.cursor()
                cursor.execute('DELETE FROM farmacia WHERE cod = ?', (codigo,))
                if cursor.rowcount == 0:
                    print("Farmácia não encontrada.")
                else:
                    conn.commit()
                    print("Farmácia excluída com sucesso!")
            except sqlite3.Error as e:
                print(f"Erro ao excluir farmácia: {e}")
            finally:
                conn.close()

    @staticmethod
    def consultar_farmacias() -> None:
        """
        Consulta as farmácias que estão em funcionamento em um determinado intervalo de horário.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                hora_inicio = input("Informe a hora de início (HH:mm): ")
                hora_fim = input("Informe a hora de término (HH:mm): ")
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT * FROM farmacia
                       WHERE hora_inicio <= ? AND hora_fim >= ?''',
                    (hora_inicio, hora_fim)
                )
                farmacias = cursor.fetchall()
                if farmacias:
                    print("Farmácias em funcionamento:")
                    for farmacia in farmacias:
                        print(f"Farmácia: {farmacia[1]}, Endereço: {farmacia[2]}, "
                              f"{farmacia[3]}, {farmacia[4]}, {farmacia[5]}")
                        cursor.execute(
                            'SELECT numero FROM tel_farmacia WHERE cod_farmacia = ?',
                            (farmacia[0],)
                        )
                        telefone = cursor.fetchone()
                        if telefone:
                            print(f"Telefone: {telefone[0]}")
                else:
                    print("Nenhuma farmácia encontrada no horário informado.")
            except sqlite3.Error as e:
                print(f"Erro ao consultar farmácias: {e}")
            finally:
                conn.close()


class OperacoesProdutos:
    """
    Operações relacionadas ao gerenciamento de produtos.
    """

    @staticmethod
    def cadastrar_produto() -> None:
        """
        Realiza o cadastro de um novo produto.
        Solicita código, nome, categoria, preço e quantidade.
        """
        if OperacoesAdministrador.admin_atual is None:
            print("É necessário estar autenticado como administrador para cadastrar produtos.")
            return

        conn = BancoDeDados.conectar()
        if conn:
            try:
                codigo = int(input("Código do produto: "))
                nome = input("Nome do produto: ")
                categoria = input("Categoria do produto: ")
                preco = float(input("Preço do produto: R$ "))
                quantidade = int(input("Quantidade do produto: "))
                cursor = conn.cursor()
                # Insere dados na tabela produto
                cursor.execute(
                    '''INSERT INTO produto (cod, nome, preco, cod_admin, cod_estoque)
                       VALUES (?, ?, ?, ?, ?)''',
                    (codigo, nome, preco, OperacoesAdministrador.admin_atual, codigo)
                )
                # Insere categoria na tabela categoria_produto
                cursor.execute(
                    '''INSERT INTO categoria_produto (categoria, cod_produto)
                       VALUES (?, ?)''', (categoria, codigo)
                )
                # Insere quantidade na tabela estoque
                cursor.execute(
                    '''INSERT INTO estoque (cod, quantidade)
                       VALUES (?, ?)''', (codigo, quantidade)
                )
                conn.commit()
                print("Produto cadastrado com sucesso!")
            except sqlite3.IntegrityError:
                print("Já existe um produto com este código.")
            except sqlite3.Error as e:
                print(f"Erro ao cadastrar produto: {e}")
            finally:
                conn.close()

    @staticmethod
    def atualizar_produto() -> None:
        """
        Atualiza os dados de um produto.
        Solicita novos dados a partir do código informado.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                codigo = int(input("Código do produto a ser atualizado: "))
                nome = input("Novo nome do produto: ")
                categoria = input("Nova categoria do produto: ")
                preco = float(input("Novo preço do produto: R$ "))
                quantidade = int(input("Nova quantidade do produto: "))
                cursor = conn.cursor()
                cursor.execute(
                    '''UPDATE produto SET nome = ?, preco = ?
                       WHERE cod = ?''',
                    (nome, preco, codigo)
                )
                cursor.execute(
                    '''UPDATE estoque SET quantidade = ?
                       WHERE cod = ?''',
                    (quantidade, codigo)
                )
                cursor.execute(
                    '''UPDATE categoria_produto SET categoria = ?
                       WHERE cod_produto = ?''',
                    (categoria, codigo)
                )
                if cursor.rowcount == 0:
                    print("Produto não encontrado.")
                else:
                    conn.commit()
                    print("Dados do produto atualizados com sucesso!")
            except sqlite3.Error as e:
                print(f"Erro ao atualizar produto: {e}")
            finally:
                conn.close()

    @staticmethod
    def excluir_produto() -> None:
        """
        Exclui um produto a partir do código informado.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                codigo = int(input("Código do produto a ser excluído: "))
                cursor = conn.cursor()
                cursor.execute('DELETE FROM produto WHERE cod = ?', (codigo,))
                cursor.execute('DELETE FROM categoria_produto WHERE cod_produto = ?', (codigo,))
                cursor.execute('DELETE FROM estoque WHERE cod = ?', (codigo,))
                if cursor.rowcount == 0:
                    print("Produto não encontrado.")
                else:
                    conn.commit()
                    print("Produto excluído com sucesso!")
            except sqlite3.Error as e:
                print(f"Erro ao excluir produto: {e}")
            finally:
                conn.close()

    @staticmethod
    def buscar_produto() -> None:
        """
        Busca um produto a partir do nome.
        Exibe os detalhes do produto caso seja encontrado.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                nome = input("Informe o nome do produto: ")
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM produto WHERE LOWER(nome) = ?',
                    (nome.lower(),)
                )
                produto = cursor.fetchone()
                if not produto:
                    print("Produto não encontrado.")
                    return
                cursor.execute(
                    'SELECT categoria FROM categoria_produto WHERE cod_produto = ?',
                    (produto[0],)
                )
                categoria = cursor.fetchone()
                cursor.execute(
                    'SELECT quantidade FROM estoque WHERE cod = ?',
                    (produto[0],)
                )
                estoque = cursor.fetchone()
                print(f"Produto encontrado: {produto[1]} - Categoria: {categoria[0]} - "
                      f"Preço: R${produto[2]:.2f} - Quantidade: {estoque[0]}")
            except sqlite3.Error as e:
                print(f"Erro ao buscar produto: {e}")
            finally:
                conn.close()

    @staticmethod
    def decrementar_estoque() -> None:
        """
        Decrementa a quantidade de um produto no estoque.
        Solicita o nome do produto e a quantidade a ser decrementada.
        """
        conn = BancoDeDados.conectar()
        if conn:
            try:
                nome = input("Informe o nome do produto: ")
                quantidade = int(input("Quantidade a ser decrementada: "))
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM produto WHERE LOWER(nome) = ?',
                    (nome.lower(),)
                )
                produto = cursor.fetchone()
                if not produto:
                    print("Produto não encontrado.")
                    return
                cursor.execute(
                    'SELECT quantidade FROM estoque WHERE cod = ?',
                    (produto[0],)
                )
                estoque = cursor.fetchone()
                nova_quantidade = estoque[0] - quantidade
                if nova_quantidade < 0:
                    print("Quantidade para decrementar é maior que a disponível.")
                    return
                cursor.execute(
                    'UPDATE estoque SET quantidade = ? WHERE cod = ?',
                    (nova_quantidade, produto[0])
                )
                conn.commit()
                print("Estoque decrementado com sucesso!")
            except sqlite3.Error as e:
                print(f"Erro ao decrementar estoque: {e}")
            finally:
                conn.close()


def menu() -> None:
    """
    Exibe o menu principal e direciona a opção escolhida para a operação correspondente.
    """
    # Inicializa o banco de dados e as tabelas
    BancoDeDados.criar_tabelas()

    # Verifica se há um administrador cadastrado; se não houver, solicita o cadastro inicial.
    if not OperacoesAdministrador.administrador_existe():
        print("Nenhum administrador cadastrado. Realize o cadastro inicial.")
        OperacoesAdministrador.cadastrar_administrador()
    else:
        if not OperacoesAdministrador.autenticar_administrador():
            print("Acesso negado. Tente novamente!")
            return

    while True:
        try:
            opcao = int(input(
                "\nBem-vindo ao PharmAnalytics! Selecione uma opção:\n"
                "1  -  Cadastrar administrador\n"
                "2  -  Cadastrar usuário\n"
                "3  -  Cadastrar farmácia\n"
                "4  -  Cadastrar produto\n"
                "5  -  Atualizar farmácia\n"
                "6  -  Atualizar produto\n"
                "7  -  Excluir farmácia\n"
                "8  -  Excluir produto\n"
                "9  -  Consultar farmácias\n"
                "10 -  Buscar produto\n"
                "11 -  Decrementar estoque\n"
                "0  -  Sair\n"
                "Opção: "
            ))
            if opcao == 1:
                OperacoesAdministrador.cadastrar_administrador()
            elif opcao == 2:
                OperacoesUsuario.cadastrar_usuario()
            elif opcao == 3:
                OperacoesFarmacia.cadastrar_farmacia()
            elif opcao == 4:
                OperacoesProdutos.cadastrar_produto()
            elif opcao == 5:
                OperacoesFarmacia.atualizar_farmacia()
            elif opcao == 6:
                OperacoesProdutos.atualizar_produto()
            elif opcao == 7:
                OperacoesFarmacia.excluir_farmacia()
            elif opcao == 8:
                OperacoesProdutos.excluir_produto()
            elif opcao == 9:
                OperacoesFarmacia.consultar_farmacias()
            elif opcao == 10:
                OperacoesProdutos.buscar_produto()
            elif opcao == 11:
                OperacoesProdutos.decrementar_estoque()
            elif opcao == 0:
                print("Saindo do sistema. Até logo!")
                break
            else:
                print("Opção inválida. Tente novamente!")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")


if __name__ == '__main__':
    menu()
