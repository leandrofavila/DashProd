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


    def desconectar(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()


class BD:
    def __init__(self):
        self.conexao = Conn()

    def car_abertos(self):
        cur = self.conexao.conectar()
        cur.execute(
            r"SELECT      "
            r"    CAR.CARREGAMENTO, "
            r"    CAR.DESCRICAO, "
            r"    COUNT(CASE WHEN TOR.TIPO_ORDEM IN ('OFA', 'OFM') THEN 1 END) AS EM_ABERTO, "
            r"    COUNT(CASE WHEN TOR.TIPO_ORDEM = 'OFE' THEN 1 END) AS ENCERRADAS "
            r"FROM FOCCO3I.TSRENG_ORDENS_VINC_CAR VIN "
            r"INNER JOIN FOCCO3I.TSRENGENHARIA_CARREGAMENTOS CAR  ON CAR.ID = VIN.CARERGAM_ID "
            r"INNER JOIN FOCCO3I.TORDENS TOR                      ON TOR.ID = VIN.ORDEM_ID "
            r"WHERE CAR.SITUACAO = 'A' "
            r"AND CAR.CARREGAMENTO > 339200 "
            r"GROUP BY CAR.CARREGAMENTO, CAR.DESCRICAO "
            r"ORDER BY TO_NUMBER(CAR.CARREGAMENTO) DESC "
        )
        car_abertos = cur.fetchall()
        car_abertos = pd.DataFrame(car_abertos, columns=['CARREGAMENTO', 'DESCRICAO', 'EM_ABERTO', 'ENCERRADAS'])
        car_abertos['CARREGAMENTO'] = car_abertos['CARREGAMENTO'].astype(str)
        self.conexao.desconectar()
        return car_abertos


if __name__ == "__main__":
    db = BD()
    print(db.car_abertos().to_string())


