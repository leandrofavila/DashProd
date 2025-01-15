import pandas as pd
import json
import time


class PLANEJAMENTO:
    def __init__(self):
        with open("db_config.json", "r") as file:
            config = json.load(file)
        self.url = config["url"]

    def get_df_pl_semanal(self):
        base_url = self.url
        timestamp = int(time.time())
        url = f"{base_url}&gid=0&cache_buster={timestamp}"

        df = pd.read_csv(url, names=[
            "CLIENTE", "PEDIDO", "PROJETO", "DESCRIÇÃO DO EQUIPAMENTO", "DATA_", "FRETE", "TIPO DE VEICULO", "MOTORISTA",
            "ENTREGA", "CARREGAMENTO", "SUPRIMENTOS", "PRAZO CONTRATO", "OBSERVAÇÕES GERAIS", "1", "2", "3", "4"
            , "5", "6", "7", "8"
        ])

        df.drop(["CLIENTE", "PEDIDO", "PROJETO", "DESCRIÇÃO DO EQUIPAMENTO", "FRETE", "TIPO DE VEICULO", "MOTORISTA",
                 "ENTREGA", "SUPRIMENTOS", "PRAZO CONTRATO", "OBSERVAÇÕES GERAIS", "1", "2", "3", "4", "5", "6", "7",
                 "8"], axis=1, inplace=True)
        df = df.dropna(subset="CARREGAMENTO", how="all")

        df["CARREGAMENTO"] = df["CARREGAMENTO"].str.replace(" ", "", regex=False)
        df["CARREGAMENTO"] = df["CARREGAMENTO"].str.replace(" / ", ",", regex=False)
        df['CARREGAMENTO'] = df['CARREGAMENTO'].str.split(",")
        df = df.explode("CARREGAMENTO")
        data_car = dict(zip(df['CARREGAMENTO'], df['DATA_']))
        return data_car


if __name__ == '__main__':
    pl_semanal = PLANEJAMENTO()
    pl_semanal.get_df_pl_semanal()
