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
            r"SELECT  "
            r"    CAR.CARREGAMENTO, "
            r"    CAR.DESCRICAO,  "
            r"    COUNT(CASE WHEN NOT EXISTS ( "
            r"                            SELECT MOV.ID  "
            r"                            FROM FOCCO3I.TORDENS_MOVTO MOV  "
            r"                            WHERE MOV.TORDEN_ROT_ID = ROT.ID "
            r"                        ) THEN 1 END) AS EM_ABERTO, "
            r"    COUNT(CASE WHEN TOR.TIPO_ORDEM = 'OFE' THEN 1 END) AS ENCERRADAS, "
            r"    CASE "
            r"        WHEN MAQ.DESCRICAO LIKE '%SERRA-FITA%'      THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PLASMA%'          THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%LASER%'           THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%GUILHOTINA%'      THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PUNCIONADEIRA%'   THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PRENSA%'          THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%DOBRADEIRA%'      THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%CALANDRA%'        THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%LIXADEIRA%'       THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%CONFORMADORA%'    THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%REBORDEADOR%'     THEN 'SOLDAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%METALEIRA%'       THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%FICEP%'           THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%TORNO%'           THEN 'USINAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%FRESA%'           THEN 'USINAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%FURADEIRA%'       THEN 'USINAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%MAQUINA-TUBO%'    THEN 'USINAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%MIG%'             THEN 'SOLDAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PARAFUSADEIRA%'   THEN 'PRE-MONTAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PISTOLA%'         THEN 'PINTURA' "
            r"        WHEN MAQ.DESCRICAO LIKE '%TANQUE%'          THEN 'PREPARACAO-SUPERFICIE' "
            r"        WHEN MAQ.DESCRICAO LIKE '%JATO%'            THEN 'PREPARACAO-SUPERFICIE' "
            r"        WHEN MAQ.DESCRICAO LIKE '%GRAVADORA%'       THEN 'ALMOX' "
            r"        ELSE 'NULL' "
            r"    END AS LOCAL_PROD "
            r"FROM FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR "
            r"LEFT JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VIN       ON CAR.ID = VIN.CARERGAM_ID "
            r"LEFT JOIN FOCCO3I.TORDENS TOR                      ON VIN.ORDEM_ID = TOR.ID "
            r"LEFT JOIN FOCCO3I.TITENS_PLANEJAMENTO TPL          ON TPL.ID = TOR.ITPL_ID "
            r"LEFT JOIN FOCCO3I.TORDENS_ROT ROT                  ON ROT.ORDEM_ID = TOR.ID "
            r"LEFT JOIN FOCCO3I.TORD_ROT_FAB_MAQ FAB             ON ROT.ID = FAB.TORDEN_ROT_ID "
            r"LEFT JOIN FOCCO3I.TMAQUINAS MAQ                    ON FAB.MAQUINA_ID = MAQ.ID "
            r"WHERE CAR.CARREGAMENTO > 339200 "
            r"  AND CAR.SITUACAO = 'A' "
            r"GROUP BY  "
            r"    CAR.CARREGAMENTO,  "
            r"    CAR.DESCRICAO, "
            r"    CASE "
            r"        WHEN MAQ.DESCRICAO LIKE '%SERRA-FITA%'      THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PLASMA%'          THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%LASER%'           THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%GUILHOTINA%'      THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PUNCIONADEIRA%'   THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PRENSA%'          THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%DOBRADEIRA%'      THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%CALANDRA%'        THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%LIXADEIRA%'       THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%CONFORMADORA%'    THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%REBORDEADOR%'     THEN 'SOLDAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%METALEIRA%'       THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%FICEP%'           THEN 'PREPARACAO' "
            r"        WHEN MAQ.DESCRICAO LIKE '%TORNO%'           THEN 'USINAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%FRESA%'           THEN 'USINAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%FURADEIRA%'       THEN 'USINAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%MAQUINA-TUBO%'    THEN 'USINAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%MIG%'             THEN 'SOLDAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PARAFUSADEIRA%'   THEN 'PRE-MONTAGEM' "
            r"        WHEN MAQ.DESCRICAO LIKE '%PISTOLA%'         THEN 'PINTURA' "
            r"        WHEN MAQ.DESCRICAO LIKE '%TANQUE%'          THEN 'PREPARACAO-SUPERFICIE' " 
            r"        WHEN MAQ.DESCRICAO LIKE '%JATO%'            THEN 'PREPARACAO-SUPERFICIE' " 
            r"        WHEN MAQ.DESCRICAO LIKE '%GRAVADORA%'       THEN 'ALMOX' " 
            r"        ELSE 'NULL' " 
            r"    END " 
            r"ORDER BY TO_NUMBER(CAR.CARREGAMENTO) DESC " 
        )
        car_abertos = cur.fetchall()
        car_abertos = pd.DataFrame(car_abertos, columns=[
            'CARREGAMENTO', 'DESCRICAO', 'EM_ABERTO', 'ENCERRADAS', 'LOCAL_PROD'
        ])
        car_abertos['CARREGAMENTO'] = car_abertos['CARREGAMENTO'].astype(str)

        # pivotando df
        car_abertos["PROPORCAO"] = car_abertos["EM_ABERTO"].astype(str) + " / " + (
                car_abertos["EM_ABERTO"] + car_abertos["ENCERRADAS"]).astype(str)

        # Pivotando os dados para transformar LOCAL_PROD em colunas
        car_abertos = car_abertos.pivot_table(
            index=["CARREGAMENTO", "DESCRICAO"],
            columns="LOCAL_PROD",
            values="PROPORCAO",
            aggfunc="first",
            fill_value="0 / 0",
        )

        car_abertos = car_abertos.reset_index()
        car_abertos = car_abertos.sort_values(by='CARREGAMENTO', ascending=False)
        car_abertos = car_abertos.replace('0 / 0', '-')
        # car_abertos = car_abertos.drop(columns=["NULL"])
        car_abertos = car_abertos[[
            'CARREGAMENTO', 'DESCRICAO', 'PREPARACAO', 'USINAGEM', 'SOLDAGEM', 'PREPARACAO-SUPERFICIE', 'PINTURA',
            'PRE-MONTAGEM', 'ALMOX'
        ]]
        return car_abertos

    def car_data(self, carregamento):
        cur = self.conexao.conectar()
        cur.execute(
            r"SELECT  "
            r"    MAQ.DESCRICAO, "
            r"    COUNT(TOR.NUM_ORDEM) AS TOT_ORDENS, "
            r"    SUM(TOR.QTDE) TOT_PECAS, "
            r"    COUNT(CASE WHEN NOT EXISTS( "
            r"                            SELECT MOV.ID FROM FOCCO3I.TORDENS_MOVTO MOV "
            r"                            WHERE MOV.TORDEN_ROT_ID = ROT.ID "
            r"                            ) THEN 1 END) AS EM_ABERTO, "
            r"    COUNT(CASE WHEN TOR.TIPO_ORDEM = 'OFE' THEN 1 END) AS ENCERRADAS "
            r"FROM FOCCO3I.TORDENS TOR "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ROT                  ON TOR.ID = ROT.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TORD_ROT_FAB_MAQ FAB             ON ROT.ID = FAB.TORDEN_ROT_ID "
            r"INNER JOIN FOCCO3I.TMAQUINAS MAQ                    ON FAB.MAQUINA_ID = MAQ.ID "
            r"INNER JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VINC      ON TOR.ID = VINC.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON VINC.CARERGAM_ID = CAR.ID "
            r"WHERE CAR.CARREGAMENTO IN (" + carregamento + ") "
            r"GROUP BY MAQ.DESCRICAO "
        )
        car_data = cur.fetchall()
        car_data = pd.DataFrame(car_data, columns=['MAQ', 'TOT_ORDENS', 'TOT_PECAS', 'EM_ABERTO', 'ENCERRADAS'])
        car_data[['TOT_ORDENS', 'TOT_PECAS', 'EM_ABERTO', 'ENCERRADAS']] = car_data[[
            'TOT_ORDENS', 'TOT_PECAS', 'EM_ABERTO', 'ENCERRADAS'
        ]].astype('int64')

        car_data["PROPORCAO"] = car_data["EM_ABERTO"].astype(str) + " / " + (
                car_data["EM_ABERTO"] + car_data["ENCERRADAS"]).astype(str)

        car_data = car_data.reset_index()
        car_data = car_data.sort_values(by='MAQ', ascending=False)
        car_data.drop(['EM_ABERTO', 'ENCERRADAS', 'index'], axis=1, inplace=True)
        car_data = car_data.rename(columns={
            'MAQ': 'Maquina', 'TOT_PECAS': 'Qtd. Peças', 'TOT_ORDENS': 'Qtd. Ordens', 'PROPORCAO': 'Abertas / Total'
        }).reset_index(drop=True)
        return car_data

    def car_desc(self, carregamento):
        cur = self.conexao.conectar()
        cur.execute(
            r"SELECT CAR.DESCRICAO FROM FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR "
            r"WHERE CAR.CARREGAMENTO IN (" + carregamento + ")  "
        )
        car_desc = cur.fetchall()[0][0]
        return car_desc

    def car_details(self, carregamento, machine=None):
        if machine:
            machine = "AND MAQ.DESCRICAO IN (" + ", ".join(f"'{m}'" for m in machine.split(",")) + ") "
        else:
            machine = ''

        print(machine)
        cur = self.conexao.conectar()
        cur.execute(
            r"SELECT DISTINCT  "
            r"    CAR.CARREGAMENTO, "
            r"    TOR.NUM_ORDEM, "
            r"    TPL.COD_ITEM,  "
            r"    TOR.QTDE,  "
            r"    TIT.DESC_TECNICA, "
            r"    MAQ.DESCRICAO AS MAQUINA, "
            r"    ALM.DESCRICAO   "
            r"FROM FOCCO3I.TITENS_PLANEJAMENTO TPL "
            r"INNER JOIN FOCCO3I.TITENS_EMPR EMP      ON TPL.ITEMPR_ID = EMP.ID "
            r"INNER JOIN FOCCO3I.TITENS TIT           ON EMP.ITEM_ID = TIT.ID  "
            r"INNER JOIN FOCCO3I.TORDENS TOR          ON TPL.ID = TOR.ITPL_ID "
            r"INNER JOIN FOCCO3I.TDEMANDAS TDE        ON TOR.ID = TDE.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TORDENS_ROT ROT      ON TOR.ID = ROT.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TORD_ROT_FAB_MAQ FAB ON ROT.ID = FAB.TORDEN_ROT_ID "
            r"INNER JOIN FOCCO3I.TMAQUINAS MAQ        ON FAB.MAQUINA_ID = MAQ.ID "
            r"INNER JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VINC      ON TOR.ID = VINC.ORDEM_ID "
            r"INNER JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON VINC.CARERGAM_ID = CAR.ID "
            r"INNER JOIN FOCCO3I.TALMOXARIFADOS ALM           ON ALM.ID = TOR.ALMOX_ID "
            r"WHERE CAR.CARREGAMENTO IN (" + carregamento + ") "
            r"" + machine + " "            
            r"GROUP BY  "
            r"    TPL.COD_ITEM,  "
            r"    TOR.NUM_ORDEM, "
            r"    TOR.QTDE,  "
            r"    TIT.DESC_TECNICA, "
            r"    MAQ.DESCRICAO, "
            r"    CAR.CARREGAMENTO,"
            r"    ALM.DESCRICAO   "
            r"HAVING COUNT(CASE  "
            r"    WHEN NOT EXISTS ( "
            r"        SELECT MOV.ID  "
            r"        FROM FOCCO3I.TORDENS_MOVTO MOV  "
            r"        WHERE MOV.TORDEN_ROT_ID = ROT.ID "
            r"    ) THEN 1  "
            r"ELSE NULL  "
            r"END) > 0 "
        )
        car_data = cur.fetchall()
        car_data = pd.DataFrame(car_data, columns=['CARREGAMENTO', 'NUM_ORDEM', 'COD_ITEM', 'QTDE', 'DESC_TECNICA', 'MAQUINA', 'ALMOX'])
        car_data[['CARREGAMENTO', 'COD_ITEM', 'NUM_ORDEM', 'QTDE']] = car_data[['CARREGAMENTO', 'COD_ITEM', 'NUM_ORDEM', 'QTDE']].astype('int64')

        return car_data

    def arranjaveis(self, machine, carregamento):
        cur = self.conexao.conectar()
        cur.execute(
            '''WITH DATA AS (
                SELECT TOR.NUM_ORDEM,
                       ROW_NUMBER() OVER (ORDER BY TOR.NUM_ORDEM) AS RN
                FROM FOCCO3I.TORDENS TOR  
                INNER JOIN FOCCO3I.TORDENS_ROT ROT                  ON TOR.ID = ROT.ORDEM_ID 
                INNER JOIN FOCCO3I.TORD_ROT_FAB_MAQ FAB             ON ROT.ID = FAB.TORDEN_ROT_ID 
                INNER JOIN FOCCO3I.TMAQUINAS MAQ                    ON FAB.MAQUINA_ID = MAQ.ID 
                INNER JOIN FOCCO3I.TSRENG_ORDENS_VINC_CAR VINC      ON TOR.ID = VINC.ORDEM_ID 
                INNER JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON VINC.CARERGAM_ID = CAR.ID 
                WHERE CAR.CARREGAMENTO IN (:carregamento)
                AND MAQ.DESCRICAO IN (:machine) 
            ),
            GROUPED AS (
                SELECT NUM_ORDEM, CEIL(RN / 420) AS GROUP_ID
                FROM DATA
            )
            SELECT LISTAGG(NUM_ORDEM, ', ') WITHIN GROUP (ORDER BY NUM_ORDEM) AS NUM_ORDENS
            FROM GROUPED
            GROUP BY GROUP_ID''',
            {"carregamento": carregamento, "machine": machine}
        )
        lis_maquina = cur.fetchall()
        lis_maquina = list(set(lis_maquina[0][0].split(', '))) if lis_maquina and lis_maquina[0][0] else None
        return lis_maquina


if __name__ == "__main__":
    db = BD()
    # print(db.car_details('MIG', '448700'))
    # print(db.car_abertos().to_string())
    print(db.arranjaveis('MIG', '448700'))
