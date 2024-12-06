from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
from datetime import datetime
from dash import dcc, html, Output, Input, Dash, dash
from ConDB import BD
from PlanejamentoSemanal import PLANEJAMENTO

server = Flask(__name__)

bd = BD()
pl_semanal = PLANEJAMENTO()

df_car_abertos = bd.car_abertos()
df_pla_semanal = pl_semanal.get_df_pl_semanal()

df_car_abertos = pd.merge(df_car_abertos, df_pla_semanal, on='CARREGAMENTO', how='left')
df_car_abertos = df_car_abertos.sort_values(by='DATA', ascending=False)
df_car_abertos['DATA'] = pd.to_datetime(df_car_abertos['DATA'], format='%d/%m/%Y', errors='coerce')

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
    filtered_df = df_car_abertos[df_car_abertos['DATA'].dt.month == selected_month]
    filtered_df['DATA'] = filtered_df['DATA'].dt.strftime('%d/%m/%Y')

    return dash.dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in filtered_df.columns],
        data=filtered_df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'}
    )


# Rota principal do Flask
@server.route('/')
def index():
    return redirect('/dashboard/')


@server.route('/details/<pedido>')
def details(pedido):
    return f"Detalhes do Pedido: {pedido}"


# Executar o servidor
if __name__ == '__main__':
    server.run(debug=True)
