from validacao import valida_cpf, valida_email, valida_nome, valida_senha
import oracledb
from fastapi import HTTPException
from bd.connection import *

def cadastra_admin(cpf: str, email: str, nome: str, senha: str):
    try:        
        if not valida_cpf(cpf):
            raise HTTPException (status_code=422, detail="CPF inválido")
        if not valida_email(email):
            raise HTTPException (status_code=422, detail="Email inválido")
        if not valida_nome(nome):
            raise HTTPException (status_code=422, detail="Nome inválido")
        if not valida_senha(senha):
            raise HTTPException (status_code=422, detail="Senha inválida")
        
        cur.execute(
            """
            INSERT INTO ADMIN (CPF_ADMIN, EMAIL_ADMIN, NOME_ADMIN, SENHA)
            VALUES (:cpf, :email, :nome, :senha)
            """, {"cpf": cpf, "email": email, "nome": nome, "senha": senha}
            )
        con.commit()

        return{"Message": "Administrador cadastrado com sucesso"}
    
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code=500, detail=f"Erro de integridade {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro {str(e)}")


def exclui_admin(cpf: str):
    cur.execute("SELECT * FROM ADMIN WHERE CPF_ADMIN = :cpf", {"cpf": cpf})
    admin_cadastrado = cur.fetchone()
    if admin_cadastrado is None:
        raise HTTPException(status_code=404, detail="Admin não encontrado")
    try:
        cur.execute("DELETE FROM ADMIN WHERE CPF_ADMIN = :cpf", {"cpf": cpf})
        con.commit()

        return{"Message": "Admin excluido com sucesso"}
    
    except oracledb.IntegrityError as e:
        raise HTTPException (status_code=500, detail=f"Erro de integridade: {str(e)}")
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"Erro: {str(e)}")