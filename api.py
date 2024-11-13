from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from bd.admin import cadastra_admin, exclui_admin
from bd.cliente import busca_cliente, cadastra_cliente, exclui_cliente
from bd.connection import *
from validacao import valida_cpf, valida_data_nascimento, valida_email, valida_endereco, valida_nome, valida_senha

app = FastAPI()

class Admin(BaseModel):
    cpf: str
    email: str
    nome: str
    senha: str

class UpdateAdmin(BaseModel):
    cpf: Optional[str]
    email: Optional[str]
    nome: Optional[str]
    senha: Optional[str]

class Cliente(BaseModel):
    cpf: str
    email: str
    nome: str
    endereco: str
    data_nascimento: str

class UpdateCliente(BaseModel):
    cpf: Optional[str]
    email: Optional[str]
    nome: Optional[str]
    endereco: Optional[str]
    data_nascimento: Optional[str]

@app.post("/put-admin/")
async def put_admin(admin: Admin):
    result = cadastra_admin(
        admin.cpf,
        admin.email, 
        admin.nome, 
        admin.senha
    )
    return result

def altera_admin(cpf: str, novo_cpf: str, email: str, nome: str, senha: str):
    cpf_valido = valida_cpf(cpf)

    cur.execute("SELECT * FROM ADMIN WHERE CPF_ADMIN = :cpf", {"cpf": cpf_valido})
    admin_cadastrado = cur.fetchone()

    if admin_cadastrado is None:
        raise HTTPException(status_code=404, detail="Admin não cadastrado")
    
    try:
        if novo_cpf != None:
            new_cpf = valida_cpf(novo_cpf)
            if not new_cpf:
                raise HTTPException(status_code=422, detail="CPF inválido")
            cur.execute("UPDATE ADMIN SET CPF_ADMIN = :new_cpf WHERE CPF_ADMIN = :cpf", {"new_cpf": new_cpf, "cpf": cpf_valido})
        if email != None:
            if not valida_email(email):
                raise HTTPException(status_code=422, detail="E-mail inválido")
            cur.execute("UPDATE ADMIN SET EMAIL_ADMIN = :email WHERE CPF_ADMIN = :cpf", {"email": email, "cpf": cpf_valido})
        if nome != None:
            if not valida_nome(nome):
                raise HTTPException(status_code=422, detail="Nome inválido")
            cur.execute("UPDATE ADMIN SET NOME_ADMIN = :nome WHERE CPF_ADMIN = :cpf", {"nome": nome, "cpf": cpf_valido})
        if senha != None:
            if not valida_senha(senha):
                raise HTTPException(status_code=422, detail="Senha inválida")
            cur.execute("UPDATE ADMIN SET SENHA = :senha WHERE CPF_ADMIN = :cpf", {"senha": senha, "cpf": cpf_valido})
        con.commit()
    except Exception as e:
        raise HTTPException("Error", detail=e)
    

@app.put("/altera-admin/{cpf_admin}")
async def put_cliente(cpf: str, admin: UpdateAdmin):
    reponse = altera_admin(
        cpf,
        admin.cpf, 
        admin.email,
        admin.nome, 
        admin.senha
        )
    return reponse
        
@app.delete("/deleta-admin/{cpf_admin}")
async def delet_admin(cpf: str):
    result = exclui_admin(cpf)
    return result


@app.get("busca_cliente/{cpf_cliente}")
async def get_cliente(cpf: str):
    result = busca_cliente(cpf)
    return result


@app.post("cadastra-cliente")
async def post_cliente(cliente: Cliente):
    result = cadastra_cliente(
        cliente.cpf,
        cliente.email,
        cliente.nome,
        cliente.endereco,
        cliente.data_nascimento
    )
    return result


def altera_cliente(cpf: str, novo_cpf: str, email: str, nome: str, endereco: str, data_nascimento: str):
    cpf_valido = valida_cpf(cpf)
    
    cur.execute("SELECT * FROM CLIENTE WHERE CPF_CLIENTE = :cpf", {"cpf": cpf_valido})
    cliente_cadastrado = cur.fetchone()

    if cliente_cadastrado is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    try:
        if novo_cpf != None:
            new_cpf = cpf_valido(novo_cpf)
            if not new_cpf:
                raise HTTPException(status_code=422, detail="CPF inválido")
            cur.execute("UPDATE CLIENTE SET CPF_CLIENTE = :novo_cpf WHERE CPF_CLIENTE = :cpf", {"novo_cpf": new_cpf, "cpf": cpf_valido})
        if email != None:
            if not valida_email(email):
                raise HTTPException(status_code=422, detail="E-mail inválido")
            cur.execute("UPDATE CLIENTE SET EMAIL_CLIENTE = :email WHERE CPF_CLIENTE = :cpf", {"cpf": cpf_valido, "email": email})
        if nome != None:
            if not valida_nome(nome):
                raise HTTPException(status_code=422, detail="Nome inválido")
            cur.execute("UPDATE CLIENTE SET NOME_CLIENTE = :nome WHERE CPF_CLIENTE = :cpf", {"nome": nome, "cpf": cpf})
        if endereco != None:
            if not valida_endereco(endereco):
                raise HTTPException(status_code=422, detail="Endereço inválido")
            cur.execute("UPDATE CLIENTE SET ENDERECO_CLIENTE = :endereco WHERE CPF_CLIENTE = :cpf", {"endereco": endereco, "cpf": cpf})
        if data_nascimento != None:
            if not valida_data_nascimento(data_nascimento):
                raise HTTPException(status_code=422, detail="Data de nascimento inválida")
            cur.execute("UPDATE CLIENTE SET DATA_NASCIMENTO_CLIENTE = :data WHERE CPF_CLIENTE = :cpf", {"data": data_nascimento, "cpf": cpf})
        con.commit()
        return {"message": "Cliente alterado com sucesso!"}
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Integrity Error", detail=e)
    except Exception as e:
        raise HTTPException(status_code="Error", detail=e)
    

@app.put("/altera-cliente/{cpf_cliente}")
async def put_cliente(cpf: str, cliente: UpdateCliente):
    result = altera_cliente(
        cpf,
        cliente.cpf,
        cliente.email,
        cliente.nome,
        cliente.endereco,
        cliente.data_nascimento
        )
    return result

@app.delete("exclui-cliente/{cpf_cliente}")
async def delete_cliente(cpf: str):
    result = exclui_cliente(cpf)
    return result