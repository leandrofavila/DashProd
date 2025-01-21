from flask import Flask, render_template, redirect, url_for, g, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd
from ConDB import BD
from PlanejamentoSemanal import PLANEJAMENTO
import fitz
import os
from jinja2 import Environment, FileSystemLoader
import win32api
from weasyprint import HTML
from datetime import datetime
import re
import pickle

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

server = Flask(__name__, static_folder='static')
bd = BD()
pl_semanal = PLANEJAMENTO()


@server.route('/')
def index():
    return redirect('/initial/')


def generate_pdf_thumbnail(pdf_path, output_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document[0]
    pixel = page.get_pixmap()
    pixel.save(output_path)
    pdf_document.close()


def style_pdf_cells(value):
    try:
        value = str(value)
        pdf_thumbnail = fr"C:\Users\pcp03\PycharmProjects\DashProd\static\pdf_thumbnails\{value}.png"
        pdf_path = f"T:\\06_Desenhos_PDF\\{value}.pdf"
        generate_pdf_thumbnail(pdf_path, pdf_thumbnail)
        url_png = url_for('static', filename=fr'pdf_thumbnails/{value}.png')
        return f'''
            <figure>
                <a href="{url_png}" target="_blank"">
                    <img src="{url_png}" alt="Miniatura do PDF"">
                </a>
            </figure>
        '''
    except Exception as e:
        print(f"Error processing value {value}: {e}")
        return value


def style_cells(value):
    if isinstance(value, str) and value.startswith("0 / "):
        return f'<div style="background-color: green; border-radius: 6px;">FINALIZADO</div>'
    return value


def arranjadas(lis_ordens):
    if not lis_ordens:
        return False
    folder_paths = [os.path.join(folder, f"{ordem}.PDF") for ordem in lis_ordens for folder in [
        r"Y:\Cnc\Puncionadeira_Cnc\PDF_Xml", r"Y:\Cnc\Plasma_Cnc\Pdf_Xml", r"Y:\Cnc\Laser\PDF_laser"
    ]]
    return any(os.path.exists(path) for path in folder_paths)


def style_machine(machine):
    status = g.dic_arranjadas.get(machine, None)
    color = 'green' if status else 'red' if status is not None else 'white'
    return f'<a href="/details/{machine}/{g.carregamento}" target="_self" style="text-decoration: none; color: {color};">{machine}</a>'


def invalid_date(value):
    if isinstance(value, str):
        match = re.match(r"(\d{2}).*?(\d{2}/\d{2})", value)
        if match:
            _, month = match.groups()
            new_date = f"{month}/{datetime.now().year}"
            return pd.to_datetime(new_date, format="%d/%m/%Y", errors='coerce')
        return value
    

@server.errorhandler(429)
def ratelimit_error(e):
    return jsonify(error=f"Muitas requisições, menos cliques por favor.{e}"), 429


limiter = Limiter(
    get_remote_address,
    app=server,
    default_limits=["1 per second"]
)


@server.route('/initial/')
def update_table():
    #todo - Amanda pediu para adicionar o peso dos itens faltantes
    # Adicionando a data de entrega do planejamento semanal a cada carregamento com sit 'A' do Focco
    df_car_abertos = bd.car_abertos()
    dic_pla_semanal = pl_semanal.get_df_pl_semanal()
    df_car_abertos['DATA_'] = df_car_abertos['CARREGAMENTO']. map(dic_pla_semanal)

    try:
        df_car_abertos_copy = df_car_abertos.copy()
        df_car_abertos_copy.columns.name = None
        #cria os checkbox
        df_car_abertos_copy.insert(0, 'Sel.',
                                   df_car_abertos_copy['CARREGAMENTO'].apply(
                                       lambda x: f'<input type="checkbox" class="row-checkbox" value="{x}">'
                                   ))

        df_car_abertos_copy['CARREGAMENTO'] = df_car_abertos_copy['CARREGAMENTO'].apply(
            lambda x: f'<a href="/dashboard/{x}" target="_self" style="text-decoration: none;">{x}</a>'
        )

        df_car_abertos_copy['DATA_AUX'] = pd.to_datetime(
            df_car_abertos_copy['DATA_'],
            format="%d/%m/%Y",
            errors='coerce'
        )

        #tratando as datas com 'a'
        df_car_abertos_copy['DATA_AUX'] = df_car_abertos_copy.apply(
            lambda row: invalid_date(row['DATA_']) if pd.isna(row['DATA_AUX']) else row['DATA_AUX'], axis=1
        )


        df_car_abertos_copy = df_car_abertos_copy.sort_values(by='DATA_AUX')
        df_car_abertos_copy = df_car_abertos_copy.drop(columns=['DATA_AUX'])
        df_car_abertos_copy.rename(columns={
            "CARREGAMENTO": "CARR.",
            "PREPARACAO-SUPERFICIE": "SUPERFICIE",
            "PRE-MONTAGEM": "MONTAGEM",
            "DATA_": "DATA"
        }, inplace=True)

        table_html = df_car_abertos_copy.to_html(
            classes="table",
            index=False,
            escape=False,
            formatters={col: style_cells for col in df_car_abertos_copy.columns},
        )

        return render_template("initial.html", table_summary=table_html)
    except Exception as e:
        return f"Erro ao processar os dados: {str(e)}", 500


@server.route('/dashboard/<carregamento>')
def dashboard(carregamento):
    car_data = bd.car_data(str(carregamento))
    g.car_data = car_data
    desc_carregamento = bd.car_desc(str(carregamento))

    g.carregamento = carregamento

    puncionadeira_arranjada = arranjadas(bd.arranjaveis('PUNCIONADEIRA', carregamento))
    laser_arranjada = arranjadas(bd.arranjaveis('LASER', carregamento))
    plasma_arranjada = arranjadas(bd.arranjaveis('PLASMA', carregamento))


    dic_arranjadas = {'PUNCIONADEIRA': puncionadeira_arranjada, 'LASER': laser_arranjada, 'PLASMA': plasma_arranjada}
    g.dic_arranjadas = dic_arranjadas

    # Adicionar link para as máquinas
    try:
        car_data['Maquina'] = car_data['Maquina'].apply(style_machine)
    except Exception as erro:
        return f"Erro: {erro}", 500

    # Renderizar a tabela resumida
    car_data = car_data.astype(str)
    car_data = car_data.sort_values(by=['Abertas / Total'], ascending=False)
    summary_table = car_data.to_html(
        classes="table",
        index=False,
        escape=False,
        formatters={col: style_cells for col in car_data.columns}
    )

    return render_template(
        "dashboard.html",
        table_summary=summary_table,
        carregamento=carregamento,
        desc_carregamento=desc_carregamento
    )


@server.route('/details/<machine>/<carregamento>')
def details(machine, carregamento):
    filtered_df = bd.car_details(carregamento, machine)
    filtered_df = filtered_df.drop(columns=['CARREGAMENTO', 'MAQUINA'])
    desc_carregamento = bd.car_desc(str(carregamento))

    if filtered_df.empty:
        return render_template(
            "details.html",
            machine=machine,
            cards=None,
            message="Nenhum valor encontrado para essa máquina."
        )

    cards_html = []

    for _, row in filtered_df.iterrows():
        pdf_thumbnail = style_pdf_cells(row['COD_ITEM'])

        card_html = f"""
        <div class="card">
            <div class="card-image">
                {pdf_thumbnail}
            </div>
            <div class="card-content">
                <div class="row">
                    <span class="label">ORDEM:</span>
                    <span class="value">{row['NUM_ORDEM']}</span>
                    <span style="margin-left: 60px;"></span> <span class="label">QTDE:</span>
                    <span class="value">{row['QTDE']}</span>
                </div>
                <div class="row desc-tecnica">
                    {row['COD_ITEM']} - {row['DESC_TECNICA']}
                </div>
                <div class="row desc-tecnica">
                    Almox destino - {row['ALMOX']}
                </div>
            </div>
        </div>
        """

        cards_html.append(card_html)

    final_html = "<div class='cards-container'>" + "".join(cards_html) + "</div>"


    return render_template(
        "details.html",
        machine=machine,
        cards=final_html,
        message=None,
        carregamento=carregamento,
        desc_carregamento=desc_carregamento
    )


@server.route('/process_selected', methods=['POST'])
def process_selected():
    try:
        data = request.json
        selected_carr = data.get('selected', [])
        df_report = bd.car_details(', '.join(map(str, selected_carr)))
        unique_machines = df_report['MAQUINA'].unique().tolist()

        selected_machines = data.get('selected_machines', [])
        if not selected_machines:
            return jsonify({'unique_machines': unique_machines})

        df_report = df_report[df_report['MAQUINA'].isin(selected_machines)]
        df_report = df_report.sort_values(by=['MAQUINA', 'CARREGAMENTO'])

        temp_file_path = os.path.join(TEMP_DIR, f"{selected_carr[0]}_temp.pkl")
        with open(temp_file_path, 'wb') as temp_file:
            pickle.dump({'df_report': df_report, 'carregamento': selected_carr}, temp_file)

        report_html = df_report.to_html(classes="table", index=False)
        return jsonify({'report_html': report_html})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@server.route('/print-report', methods=['POST'])
def print_report():
    try:
        data = request.json
        temp_file_path = data.get('temp_file_path')

        with open(temp_file_path, 'rb') as temp_file:
            temp_data = pickle.load(temp_file)

        df_report = temp_data['df_report']
        carregamento = temp_data['carregamento']
        print(df_report)

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('templates/Rel_PDF.html')
        html_rel = template.render(rel_final=df_report, desc_car=carregamento,
                                   carregamento=carregamento)

        with open("html_rel.html", "w") as file:
            file.write(html_rel)

        HTML('html_rel.html').write_pdf(f"hist/rel_{carregamento}.pdf")


        win32api.ShellExecute(0, "print", 'report.pdf', None, ".", 0)
        print('foi')

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    try:
        server.run(host='0.0.0.0', port=8000)
    except Exception as err:
        print(err)
