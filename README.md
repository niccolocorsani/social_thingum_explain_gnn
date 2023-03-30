# explainable!
[Sub_graph_x_documentation.pdf](https://github.com/SocialThingsIT/explainable/files/10958899/Sub_graph_x_documentation.4.pdf)

Il sistema MCTS è composto da più fasi che vengono eseguite in maniera iterativa fin tanto che non viene trovato uno stato foglia ottimale.

Partendo da un albero del genere:

![Schermata 2023-03-13 alle 16 28 32](https://user-images.githubusercontent.com/126795492/224748728-80b93f15-f2ba-4810-b040-d4e05b4b71b7.png)



Si può osservare nella fase animata l'iniseme di azioni che vengono svolte:

![info-software-tesi](https://user-images.githubusercontent.com/126795492/223439290-3da27db2-5a26-44b1-9c03-b6f81d788a0f.gif)


La linea ondeggiata rappresenta la fase di simulation (random walk).
La linea dritta che appare alla fine dell'animazione rappresenta un'esapnsione di un nodo.
La conclusione della GIF è questa:




![Schermata 2023-03-13 alle 16 51 30](https://user-images.githubusercontent.com/126795492/224755527-bfd7e298-baae-4abe-a7ad-ba5c103d9795.png)

Dopo questa fase vi sarebbe in teoria una nuova fase di back-propagation che aggiorna tutti i nodi (nel caso specifico 3 nodi) e poi la fase select, simulation e di nuovo node exapansion.

Nella seguente immagine si può osservare un esempio di labeling:

<img width="590" alt="Immagine 2023-03-16 165844" src="https://user-images.githubusercontent.com/126795492/225679913-098ddf1c-fd15-44c5-bf6b-26c88c9f781a.png">

In particolare, come si osserva nelle immagini tutti i nodi dell'albero (rappresentati da i vari sotto grafi) hanno una label con i due valori: visits e score.

I nodi foglia sono quelli a destra e in questo caso hanno 2 edge. Su tali nodi viene calcolato il valore di win o score. Tale valore sarà propagato su sul percorso dei nodi espansi (node-expansion)


Di seguito un'altra gif che rappresenta la sequenza di azioni svolte:
![info-software-tesi](https://user-images.githubusercontent.com/126795492/226555373-35b68195-07ca-4089-94b5-6248b5e1cde4.gif)


[presentation.pptx](https://github.com/SocialThingsIT/explainable/files/11030731/presentation.pptx)

# Github action workflow

Il sistema oltre allo svolgimento dell'algoritmo MonteCarlo prevede una serie di pipeline per l'automazione di certi processi.

Una delle tante pipeline è quelle che riguarda l'automazione della creazione e caricamento di un container docker su Google Cloud Run.
Il codice relativo a ciò si trova al path ./.github/workflows/push_container_to_gcr.yml .

Di seguito una breve spiegazione del flusso:

Il file di Github action svolge una serie di azioni:






