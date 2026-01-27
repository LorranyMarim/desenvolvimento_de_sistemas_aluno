import mysql.connector
def conectar_database():
    try:
        conexao = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "root",
            database = "validacao_dados"
        )
        return conexao
    except:
        return None