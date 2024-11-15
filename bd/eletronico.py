from validacao import valida_nome, valida_cpf
from bd.connection import *
from fastapi import HTTPException
import oracledb


def busca_eletro(cpf: str):
    try:
        cur.execute("SELECT ELETRODOMESTICO, MODELO FROM ELETRO WHERE CPF_CLIENTE = :cpf", {"cpf": cpf})
        eletros = cur.fetchall()
        for eletro in eletros:
            eletro_dict = {
                "Eletrodoméstico": eletro[0],
                "Modelo": eletro[1]
            }
        return eletro_dict
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    
def cadastra_eletronico(eletro: str, marca: str, modelo: str, eficiencia: str, consumo_ener_med: int, cpf_cliente: str):
    try:
        if not valida_nome(eletro):
            raise HTTPException(status_code=422, detail="Eletronico inválido")
        if not valida_nome(marca):
            raise HTTPException(status_code=422, detail="Marca inválida")
        if not valida_cpf(cpf_cliente):
            raise HTTPException(status_code=422, detail="CPF inválido")
        cur.execute(
        """INSERT INTO ELETRO (ELETRODOMESTICO, MARCA, MODELO, EFICIENCIA_ENERGETICA, CONSUMO_ENER_MED, CPF_CLIENTE) 
        VALUES (:eletro, :marca, :modelo, :eficiencia, :consumo_ener_med, :cpf_cliente)
        """, {"eletro": eletro, "marca": marca, "modelo": modelo, "eficiencia": eficiencia, "consumo_ener_med": consumo_ener_med, "cpf_cliente": cpf_cliente}
        )
        con.commit()
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    
def exclui_eletronico(eletro: str, cpf_cliente: str):
    cur.execute("SELECT * FROM ELETRO WHERE CPF_CLIENTE = :cpf_cliente AND ELETRODOMESTICO = :eletro", {"cpf_cliente": cpf_cliente, "eletro": eletro})
    eletrodomestico = cur.fetchone()
    if eletrodomestico is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não encontrado")
    try:
        cur.execute("DELETE FROM ELETRO WHERE CPF_CLIENTE = :cpf_cliente AND ELETRODOMESTICO = :eletro", {"cpf_cliente": cpf_cliente, "eletro": eletro})
        con.commit()
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)