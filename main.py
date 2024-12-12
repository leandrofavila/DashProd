from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
from datetime import datetime
from dash import dcc, html, Output, Input, Dash, dash
from dash.dash_table import DataTable
from ConDB import BD
from PlanejamentoSemanal import PLANEJAMENTO


server = Flask(__name__)

bd = BD()
pl_semanal = PLANEJAMENTO()

#Adicionando a data de entrega do planejamento semanal a cada carregamento com sit 'A' do Focco
df_car_abertos = bd.car_abertos()
df_pla_semanal = pl_semanal.get_df_pl_semanal()
df_car_abertos = pd.merge(df_car_abertos, df_pla_semanal, on='CARREGAMENTO', how='left')
df_car_abertos = df_car_abertos.sort_values(by='DATA_', ascending=False)
df_car_abertos['DATA_'] = pd.to_datetime(df_car_abertos['DATA_'], format='%d/%m/%Y', errors='coerce')


app = Dash(__name__, server=server, url_base_pathname='/dashboard/')

app.layout = html.Div([
    dcc.Slider(
        1, 12, 1,
        marks={i: {'label': month} for i, month in enumerate(
            ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'], start=1)},
        id='meu_slider',
        value=datetime.now().month,
        included=False
    ),
    html.Div(id='output_table')
])


@app.callback(
    Output('output_table', 'children'),
    [Input('meu_slider', 'value')]
)
def update_table(selected_month):
    filtered_df = df_car_abertos[df_car_abertos['DATA_'].dt.month == selected_month]
    filtered_df['DATA'] = filtered_df['DATA_'].dt.strftime('%d/%m/%Y')

    # Cria links na coluna 'CARREGAMENTO'
    filtered_df.loc[:, 'CARREGAMENTO'] = filtered_df['CARREGAMENTO'].apply(
        lambda x: f'<a href="/dashboard/{x}" target="_self" style="text-decoration: none;">{x}</a>'
    )

    filtered_df.drop('DATA_', axis=1, inplace=True)
    return dash.dash_table.DataTable(
        columns=[{"name": col, "id": col, "presentation": "markdown" if col == 'CARREGAMENTO' else None}
                 for col in filtered_df.columns],
        data=filtered_df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        markdown_options={"html": True}
    )


@server.route('/')
def index():
    return redirect('/dashboard/')


@server.route('/dashboard/<carregamento>')
def dashboard(carregamento):
    global car_data
    car_data = bd.car_data(str(carregamento))
    desc_carregamento = car_data['CAR_DESC'].iloc[0]
    car_data = car_data.drop('CAR_DESC', axis=1)

    summary = (
        car_data.groupby("MAQUINA")["TIPO_ORDEM"]
        .value_counts()
        .unstack(fill_value=0)
        .reset_index()
    )


    summary['Abertas / Total'] = ''

    def calcular_tipo_ordem_count(row):
        ofa = int(row['OFA']) if 'OFA' in row else 0
        ofe = int(row['OFE']) if 'OFE' in row else 0
        total = ofa + ofe
        return f"{ofa}/{total}"

    summary['Abertas / Total'] = summary.apply(calcular_tipo_ordem_count, axis=1)


    summary['MAQUINA'] = summary['MAQUINA'].apply(
        lambda x: f'<a href="/details/{x}" target="_self" style="text-decoration: none;">{x}</a>'
    )
    summary = summary.rename_axis(None, axis=1)
    summary = summary.drop(columns=["TIPO_ORDEM"], errors='ignore')


    # Renderizar a tabela resumida
    summary_table = summary[["MAQUINA", "Abertas / Total"]].to_html(
        classes="table", index=False, escape=False
    )

    return render_template(
        "dashboard.html",
        table_summary=summary_table,
        carregamento=carregamento,
        desc_carregamento=desc_carregamento
    )


@server.route('/details/<machine>')
def details(machine):
    filtered_df = car_data[car_data["MAQUINA"] == machine]
    filtered_df.drop('MAQUINA', axis=1, inplace=True)

    detail_table = filtered_df.to_html(classes="table", index=False, escape=False)
    return render_template(
        "details.html", machine=machine, table_detail=detail_table
    )


if __name__ == '__main__':
    server.run(debug=True)
