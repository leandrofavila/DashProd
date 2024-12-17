from flask import Flask, render_template, redirect, url_for, send_file
import pandas as pd
from ConDB import BD
from PlanejamentoSemanal import PLANEJAMENTO
import fitz


server = Flask(__name__, static_folder='static')

bd = BD()
pl_semanal = PLANEJAMENTO()


@server.route('/')
def index():
    return redirect('/initial/')


def generate_pdf_thumbnail(pdf_path, output_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document[0]  # Seleciona a primeira página
    pix = page.get_pixmap()  # Renderiza a página
    pix.save(output_path)  # Salva como imagem
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
                <a href="{url_png}" target="_blank" style="text-decoration: none; color: inherit;">
                    <img src="{url_png}" alt="Miniatura do PDF" style="width: 100%; height: auto;">
                </a>
                <figcaption>{value}</figcaption>
            </figure>
        '''
    except Exception as e:
        print(f"Error processing value {value}: {e}")
        return value



def style_cells(value):
    if isinstance(value, str) and value.startswith("0 / "):
        return f'<div style="background-color: lightgreen;" title="PRONTO">FINALIZADO</div>'
    return value


@server.route('/initial/')
def update_table():
    # Adicionando a data de entrega do planejamento semanal a cada carregamento com sit 'A' do Focco
    df_car_abertos = bd.car_abertos()
    df_pla_semanal = pl_semanal.get_df_pl_semanal()
    df_car_abertos = pd.merge(df_car_abertos, df_pla_semanal, on='CARREGAMENTO', how='left')
    df_car_abertos = df_car_abertos.sort_values(by='DATA_', ascending=False)
    try:
        df_car_abertos_copy = df_car_abertos.copy()
        df_car_abertos_copy['CARREGAMENTO'] = df_car_abertos_copy['CARREGAMENTO'].apply(
            lambda x: f'<a href="/dashboard/{x}" target="_self" style="text-decoration: none;">{x}</a>'
        )

        # Converter para HTML
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
    global car_data
    car_data = bd.car_data(str(carregamento))
    global desc_carregamento
    desc_carregamento = bd.car_desc(str(carregamento))

    #add link para as maquinas
    car_data['Maquina'] = car_data['Maquina'].apply(
        lambda x: f'<a href="/details/{x}/{carregamento}" target="_self" style="text-decoration: none;">{x}</a>'
    )
    # Renderizar a tabela resumida
    car_data = car_data.astype(str)
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
    filtered_df = bd.car_details(machine, carregamento)

    if filtered_df.empty:
        return render_template(
            "details.html",
            machine=machine,
            table_detail=None,
            message="Nenhum valor encontrado para essa máquina."
        )

    detail_table = filtered_df.to_html(
        classes="table",
        index=False,
        escape=False,
        formatters={'COD_ITEM': style_pdf_cells}
    )
    return render_template(
        "details.html",
        machine=machine,
        table_detail=detail_table,
        message=None
    )


if __name__ == '__main__':
    try:
        server.run(host='0.0.0.0', port=8000)
    except Exception as err:
        print(err)
