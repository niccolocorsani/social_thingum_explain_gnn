import os

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QComboBox
import sys

from MySQL_to_BigQuery import trasferisci_mysql_a_big_query
from generate_csv_json_mysql_from_log import run_all_pipeline_to_update_json_and_my_sql

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MyWindow(QWidget):
  def __init__(self):
    super().__init__()

    # Creazione dei bottoni
    self.button1 = QPushButton('Aggiorna Json, MySQL, BigQuery')

    # Creazione delle label
    self.label1 = QLabel(
      'La seguente feature permette di creare il Json a partire dai file di log.txt,\n successivmanete viene creato il DB Schema MySQL e aggiornati i dati di conseguenza. \n Infine viene trasferita la logica di MySQL su BigQuery.')

    # Creazione della text area
    self.text_area = QTextEdit()

    # Connessione dei bottoni alla funzione di gestione dell'evento
    self.button1.clicked.connect(self.aggiorna_dati)

    # Creazione della layout
    vbox = QVBoxLayout()
    hbox1 = QHBoxLayout()
    hbox1.addWidget(self.label1)
    hbox1.addWidget(self.button1)
    vbox.addLayout(hbox1)
    hbox2 = QHBoxLayout()
    vbox.addLayout(hbox2)
    vbox.addWidget(self.text_area)

    self.label2 = QLabel('Seleziona uno dei report per poter visualizzare i dati relativi alle esecuzioni Monte Carlo')

    vbox.addWidget(self.label2)

    # Creazione del menu a tendina
    self.combo_box = QComboBox()

    # Dalla directory attuale prendi tutti i file che contengo la substringa 'log'
    # e li aggiungi al menu a tendina
    import glob
    files = os.listdir(ROOT_DIR + '/jsons')
    for file in files:
      self.combo_box.addItem(file)

    # Connessione del menu a tendina alla funzione di gestione dell'evento
    self.combo_box.currentIndexChanged.connect(self.handle_combo_box)

    # Aggiunta del menu a tendina alla layout
    vbox.addWidget(self.combo_box)

    self.setLayout(vbox)

  def handle_combo_box(self, index):
    option = self.combo_box.itemText(index)
    print(option)

    html_file =ROOT_DIR +'/html_view_reports'
    html_file = html_file + option.replace('.json', '.html')
    print(html_file)
    self.openWebPage(html_file)
    self.text_area.append("Opzione selezionata: " + option)

  def aggiorna_dati(self):
    run_all_pipeline_to_update_json_and_my_sql()
    trasferisci_mysql_a_big_query()
    self.text_area.append("Cartella jsons, mysql e bigquery aggiornati ")

  def openWebPage(self, htmlFile):
    import webbrowser
    import http.server
    import threading
    import random
    import os
    import socketserver

    # Generate a random port number
    # Get the path of the HTML file to serve
    html_file_path = ROOT_DIR + '/charts.html'

    # Generate a random port number
    port = random.randint(1024, 65535)

    os.chdir(os.path.dirname(html_file_path))
    # Start a simple HTTP server to serve the HTML file at the random port number
    handler_class = http.server.SimpleHTTPRequestHandler
    handler_class.extensions_map['.html'] = 'text/html'
    httpd = socketserver.TCPServer(("", port), handler_class)
    threading.Thread(target=httpd.serve_forever).start()
    # Open the web page in the default browser

    htmlFile = htmlFile.replace(ROOT_DIR,'').replace('/','')


    html_file_charts = '/charts.html' + '?'+ htmlFile

    print(html_file_charts)




    webbrowser.open(('http://localhost:{}' + html_file_charts).format(port))


if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = MyWindow()
  window.show()
  sys.exit(app.exec())
