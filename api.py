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
