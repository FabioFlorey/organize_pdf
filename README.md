# 🍱 Organize PDF

<p align="center">
<img src="https://github.com/FabioFlorey/organize_pdf/assets/93403866/df7a0e2c-3202-470a-ba89-83d5867743fb" alt""">
</p>

## Descrizione

`pdf_organizer` è uno script Python progettato per gestire e organizzare documenti PDF. Il programma analizza una directory di PDF, estrae immagini dalle prime pagine, le confronta per similitudine visiva, e organizza i documenti in sottocartelle basate sulla loro similarità. È anche responsabile della gestione delle dipendenze richieste per il corretto funzionamento dello script. Lo script è progettato per essere semplice al primo utilizzo da parte di Davide, chi è Davide? Evidentemente non fate parte della Massoneria. Comunque, non ci sono orpelli, tutto è molto 'diretto'. In futuro, magari...

## Funzionalità

- **Estrazione delle Immagini**: Estrae le immagini dalla prima pagina di ogni PDF.
- **Rilevamento della Similarità**: Confronta le immagini estratte per determinare se i PDF appartengono alla stessa categoria o azienda.
- **Organizzazione dei PDF**: Sposta i PDF in sottocartelle basate sulla similarità delle immagini.
- **Installazione Automatica delle Dipendenze**: Installa automaticamente le librerie necessarie se non sono già presenti.
- **Report Finale**: Crea un report con il numero di PDF per ogni categoria trovata.

## Requisiti

Prima di eseguire il programma, assicurati di avere Python 3.8 o superiore installato. `pdf_organizer` richiede alcune librerie che possono essere installate automaticamente tramite `requirements.txt`.

## Installazione

1. **Clona il Repository**

   `git clone https://github.com/FabioFlorey/pdf_organizer.git`
   `cd pdf_organizer`

2. **Crea un Ambiente Virtuale**

   `python -m venv venv`
   `source venv/bin/activate`, mentre su Windows usa `venv\Scripts\activate`

4. **Installa le Dipendenze**

   Il programma installerà automaticamente le dipendenze se necessario, ma puoi anche eseguire questo comando per essere sicuro:

   `pip install -r requirements.txt`

## Uso

Esegui lo script con i seguenti parametri:

`python pdf_organizer.py -s /percorso/della/directory/dei/pdf [options]`

### Parametri

- `-s, --source`: *Directory contenente i PDF*  
  **Obbligatorio**. Il percorso alla directory che contiene i file PDF da organizzare.

- `-r, --requirements`: *File di testo contenente i requisiti*  
  **Opzionale**. Specifica il file che elenca le dipendenze (default: `requirements.txt`).

- `--similarity_threshold`: *Percentuale di similarità*  
  **Opzionale**. Soglia di similarità tra le immagini (default: `0.8`).

- `--ratio`: *Rapporto di taglio dell'immagine*  
  **Opzionale**. Rapporto per il taglio dell'immagine del PDF (default: `0.14`).

### Esempio

`python pdf_organizer.py -s /percorso/della/directory/dei/pdf --similarity_threshold 0.85 --ratio 0.2`

## Dettagli Tecnici

### Librerie Utilizzate

- `PyMuPDF`: Per estrarre immagini dalle pagine dei PDF.
- `Pillow`: Per elaborare le immagini.
- `imagehash`: Per calcolare e confrontare l'hash percettivo delle immagini.
- `tqdm`: Per visualizzare una barra di progresso durante il processo.
- `colorama`: Per colorare il testo nella console.

### Funzioni Principali

- **`check_and_install_packages(requirements_file)`**: Controlla e installa i pacchetti necessari.
- **`import_libraries()`**: Importa le librerie richieste e installa quelle mancanti.
- **`are_images_similar(img1, img2, threshold)`**: Verifica la similarità tra due immagini.
- **`crop_image(img, ratio)`**: Taglia e processa l'immagine estratta dal PDF.
- **`cleanup_directory(directory)`**: Elimina file e cartelle temporanee.
- **`process_pdfs(pdf_dir, img_dir, docs_dir, log_dir, similarity_threshold, ratio)`**: Elabora i PDF e li organizza in base alla loro similarità.

## Contributi

Se desideri contribuire a questo progetto, per favore segui questi passaggi:

1. **Fork** il repository.
2. Crea un nuovo branch per le tue modifiche (`git checkout -b feature/nuova-caratteristica`).
3. Fai il **commit** delle tue modifiche (`git commit -am 'Aggiunta nuova caratteristica'`).
4. **Push** il branch (`git push origin feature/nuova-caratteristica`).
5. Apri una **pull request**.

## Licenza

Questo progetto è concesso sotto la Licenza MIT - vedi il file [LICENSE](LICENSE) per dettagli.

## Contatti

Per domande o suggerimenti, contattami a [questo](mailto:fabioflorey@icloud.com) indirizzo.

---

Buona organizzazione dei PDF! 📄✨
