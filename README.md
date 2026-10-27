# 📚 MangaWorld Scraper

**Scarica i volumi dei manga da MangaWorld e convertili automaticamente in PDF.**

MangaWorld Scraper è uno strumento sviluppato in Python che automatizza il download dei volumi di un'opera disponibile su MangaWorld. Il programma raccoglie le pagine dei capitoli, le organizza nell'ordine corretto e genera un PDF per ogni volume.

🚀 **Non serve installare Python per utilizzare il programma:** sono disponibili eseguibili precompilati tramite build automatiche per **Linux, macOS e Windows**.

## ✨ Funzionalità

- 📚 **Download completo** — scarica tutti i volumi disponibili di un'opera.
- 📄 **Conversione in PDF** — genera un PDF separato per ogni volume.
- 📂 **Destinazione personalizzabile** — scegli dove salvare i manga scaricati.
- 🧹 **Pulizia automatica** — elimina le immagini temporanee dopo la creazione del PDF.
- 🛠️ **Gestione degli errori** — conserva le immagini temporanee disponibili in caso di problemi durante il download.

## ⬇️ Download e installazione

### Metodo consigliato: eseguibili precompilati

Vai alla sezione **[Releases](../../releases/latest)** e scarica il file corrispondente al tuo sistema operativo.

| Sistema operativo | File da scaricare |
|---|---|
| 🐧 Linux | Eseguibile per Linux |
| 🍎 macOS | Eseguibile per macOS |
| 🪟 Windows | Eseguibile per Windows |

Le release vengono generate automaticamente tramite una procedura di build. In questo modo puoi utilizzare il programma senza dover installare manualmente Python e le sue librerie.

1. Apri la pagina delle [ultime release](../../releases/latest).
2. Individua la sezione **Assets**.
3. Scarica l'eseguibile compatibile con il tuo sistema operativo.
4. Estrai l'archivio, se necessario.
5. Avvia il programma dal terminale seguendo gli esempi riportati di seguito.

## 📖 Come si usa

La sintassi generale è:

```text
ScraperMW URL_DELL_OPERA [VOLUME] [-o CARTELLA_DESTINAZIONE]
```
sostituisci `ScraperMW` con il percorso e il nome effettivi del file scaricato.

### ⚠️ Quale URL bisogna inserire?

Devi inserire **l'URL della pagina principale dell'opera su MangaWorld**, quella in cui sono presentate le informazioni sul manga e l'elenco dei suoi volumi.

Non devi inserire l'URL di un singolo capitolo, di una pagina di lettura o di una singola immagine.

Copia l'indirizzo della pagina principale dell'opera dalla barra del browser e usalo come `URL_DELL_OPERA`.

### 📚 Scaricare tutti i volumi

```bash
ScraperMW "URL_DELL_OPERA"
```

Il programma individua i volumi disponibili e li scarica uno dopo l'altro, generando un PDF per ciascun volume.

### 📕 Scaricare un singolo volume

Per scaricare esclusivamente il volume 5:

```bash
ScraperMW "URL_DELL_OPERA" 5
```

Il numero del volume deve essere maggiore o uguale a `1` e corrispondere a un volume disponibile.

### 📂 Scegliere la cartella di destinazione

Utilizza l'opzione `-o` oppure `--output-dir` per scegliere dove salvare i file:

```bash
ScraperMW "URL_DELL_OPERA" -o "/percorso/alla/cartella/Manga"
```

Per scaricare il solo volume 5 in una cartella specifica:

```bash
ScraperMW "URL_DELL_OPERA" 5 -o "/percorso/alla/cartella/Manga"
```

Se non specifichi una destinazione, il programma utilizza la directory corrente, cioè la cartella da cui viene eseguito il comando.

### ❔ Visualizzare l'aiuto

Per consultare gli argomenti disponibili:

```bash
ScraperMW --help
```

## 🗂️ Organizzazione dei file

Il programma crea automaticamente una cartella per l'opera e salva al suo interno i PDF dei volumi.

```text
Manga/
└── NomeOpera/
    ├── volume-1.pdf
    ├── volume-2.pdf
    ├── volume-3.pdf
    └── ...
```

Durante il download vengono create anche cartelle temporanee contenenti le immagini dei capitoli. Quando il PDF viene creato correttamente, queste immagini vengono eliminate.

Se si verifica un errore, le immagini temporanee già scaricate vengono conservate per agevolare il recupero del lavoro svolto.

## 🧩 Tecnologie utilizzate

| Tecnologia | Utilizzo |
|---|---|
| [Python](https://www.python.org/) | Linguaggio di programmazione |
| [Requests](https://requests.readthedocs.io/) | Richieste HTTP e download |
| [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) | Analisi del codice HTML |
| [Pillow](https://pillow.readthedocs.io/) | Elaborazione delle immagini e creazione dei PDF |

## ⚠️ Limitazioni

- Il funzionamento dipende dalla struttura delle pagine di MangaWorld, che potrebbe cambiare nel tempo.
- È necessaria una connessione a Internet durante il download.
- Il programma non garantisce il ripristino automatico di un download interrotto.
- La memoria e lo spazio su disco richiesti dipendono dal numero e dalle dimensioni delle pagine.
- Errori del sito o eventuali restrizioni alle richieste possono impedire il completamento del download.

## ⚖️ Note legali

Il progetto è realizzato a scopo didattico e per uso personale.

Chi utilizza il programma è responsabile del rispetto delle leggi applicabili, dei termini di servizio della piattaforma e dei diritti d'autore. Scarica esclusivamente contenuti che sei autorizzato a scaricare.

## 📄 Licenza

Questo progetto è distribuito sotto licenza **GNU General Public License v3.0 (GPL-3.0)**.

Sei libero di utilizzare, studiare, modificare e ridistribuire il software, nel rispetto delle condizioni previste dalla licenza. In particolare, la distribuzione di versioni modificate deve rispettare gli obblighi di copyleft della GPL-3.0.

Per maggiori informazioni, consulta il file [`LICENSE`](LICENSE) incluso nel repository oppure visita la pagina ufficiale della [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html).

---

*Realizzato con Python 🐍*
