import cx_Oracle
import pandas as pd
import json


class Conn:
    def __init__(self):
        self.cursor = None
        self.connection = None
        self.connect()

    def connect(self):
        with open("db_config.json", "r") as file:
            config = json.load(file)

        dsn = cx_Oracle.makedsn(
            config["dsn"].split(":")[0],
            int(config["dsn"].split(":")[1].split("/")[0]),
            service_name=config["dsn"].split("/")[1]
        )
        self.connection = cx_Oracle.connect(
            user=config["user"],
            password=config["password"],
            dsn=dsn,
            encoding="UTF-8"
        )
        self.cursor = self.connection.cursor()

    def conectar(self):
        if not self.connection or not self.cursor:
            self.connect()
        return self.cursor


class BD:
    def __init__(self):
        self.conexao = Conn()

    def car_abertos(self):
        cur = self.conexao.conectar()
        cur.execute(
            r"SELECT CAR.CARREGAMENTO, CAR.DESCRICAO,  "
            r"    COUNT(CASE WHEN TOR.TIPO_ORDEM IN ('OFA', 'OFM') THEN 1 END) AS EM_ABERTO, "
            r"    COUNT(CASE WHEN TOR.TIPO_ORDEM = 'OFE' THEN 1 END) AS ENCERRADAS, "
            r"CASE "
            r"    WHEN MAQ.DESCRICAO LIKE '%SERRA-FITA%'      THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PLASMA%'          THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%LASER%'           THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%GUILHOTINA%'      THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PUNCIONADEIRA%'   THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PRENSA%'          THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%DOBRADEIRA%'      THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%CALANDRA%'        THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%LIXADEIRA%'       THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%CONFORMADORA%'    THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%REBORDEADOR%'     THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%METALEIRA%'       THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%FICEP%'           THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%TORNO%'           THEN 'USINAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%FRESA%'           THEN 'USINAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%FURADEIRA%'       THEN 'USINAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%MAQUINA-TUBO%'    THEN 'USINAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%MIG%'             THEN 'SOLDAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PARAFUSADEIRA%'   THEN 'PRE-MONTAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PISTOLA%'         THEN 'PINTURA' "
            r"    WHEN MAQ.DESCRICAO LIKE '%TANQUE%'          THEN 'PREPARACAO-SUPERFICIE' "
            r"    WHEN MAQ.DESCRICAO LIKE '%JATO%'            THEN 'PREPARACAO-SUPERFICIE' "
            r"    WHEN MAQ.DESCRICAO LIKE '%GRAVADORA%'       THEN 'ALMOX' "
            r"    ELSE 'NULL' "
            r"END AS LOCAL_PROD "
            r"FROM FOCCO3I.TORDENS TOR "
            r"INNER JOIN FOCCO3I.TITENS_PLANEJAMENTO TPL          ON TPL.ID = TOR.ITPL_ID "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ROT                  ON ROT.ORDEM_ID = TOR.ID "
            r"INNER JOIN FOCCO3I.TORD_ROT_FAB_MAQ FAB             ON ROT.ID = FAB.TORDEN_ROT_ID "
            r"INNER JOIN FOCCO3I.TMAQUINAS MAQ                    ON FAB.MAQUINA_ID = MAQ.ID "
            r"INNER JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VIN       ON VIN.ORDEM_ID = TOR.ID "
            r"INNER JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON CAR.ID = VIN.CARERGAM_ID "
            r"WHERE CAR.CARREGAMENTO > 339200 "
            r"AND CAR.SITUACAO = 'A' "
            r"GROUP BY CAR.CARREGAMENTO, CAR.DESCRICAO, "
            r"CASE "
            r"    WHEN MAQ.DESCRICAO LIKE '%SERRA-FITA%'      THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PLASMA%'          THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%LASER%'           THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%GUILHOTINA%'      THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PUNCIONADEIRA%'   THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PRENSA%'          THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%DOBRADEIRA%'      THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%CALANDRA%'        THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%LIXADEIRA%'       THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%CONFORMADORA%'    THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%REBORDEADOR%'     THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%METALEIRA%'       THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%FICEP%'           THEN 'PREPARACAO' "
            r"    WHEN MAQ.DESCRICAO LIKE '%TORNO%'           THEN 'USINAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%FRESA%'           THEN 'USINAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%FURADEIRA%'       THEN 'USINAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%MAQUINA-TUBO%'    THEN 'USINAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%MIG%'             THEN 'SOLDAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PARAFUSADEIRA%'   THEN 'PRE-MONTAGEM' "
            r"    WHEN MAQ.DESCRICAO LIKE '%PISTOLA%'         THEN 'PINTURA' "
            r"    WHEN MAQ.DESCRICAO LIKE '%TANQUE%'          THEN 'PREPARACAO-SUPERFICIE' "
            r"    WHEN MAQ.DESCRICAO LIKE '%JATO%'            THEN 'PREPARACAO-SUPERFICIE' "
            r"    WHEN MAQ.DESCRICAO LIKE '%GRAVADORA%'       THEN 'ALMOX' "
            r"    ELSE 'NULL' "
            r"END "
            r"ORDER BY TO_NUMBER(CAR.CARREGAMENTO) DESC "
        )
        car_abertos = cur.fetchall()
        car_abertos = pd.DataFrame(car_abertos, columns=[
            'CARREGAMENTO', 'DESCRICAO', 'EM_ABERTO', 'ENCERRADAS', 'LOCAL_PROD'
        ])
        car_abertos['CARREGAMENTO'] = car_abertos['CARREGAMENTO'].astype(str)

        #pivotando df
        car_abertos["PROPORCAO"] = car_abertos["EM_ABERTO"].astype(str) + " / " + (car_abertos["EM_ABERTO"] + car_abertos["ENCERRADAS"]).astype(str)

        # Pivotando os dados para transformar LOCAL_PROD em colunas
        car_abertos = car_abertos.pivot_table(
            index=["CARREGAMENTO", "DESCRICAO"],  # Índices de agrupamento
            columns="LOCAL_PROD",  # Valores que virarão colunas
            values="PROPORCAO",  # Coluna com as proporções
            aggfunc="first",  # Como cada grupo tem um único valor, usamos "first"
            fill_value="0 / 0",  # Preenche valores ausentes
        )

        car_abertos = car_abertos.reset_index()
        car_abertos = car_abertos.sort_values(by='CARREGAMENTO', ascending=False)
        car_abertos = car_abertos.replace('0 / 0', '-')
        car_abertos = car_abertos.drop(columns=["NULL"])
        car_abertos = car_abertos[[
            'CARREGAMENTO', 'DESCRICAO', 'PREPARACAO', 'USINAGEM', 'SOLDAGEM', 'PREPARACAO-SUPERFICIE', 'PINTURA',
            'PRE-MONTAGEM', 'ALMOX'
        ]]
        #print(car_abertos.to_string())
        #quit()
        return car_abertos

    def car_data(self, carregamento):
        cur = self.conexao.conectar()
        cur.execute(
            r"SELECT  "
            r"    CAR.DESCRICAO, "
            r"    MAQ.DESCRICAO, "
            r"    TOR.NUM_ORDEM, "
            r"    TOR.QTDE, "
            r"    TOR.TIPO_ORDEM, "
            r"    MASC.ID, "
            r"    MASC.MASCARA "
            r"FROM FOCCO3I.TORDENS TOR "
            r"INNER JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VIN       ON VIN.ORDEM_ID = TOR.ID "
            r"INNER JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON CAR.ID = VIN.CARERGAM_ID "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ROT                  ON TOR.ID = ROT.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TORD_ROT_FAB_MAQ FAB             ON ROT.ID = FAB.TORDEN_ROT_ID "
            r"INNER JOIN FOCCO3I.TMAQUINAS MAQ                    ON FAB.MAQUINA_ID = MAQ.ID "
            r"LEFT JOIN FOCCO3I.TMASC_ITEM MASC                   ON MASC.ID = TOR.TMASC_ITEM_ID "
            r"WHERE CAR.CARREGAMENTO IN (" + carregamento + ") "
        )
        car_data = cur.fetchall()
        car_data = pd.DataFrame(car_data, columns=['CAR_DESC', 'MAQUINA', 'NUM_ORDEM', 'QTDE', 'TIPO_ORDEM', 'MASC', 'MASC_DESC'])
        car_data.dropna(subset=['QTDE', 'MASC'], inplace=True)
        car_data[['QTDE', 'MASC']] = car_data[['QTDE', 'MASC']].astype('int64')
        return car_data


if __name__ == "__main__":
    db = BD()
    print(db.car_abertos().to_string())
