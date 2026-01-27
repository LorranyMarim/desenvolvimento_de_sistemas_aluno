from flask import Flask, render_template, request, redirect, url_for
from data_base import conectar_database

app = Flask(__name__)

# Função auxiliar para garantir que sempre teremos o banco e o cursor à mão
def obter_conexao_e_cursor():
    db = conectar_database()
    if db is not None:
        cursor = db.cursor(dictionary=True)
        return db, cursor
    return None, None

# No seu app.py, adicione ou ajuste estas rotas:

@app.route('/') # Rota raiz (padrão)
@app.route('/index') # Rota específica /index
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 1. Coleta de dados do formulário
        email_digitado = request.form.get('email')
        senha_digitada = request.form.get('senha')

        # 2. Tentativa de conexão
        db, cursor = obter_conexao_e_cursor()
        
        if db is None:
            return render_template('login.html', erro="Erro crítico: Banco de dados offline.")

        # 3. Lógica de busca: verificamos se o usuário existe
        comando_busca = "SELECT * FROM usuario WHERE email = %s"
        cursor.execute(comando_busca, (email_digitado,))
        usuario_encontrado = cursor.fetchone()

        # 4. Validação passo a passo
        mensagem_erro = None

        if usuario_encontrado is None:
            mensagem_erro = "Este e-mail não está cadastrado em nosso sistema."
        else:
            # Se o usuário existe, comparamos a senha
            if usuario_encontrado['senha'] != senha_digitada:
                mensagem_erro = "Senha incorreta. Tente novamente."

        # 5. Fechamento de recursos (Boa prática em qualquer linguagem)
        cursor.close()
        db.close()

        # 6. Decisão final: Redireciona ou volta para a tela com erro
        if mensagem_erro is None:
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erro=mensagem_erro)

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # 1. Coleta de dados
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        # 2. Validação básica de lógica (antes de tocar no banco)
        if senha != confirmar_senha:
            return render_template('cadastro.html', erro="As senhas digitadas não são iguais.")

        db, cursor = obter_conexao_e_cursor()
        if db is None:
            return render_template('cadastro.html', erro="Erro ao conectar ao servidor.")

        # 3. Verificação de duplicidade (Não podemos cadastrar o mesmo e-mail duas vezes)
        cursor.execute("SELECT id_usuario FROM usuario WHERE email = %s", (email,))
        if cursor.fetchone() is not None:
            cursor.close()
            db.close()
            return render_template('cadastro.html', erro="Este e-mail já está em uso.")

        # 4. Inserção de dados (Uso de %s para evitar SQL Injection)
        try:
            comando_insert = "INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)"
            cursor.execute(comando_insert, (nome, email, senha))
            
            # MUITO IMPORTANTE: Em operações de escrita, precisamos do COMMIT
            db.commit() 
            
            sucesso = True
        except:
            db.rollback() # Cancela se algo der errado
            sucesso = False
        finally:
            cursor.close()
            db.close()

        if sucesso:
            return redirect(url_for('login'))
        else:
            return render_template('cadastro.html', erro="Erro ao salvar os dados. Tente mais tarde.")

    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)