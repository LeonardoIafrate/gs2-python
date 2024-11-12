import oracledb
from fastapi import HTTPException
from bd.connection import *
from validacao import valida_cpf, valida_email, valida_endereco, valida_nome, valida_senha, valida_data_nascimento


def busca_usuario(cpf: str):
    try:
        cur.execute("SELECT * FROM USUARIO WHERE CPF_CLIENTE = :cpf", {"cpf": cpf})
        usuario = cur.fetchone()
        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
    except oracledb.IntegrityError as e:
        print("Erro de integridade", e)
        return{"Error": f"Erro de integridade {str(e)}"}
    


def cadastra_usuario(cpf: str, nome: str, email: str, endereco: str, senha: str, data: str):
    try:
        cpf_valido = valida_cpf(cpf)
        if not cpf_valido:
            raise HTTPException(status_code=422, detail="CPF inválido")
        if not valida_nome(nome):
            raise HTTPException(status_code=422, detail="Nome inválido")
        if not valida_email(email):
            raise HTTPException(status_code=422, detail="E-mail inválido")
        if not valida_endereco(endereco):
            raise HTTPException(status_code=422, detail="Endereço inválido")
        if not valida_senha(senha):
            raise HTTPException(status_code=422, detail="Senha inválida")
        if not valida_data_nascimento(data):
            raise HTTPException(status_code=422, detail="Data de nascimento inválida")
        
        cur.execute(
            """
            INSERT INTO USUARIO (CPF_USUARIO, NOME_USUARIO, EMAIL, ENDERECO, SENHA, DATA_NASCIMENTO)
            VALUES (:cpf, :nome, :email, :endereco, :senha, :data)
            """, {"cpf": cpf, "nome": nome, "email": email, "endereco": endereco, "senha": senha, "data": data})
        
        print("Usuário cadastrado com sucesso")
        return{"Message": "Usuário cadastrado com sucesso"}

    except oracledb.IntegrityError as e:
        print("Erro de integridade", e)
        return {"Error": f"Erro de integridade {str(e)}"}
    
def exclui_usuario(cpf: str):
    cur.execute("SELECT * FROM USUARIO WHERE CPF_USUARIO = :cpf", {"cpf": cpf})
    usuario_cadastrado = cur.fetchone()
    
    if usuario_cadastrado is None:
        print("Erro 404: Usuário não encontrado")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    try:
        cur.execute("DELETE FROM USUARIO WHERE CPF_USUARIO = :cpf", {"cpf": cpf})
        con.commit()
        print("Usuário excluído com sucesso")
        return {"Message": "Usuário excluído com sucesso"}
    except oracledb.IntegrityError as e:
        print("Erro de integridade", e)
        return {"Error": f"Erro de integridade {str(e)}"}