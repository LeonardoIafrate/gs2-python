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
    

def calculo_eletri_h_diario(modelo: str, horas: float):
    cur.execute("SELECT CONSUMO_ENER_MED FROM ELETRO WHERE MODELO = :modelo", {"modelo": modelo})
    consumo = cur.fetchone()
    
    if consumo is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não encontrado")
    
    try:
        consumo_diario = consumo[0] / 30 / 24 * horas
        valor_consumo = consumo_diario * 0.65
        return {"O consumo diário do eletrodoméstico é de": f"{consumo_diario:.2f}kWh, equivalente a R${valor_consumo:.2f}"}
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


def calculo_eletri_u_diario(modelo: str, uso: int):
    cur.execute("SELECT CONSUMO_ENER_MED FROM ELETRO WHERE MODELO = :modelo", {"modelo": modelo})
    consumo = cur.fetchone()
    
    if consumo is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não encontrado")
    
    try:
        consumo_diario = consumo[0] / 30 * uso
        valor_consumo = consumo_diario * 0.65
        return {"O consumo diário do eletrodoméstico é de": f"{consumo_diario:.2f}kWh, equivalente a R${valor_consumo:.2f}"}
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

def calculo_eletri_h_mensal(modelo: str, horas: float, dias: int):
    cur.execute("SELECT CONSUMO_ENER_MED FROM ELETRO WHERE MODELO = :modelo", {"modelo": modelo})
    consumo = cur.fetchone()

    if consumo is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não econtrado")
    
    try:
        consumo_mensal = consumo[0] / 30 / 24 * horas * dias
        valor_consumo_mensal = consumo_mensal * 0.65
        return {"O consumo mensal do eletrodoméstico é de": f"{consumo_mensal:.2f}kWh, equivalente a R${valor_consumo_mensal:.2f}"}
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Erro de integridade: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


def calculo_eletri_u_mensal(modelo: str, uso: int, dias: int):
    cur.execute("SELECT CONSUMO_ENER_MED FROM ELETRO WHERE MODELO = :modelo", {"modelo": modelo})
    consumo = cur.fetchone()

    if consumo is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não econtrado")
    
    try:
        consumo_mensal = consumo[0] / 30 * uso * dias
        valor_consumo_mensal = consumo_mensal * 0.65
        return {"O consumo mensal do eletrodoméstico é de": f"{consumo_mensal:.2f}kWh, equivalente a R${valor_consumo_mensal:.2f}"}
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Erro de integridade: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


def consumo_geral_diario(cpf: str, horas: float):
    try:
        cpf_valido = valida_cpf(cpf)

        eletros = busca_eletros(cpf_valido)

        consumo_total = 0
        valor_total = 0
        consumo_detalho = []

        for eletro in eletros:
            modelo = eletro['Modelo']

            resultado_diario = calculo_eletri_diario(modelo, horas)

            consumo_diario = resultado_diario['consumo_diario']
            valor_consumo = resultado_diario['valor_consumo']

            consumo_total += consumo_diario
            valor_total += valor_consumo

            consumo_detalho.append({
                "Eletrodoméstico": eletro['Eletrodomestico'],
                "Modelo": modelo,
                "Consumo Diário do eletrodoméstico": f"{consumo_diario:.2f}kWh",
                "Valor do consumo do eletrodoméstico": f"R${valor_consumo:.2f}"
            })

        return{
            "Consumo total do dia": f"{consumo_total:.2f}kWh",
            "Valor total do consumo do dia": f"R${valor_total:.2f}",
            "Consumo detalhado do dia": consumo_detalho
        }
    
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code="Erro de integridade", detail=e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


def cadastra_eletronico(eletro: str, marca: str, modelo: str, eficiencia: str, consumo_ener_med: float, cpf_cliente: str):
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

        return {"Eletrônico cadastrado com sucesso"}

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