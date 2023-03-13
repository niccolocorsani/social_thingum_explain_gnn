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
        self.button2 = QPushButton('Apri report')

        # Creazione delle label
        self.label1 = QLabel('Label 1')
        self.label2 = QLabel('Label 2')

        # Creazione della text area
        self.text_area = QTextEdit()

        # Connessione dei bottoni alla funzione di gestione dell'evento
        self.button1.clicked.connect(self.aggiorna_dati)
        self.button2.clicked.connect(lambda: self.write_button_name(self.button2))

        # Creazione della layout
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.label1)
        hbox1.addWidget(self.button1)
        vbox.addLayout(hbox1)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.label2)
        hbox2.addWidget(self.button2)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.text_area)

        # Creazione del menu a tendina
        self.combo_box = QComboBox()

        # Dalla directory attuale prendi tutti i file che contengo la substringa 'log'
        # e li aggiungi al menu a tendina
        import glob
        files = glob.glob(os.path.join(ROOT_DIR+'/jsons', '*log*'))
        for file in files:
            self.combo_box.addItem(file)


        # Connessione del menu a tendina alla funzione di gestione dell'evento
        self.combo_box.currentIndexChanged.connect(self.handle_combo_box)

        # Aggiunta del menu a tendina alla layout
        vbox.addWidget(self.combo_box)

        self.setLayout(vbox)

    def handle_combo_box(self, index):
      option = self.combo_box.itemText(index)
      self.openWebPage(option.replace('.json', '.html').replace('/jsons',''))
      self.text_area.append("Opzione selezionata: " + option)



    def write_button_name(self, button):
        self.text_area.append(button.text())



    def aggiorna_dati(self):
      run_all_pipeline_to_update_json_and_my_sql()
      trasferisci_mysql_a_big_query()
      self.text_area.append("Cartella jsons, mysql e bigquery aggiornati " )

    def openWebPage(self, htmlFile):
      import webbrowser
      import http.server
      import threading
      import random
      import os
      import socketserver

      # Generate a random port number
      # Get the path of the HTML file to serve
      html_file_path = ROOT_DIR + '/best_subgraph.html'

      # Generate a random port number
      port = random.randint(1024, 65535)

      os.chdir(os.path.dirname(html_file_path))
      # Start a simple HTTP server to serve the HTML file at the random port number
      handler_class = http.server.SimpleHTTPRequestHandler
      handler_class.extensions_map['.html'] = 'text/html'
      httpd = socketserver.TCPServer(("", port), handler_class)
      threading.Thread(target=httpd.serve_forever).start()
      # Open the web page in the default browser
      webbrowser.open(('http://localhost:{}/' + htmlFile).format(port))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
