from validacao import valida_cpf, valida_email, valida_nome, valida_endereco, valida_data_nascimento
from datetime import datetime
import oracledb
from fastapi import HTTPException
from bd.connection import *


def busca_cliente(cpf: str):
    try:
        cur.execute("SELECT * FROM CLI WHERE CPF_CLIENTE = :cpf", {"cpf": cpf})
        resultado = cur.fetchall()
        if resultado is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return resultado
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    except Exception as e:
        raise HTTPException(status_code="Erro", detail=e)


def cadastra_cliente(cpf: str, email: str, nome: str, endereco: str, data_nascimento: str):
    try:
        if not valida_cpf(cpf):
            raise HTTPException(status_code=422, detail="CPF inválido")
        if not valida_email(email):
            raise HTTPException(status_code=422, detail="E-mail inválido")
        if not valida_nome(nome):
            raise HTTPException(status_code=422, detail="Nome inválido")
        if not valida_endereco(endereco):
            raise HTTPException(status_code=422, detail="Endereço inválido")
        
        data_valida = valida_data_nascimento(data_nascimento)
        if data_valida:
            cur.execute(
                """
                INSERT INTO CLI (CPF_CLIENTE, EMAIL_CLIENTE, NOME_CLIENTE, ENDERECO_CLIENTE, DATA_NASCIMENTO)
                VALUES (:cpf, :email, :nome, :endereco, TO_DATE(:data_nascimento, 'YYYY-MM-DD'))
                """, {"cpf": cpf, "email": email, "nome": nome, "endereco": endereco, "data_nascimento": data_nascimento}
                )
            
            con.commit()

            return{"Message": "Cliente cadastrado com sucesso"}

    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    except Exception as e:
        raise HTTPException(status_code="Error", detail=e)
    

def exclui_cliente(cpf:str):
    cpf_valido = valida_cpf(cpf)

    cur.execute("SELECT * FROM CLI WHERE CPF_CLIENTE = :cpf", {"cpf": cpf_valido})
    cliente_cadastrado = cur.fetchone()

    if cliente_cadastrado is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    try:
        cur.execute("DELETE FROM CLI WHERE CPF_CLIENTE = :cpf", {"cpf": cpf_valido})
        con.commit()

        return{"Message": "Cliente excluido com sucesso"}

    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    except Exception as e:
        raise HTTPException(status_code="Error", detail=e)