import json
from validacao import valida_nome, valida_cpf, valida_eficiencia
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

        with open("busca_eletros.json", "w") as arquivo_json:
            json.dump(eletro_list, arquivo_json, indent=4, ensure_ascii=False)

        return eletro_list
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code=500, detail=f"Erro de integridade: {str(e)}")
    

def busca_eletro(modelo: str, cpf_cliente: str):
    try:
        cpf_valido = valida_cpf(cpf_cliente)
        cur.execute("SELECT ELETRODOMESTICO, MARCA, MODELO, EFICIENCIA_ENERGETICA, POTENCIA FROM ELETRO WHERE MODELO = :modelo AND CPF_CLIENTE = :cpf_cliente", {"modelo": modelo, "cpf_cliente": cpf_valido})
        eletro = cur.fetchone()

        if eletro is None:
            raise HTTPException(status_code=404, detail="Eletrodoméstico não encontrado")
        
        eletro_dict = {
            "Eletrodomestico": eletro[0], 
            "Marca": eletro[1], 
            "Modelo": eletro[2],
            "Eficiência Energética": eletro[3],
            "Consumo em Wats do aparelho": eletro[4]
            }
        
        with open("busca_eletro.json", "w") as arquivo_json:
            json.dump(eletro_dict, arquivo_json, indent=4, ensure_ascii=False)

        return eletro_dict

    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")
    

def calcula_w(kwh: float, horas: float):
    calculo = kwh * 1000 / (30 * horas)
    return {"O aparelho tem a potência de": f"{calculo:.2f}W"}


def calculo_eletri_diario(modelo: str, horas: int, minutos: int):
    cur.execute("SELECT POTENCIA FROM ELETRO WHERE MODELO = :modelo", {"modelo": modelo})
    potencia = cur.fetchone()
    
    if potencia is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não encontrado")
    
    try:
        minutos = int(minutos)
        horas = int(horas)

        if minutos > 59:
            raise HTTPException(status_code=422, detail="Não é possível colocar minutos acima de 59")
        
        percentual_minutos = minutos / 60
        horas_totais = horas + percentual_minutos
        consumo_diario = (potencia[0] * horas_totais) / 1000
        valor_consumo = consumo_diario * 0.65

        resultado = {
            "modelo": modelo,
            "horas": horas,
            "minutos": minutos,
            "consumo_diario_kWh": round(consumo_diario, 2),
            "valor_consumo_reais": round(valor_consumo, 2),
        }

        with open("calculos_diarios.json", "a") as arquivo_json:
            arquivo_json.write(json.dumps(resultado, ensure_ascii=False) + "\n")

        return {"O consumo diário do eletrodoméstico é de": f"{consumo_diario:.2f}kWh, equivalente a R${valor_consumo:.2f}"}
    
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code=500, detail=f"Erro de integridade: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


def calculo_eletri_mensal(modelo: str, horas: int, minutos: int, dias: int):
    cur.execute("SELECT POTENCIA FROM ELETRO WHERE MODELO = :modelo", {"modelo": modelo})
    potencia = cur.fetchone()

    if potencia is None:
        raise HTTPException(status_code=404, detail="Eletrodoméstico não econtrado")
    
    try:
        if minutos > 59:
            raise HTTPException(status_code=422, detail="Não é possível colocar minutos acima de 59")
        percentual_minutos = minutos / 60
        horas_totais = horas + percentual_minutos
        consumo_mensal = potencia[0] * horas_totais * dias / 1000
        valor_consumo_mensal = consumo_mensal * 0.65

        resultado = {
            "modelo": modelo,
            "horas": horas,
            "minutos": minutos,
            "dias": dias,
            "consumo_mensal_kWh": round(consumo_mensal, 2),
            "valor_consumo_mensal_reais": round(valor_consumo_mensal, 2)
        }

        with open("calculos_mensais.json", "w") as arquivo_json:
            json.dump(resultado, arquivo_json, indent=4)

        return {"O consumo mensal do eletrodoméstico é de": f"{consumo_mensal:.2f}kWh, equivalente a R${valor_consumo_mensal:.2f}"}
    except oracledb.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Erro de integridade: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


def cadastra_eletronico(eletro: str, marca: str, modelo: str, eficiencia: str, potencia: float, cpf_cliente: str):
    try:
        if not valida_nome(eletro):
            raise HTTPException(status_code=422, detail="Eletronico inválido")
        if not valida_nome(marca):
            raise HTTPException(status_code=422, detail="Marca inválida")
        if not valida_cpf(cpf_cliente):
            raise HTTPException(status_code=422, detail="CPF inválido")
        if not valida_eficiencia(eficiencia):
            raise HTTPException(status_code=422, detail="Eficiência inválida")
        cur.execute(
        """INSERT INTO ELETRO (ELETRODOMESTICO, MARCA, MODELO, EFICIENCIA_ENERGETICA, POTENCIA, CPF_CLIENTE) 
        VALUES (:eletro, :marca, :modelo, :eficiencia, :potencia, :cpf_cliente)
        """, {"eletro": eletro, "marca": marca, "modelo": modelo, "eficiencia": eficiencia, "potencia": potencia, "cpf_cliente": cpf_cliente}
        )
        con.commit()

        return {"Message": "Eletrônico cadastrado com sucesso"}

    except oracledb.IntegrityError as e:
        raise HTTPException(status_code=500, detail=f"Erro de integridade: {str(e)}")


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