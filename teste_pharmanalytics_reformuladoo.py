import unittest
import sqlite3
from pharmanalytics_reformulado import cadastrar_usuario, cadastrar_farmacia, cadastrar_produto, atualizar_produto, excluir_produto, buscar_produto

class TestPharmanalytics(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Cria um banco de dados temporário para os testes"""
        cls.conn = sqlite3.connect(':memory:')
        cls.cursor = cls.conn.cursor()
        
        # Criar tabelas temporárias para os testes
        cls.cursor.executescript('''
            CREATE TABLE usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL
            );
            CREATE TABLE farmacia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                endereco TEXT NOT NULL
            );
            CREATE TABLE produto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL,
                estoque INTEGER NOT NULL,
                farmacia_id INTEGER NOT NULL,
                FOREIGN KEY (farmacia_id) REFERENCES farmacia(id)
            );
        ''')
        cls.conn.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Fecha a conexão após os testes"""
        cls.conn.close()
    
    def test_cadastrar_usuario(self):
        """Teste unitário: cadastra um usuário e verifica se foi inserido corretamente."""
        cadastrar_usuario(self.conn, 'João', 'joao@email.com', 'senha123')
        self.cursor.execute("SELECT * FROM usuario WHERE email = ?", ('joao@email.com',))
        usuario = self.cursor.fetchone()
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario[1], 'João')
    
    def test_cadastrar_e_buscar_farmacia(self):
        """Teste de integração: cadastra uma farmácia e verifica se a consulta funciona."""
        cadastrar_farmacia(self.conn, 'Farmácia Central', 'Rua A, 123')
        self.cursor.execute("SELECT * FROM farmacia WHERE nome = ?", ('Farmácia Central',))
        farmacia = self.cursor.fetchone()
        self.assertIsNotNone(farmacia)
        self.assertEqual(farmacia[1], 'Farmácia Central')
    
    def test_fluxo_completo_produto(self):
        """Teste de sistema: fluxo de cadastrar, atualizar e deletar um produto."""
        cadastrar_farmacia(self.conn, 'Farmácia Teste', 'Rua B, 456')
        self.cursor.execute("SELECT id FROM farmacia WHERE nome = ?", ('Farmácia Teste',))
        farmacia_id = self.cursor.fetchone()[0]
        
        # Cadastro de produto
        cadastrar_produto(self.conn, 'Paracetamol', '500mg - Analgésico', 10.0, 50, farmacia_id)
        self.cursor.execute("SELECT * FROM produto WHERE nome = ?", ('Paracetamol',))
        produto = self.cursor.fetchone()
        self.assertIsNotNone(produto)
        
        # Atualização do produto
        atualizar_produto(self.conn, produto[0], nome='Paracetamol 750mg', preco=12.0)
        self.cursor.execute("SELECT * FROM produto WHERE id = ?", (produto[0],))
        produto_atualizado = self.cursor.fetchone()
        self.assertEqual(produto_atualizado[1], 'Paracetamol 750mg')
        self.assertEqual(produto_atualizado[3], 12.0)
        
        # Exclusão do produto
        excluir_produto(self.conn, produto[0])
        self.cursor.execute("SELECT * FROM produto WHERE id = ?", (produto[0],))
        produto_excluido = self.cursor.fetchone()
        self.assertIsNone(produto_excluido)

if __name__ == '__main__':
    unittest.main()
