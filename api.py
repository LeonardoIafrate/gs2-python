from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from bd.admin import cadastra_admin, exclui_admin
from bd.cliente import busca_cliente, cadastra_cliente, exclui_cliente
from bd.eletronico import busca_eletros, cadastra_eletronico, exclui_eletronico, consumo_geral_diario, calculo_eletri_u_mensal,calculo_eletri_h_mensal, calculo_eletri_u_diario, calculo_eletri_h_diario
from bd.connection import *
from validacao import valida_cpf, valida_data_nascimento, valida_email, valida_endereco, valida_nome, valida_senha, valida_eficiencia

app = FastAPI()

class Admin(BaseModel):
    cpf: str
    email: str
    nome: str
    senha: str

class UpdateAdmin(BaseModel):
    cpf: Optional[str] = None
    email: Optional[str] = None
    nome: Optional[str] = None
    senha: Optional[str] = None

class Cliente(BaseModel):
    cpf: str
    email: str
    nome: str
    endereco: str
    data_nascimento: str

class UpdateCliente(BaseModel):
    cpf: Optional[str] = None
    email: Optional[str] = None
    nome: Optional[str] = None
    endereco: Optional[str] = None
    data_nascimento: Optional[str] = None

class Eletro(BaseModel):
    Eletrodomestico: str
    Marca: str
    Modelo: str
    Eficiencia_energetica: str
    Consumo_ener_med: float
    CPF_cliente: str

class UpdateEletro(BaseModel):
    Eletrodomestico: Optional[str] = None
    Marca: Optional[str] = None
    Modelo: Optional[str] = None
    Eficiencia_energetica: Optional[str] = None
    Consumo_ener_med: Optional[float] = None
    CPF_cliente: Optional[str] = None

@app.post("/post-admin/")
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

        return{"Message": "Admin alterado com sucessos"}
    except Exception as e:
        raise HTTPException("Error", detail=e)
    

@app.put("/altera-admin/{cpf_admin}")
async def put_admin(cpf: str, admin: UpdateAdmin):
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


@app.get("/busca_cliente/{cpf_cliente}")
async def get_cliente(cpf: str):
    result = busca_cliente(cpf)
    return result


@app.post("/post-cliente/")
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
    
    cur.execute("SELECT * FROM CLI WHERE CPF_CLIENTE = :cpf", {"cpf": cpf_valido})
    cliente_cadastrado = cur.fetchone()

    if cliente_cadastrado is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    try:
        if novo_cpf != None:
            new_cpf = cpf_valido(novo_cpf)
            if not new_cpf:
                raise HTTPException(status_code=422, detail="CPF inválido")
            cur.execute("UPDATE CLI SET CPF_CLIENTE = :novo_cpf WHERE CPF_CLIENTE = :cpf", {"novo_cpf": new_cpf, "cpf": cpf_valido})
        if email != None:
            if not valida_email(email):
                raise HTTPException(status_code=422, detail="E-mail inválido")
            cur.execute("UPDATE CLI SET EMAIL_CLIENTE = :email WHERE CPF_CLIENTE = :cpf", {"cpf": cpf_valido, "email": email})
        if nome != None:
            if not valida_nome(nome):
                raise HTTPException(status_code=422, detail="Nome inválido")
            cur.execute("UPDATE CLI SET NOME_CLIENTE = :nome WHERE CPF_CLIENTE = :cpf", {"nome": nome, "cpf": cpf})
        if endereco != None:
            if not valida_endereco(endereco):
                raise HTTPException(status_code=422, detail="Endereço inválido")
            cur.execute("UPDATE CLI SET ENDERECO_CLIENTE = :endereco WHERE CPF_CLIENTE = :cpf", {"endereco": endereco, "cpf": cpf})
        if data_nascimento != None:
            if not valida_data_nascimento(data_nascimento):
                raise HTTPException(status_code=422, detail="Data de nascimento inválida")
            cur.execute("UPDATE CLI SET DATA_NASCIMENTO_CLIENTE = :data WHERE CPF_CLIENTE = :cpf", {"data": data_nascimento, "cpf": cpf})
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


@app.delete("/exclui-cliente/{cpf_cliente}")
async def delete_cliente(cpf: str):
    result = exclui_cliente(cpf)
    return result


@app.get("/busca-eletros/{cpf_cliente}")
async def get_eletros(cpf: str):
    result = busca_eletros(cpf)
    return result


@app.get("/consumo-eletrodomestico-diario-horas/{modelo}")
async def get_consumo(modelo: str, horas: float):
    result = calculo_eletri_h_diario(modelo, horas)
    return result


@app.get("/consumo-eletrodomestico-diario-uso/{modelo}")
async def get_consumo(modelo: str, usos: int):
    result = calculo_eletri_u_diario(modelo, usos)
    return result


@app.get("/consumo-eletrodomestico-mensal-horas/{modelo}")
async def get_consumo(modelo: str, horas: float, dias: int):
    result = calculo_eletri_h_mensal(modelo, horas, dias)
    return result


@app.get("/consumo-eletrodomestico-mensal-usos/{modelo}")
async def get_consumo(modelo: str, usos: int, dias: int):
    result = calculo_eletri_u_mensal(modelo, usos, dias)
    return result


@app.post("/cadastra-eletro")
async def post_eletro(eletro: Eletro):
    result = cadastra_eletronico(
        eletro.Eletrodomestico,             
        eletro.Marca,
        eletro.Modelo,
        eletro.Eficiencia_energetica,
        eletro.Consumo_ener_med,
        eletro.CPF_cliente
    )
    return result


def altera_eletronico(cpf: str, modelo: str, eletrodomestico: str, marca: str, new_modelo: str, eficiencia_energetica: str, consumo_ener_med: float, new_cpf_cliente: str): 
    cpf_valido = valida_cpf(cpf)

    cur.execute("SELECT * FROM ELETRO WHERE CPF_CLIENTE = :cpf AND MODELO= :modelo", {"cpf": cpf, "modelo": modelo})
    eletro_cadastrado = cur.fetchone()
    if eletro_cadastrado is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não encontrado")
    try:
        if eletrodomestico != None:
            if not valida_nome(eletrodomestico):
                raise HTTPException(status_code=422, detail="Eletrodoméstico inválido")
            cur.execute("UPDATE ELETRO SET ELETRODOMESTICO = :eletrodomestico WHERE CPF_CLIENTE = :cpf_cliente AND MODELO = :modelo", {"eletro": eletrodomestico,"cpf_cliente": cpf_valido, "modelo": modelo})
        if marca != None:
            if not valida_nome(marca):
                raise HTTPException(status_code=422, detail="Marca inválida")
            cur.execute("UPDATE ELETRO SET MARCA = :marca WHERE CPF_CLIENTE = :cpf_cliente AND MODELO = :modelo", {"marca": marca, "cpf_cliente": cpf_valido, "modelo": modelo})
        if new_modelo != None:
            cur.execute("UPDATE ELETRO SET MODELO = :new_modelo WHERE CPF_CLIENTE = :cpf_cliente AND MODELO = :modelo", {"new_modelo": new_modelo, "cpf_cliente": cpf_valido, "modelo": modelo})
        if eficiencia_energetica != None:
            if not valida_eficiencia(eficiencia_energetica):
                raise HTTPException(status_code=422, detail="Eficiência energética inválida")
            cur.execute("UPDATE ELETRO SET EFICIENCIA_ENERGETICA = :eficiencia_energetica WHERE CPF_CLIENTE = :cpf_cliente AND MODELO = :modelo", {"eficiencia_energetica": eficiencia_energetica, "cpf_cliente": cpf_valido, "modelo": modelo})
        if consumo_ener_med != None:
            cur.execute("UPDATE ELETRO SET CONSUMO_ENER_MED = :consumo_ener_med WHERE CPF_CLIENTE = :cpf_cliente AND MODELO = :modelo", {"consumo_ener_med": consumo_ener_med, "cpf_cliente": cpf_valido, "modelo": modelo})
        if new_cpf_cliente != None:
            new_cpf_valido = valida_cpf(new_cpf_cliente)
            if not new_cpf_valido:
                raise HTTPException(status_code=422, detail="CPF inválido")
            cur.execute("UPDATE ELETRO SET CPF_CLIENTE = :new_cpf_valido WHERE CPF_CLIENTE = :cpf_cliente AND MODELO = :modelo", {"new_cpf_valido": new_cpf_valido, "cpf_cliente": cpf_valido, "modelo": modelo})
        con.commit()

        return{"Message": "Eletrodomestico alterado com sucesso"}
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    except Exception as e:
        raise HTTPException(status_code="Error", detail=e)
    

@app.put("/altera-eletrodomestico/{cpf_cliente}")
async def put_eletrodomestico(cpf_cliente: str, modelo: str, eletro: UpdateEletro):
    result = altera_eletronico(
        cpf_cliente,
        modelo,
        eletro.Eletrodomestico,
        eletro.Marca,
        eletro.Modelo,
        eletro.Eficiencia_energetica,
        eletro.Consumo_ener_med,
        eletro.CPF_cliente
    )
    return result


@app.delete("/exclui-eletrodomestico/{cpf_cliente}")
async def delete_eletrodomestico(eletro: str, cpf_cliente: str):
    result = exclui_eletronico(eletro, cpf_cliente)
    return result