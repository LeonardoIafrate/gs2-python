from validacao import valida_nome, valida_cpf
from bd.connection import *
from fastapi import HTTPException
import oracledb


def busca_eletros(cpf: str):
    try:
        cur.execute("SELECT ELETRODOMESTICO, MODELO FROM ELETRO WHERE CPF_CLIENTE = :cpf", {"cpf": cpf})
        eletros = cur.fetchall()

        if eletros is None:
            raise HTTPException(status_code=404, detail="Eletrodoméstico não encontrado")

        eletro_list = []
        for eletro in eletros:
            eletro_dict = {
                "Eletrodoméstico": eletro[0],
                "Modelo": eletro[1]
            }
            eletro_list.append(eletro_dict)
        return eletro_list
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    

def busca_eletro(modelo: str):
    try:
        cur.execute("SELECT ELETRODOMESTICO, MARCA, MODELO, EFICIENCIA_ENERGETICA, CONSUMO_ENER_MED FROM ELETRO WHERE MODELO = :modelo", {"modelo", modelo})
        eletro = cur.fetchone()

        if eletro is None:
            raise HTTPException(status_code=404, detail="Eletrodoméstico não encontrado")
        
        eletro_dict = {
            "Eletrodomestico": eletro[0], 
            "Marca": eletro[1], 
            "Modelo": eletro[2],
            "Eficiência Energética": eletro[3],
            "Consumo energético medido": eletro[4]
            }

        return eletro_dict

    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")
    

def calculo_eletri_diario(modelo: str, horas: float):
    cur.execute("SELECT CONSUMO_ENER_MED FROM ELETRO WHERE MODELO = :modelo", {"modelo": modelo})
    consumo = cur.fetchone()
    
    if consumo is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não encontrado")
    
    try:
        consumo_diario = consumo[0] * horas
        valor_consumo = consumo_diario * 0.65
        return {"O consumo diário do eletrodoméstico é de": f"{consumo_diario}kWh, equivalente a R${valor_consumo}"}
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


def calculo_eletri_mensal(modelo: str, horas: float, dias: int):
    cur.execute("SELECT CONSUMO_ENER_MED FROM ELETRO WHERE MODELO = :modelo", {"modelo": modelo})
    consumo = cur.fetchone()

    if consumo is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não econtrado")
    
    try:
        consumo_mensal = consumo[0] * horas * dias
        valor_consumo_mensal = consumo_mensal * 0.65
        return {"O consumo mensal do eletrodoméstico é de": f"{consumo_mensal}kWh, equivalente a R${valor_consumo_mensal}"}
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Erro de integridade: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


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