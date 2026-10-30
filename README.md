# London Airbnb Listings · Para-procesimi (Pjesa I)

Ky projekt analizon si ndryshon çmimi për natë i listimeve Airbnb në Londër sipas llojit të dhomës, lagjes dhe kapacitetit. Burimi i deklaruar është Inside Airbnb; një rresht përfaqëson një listim. Dataset-i lokal është `dataset/listings.csv.gz` (nuk ruhet në Git). Versioni i përdorur është snapshot-i i Londrës i datës 2026-09-17; lidhjet e shkarkimit janë më poshtë dhe te notebook-u 02 (seksioni 0).

## Notebook-et

1. [`notebooks/01_inspektimi_dhe_kualiteti.ipynb`](notebooks/01_inspektimi_dhe_kualiteti.ipynb) — mbledhja dhe kuptimi i të dhënave, tipet, kualiteti, mungesat, dublikatat, agregimi dhe mostrimi.
2. [`notebooks/02_pastrimi_dhe_transformimi.ipynb`](notebooks/02_pastrimi_dhe_transformimi.ipynb) — burimi i të dhënave, pastrimi, integrimi me `reviews` dhe `calendar`, strategjia për mungesat, vlerat ekstreme, transformimi (logaritmi, standardizimi), zgjedhja e nënbashkësisë së vetive dhe reduktimi i dimensionit (PCA).
3. [`notebooks/03_krijimi_vetive_dhe_kodimi.ipynb`](notebooks/03_krijimi_vetive_dhe_kodimi.ipynb) — krijimi i vetive të reja, grupimi i llojit të pronës dhe i pajisjeve, diskretizimi, binarizimi dhe kodimi i kategorive. Lexon `listings_clean_full.csv` nga notebook-u 02.

Çdo notebook ka shpjegime në shqip dhe kode që mund të ekzekutohen qelizë pas qelize. Grafikët shfaqen brenda notebook-ut kur ekzekutohen qelizat; nuk ruhen si skedarë imazhi. Rezultatet kryesore të ekzekutimit aktual janë te [`reports/preprocessing_summary.md`](reports/preprocessing_summary.md).

## Nisja

Nga rrënja e projektit, me Python 3.10 ose më të ri:

Windows (PowerShell):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m jupyter lab
```

Linux / macOS (bash ose zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyter lab
```

Vendosni dataset-in origjinal te `dataset/listings.csv.gz` para ekzekutimit. Ky skedar nuk përfshihet në Git. Komandat përdorin rrugë relative nga rrënja e projektit.

Notebook-u 02 integron edhe `reviews.csv.gz` dhe `calendar.csv.gz` të të njëjtit snapshot (Londër, 2026-09-17); pa to ai ndalon me një mesazh gabimi. Shkarkojini nga Inside Airbnb dhe vendosini te `dataset/` (`curl` është i disponueshëm edhe në Windows 10 e më të ri):

```bash
BASE=https://data.insideairbnb.com/united-kingdom/england/london/2026-09-17/data
curl -L -o dataset/reviews.csv.gz  $BASE/reviews.csv.gz    # rreth 287 MB
curl -L -o dataset/calendar.csv.gz $BASE/calendar.csv.gz   # rreth 82 MB
```

Edhe këta skedarë nuk përfshihen në Git: janë shumë të mëdhenj (GitHub nuk pranon skedarë mbi 100 MB), prandaj mbeten te `.gitignore`.

Hapni notebook-et sipas rendit dhe zgjidhni kernel-in e mjedisit `.venv`. Ato gjejnë automatikisht `dataset/` kur kernel-i nis nga rrënja e projektit ose nga dosja `notebooks/`. Notebook-u 02 krijon `dataset/listings_clean_full.csv` (tabela e plotë e pastruar), `dataset/listings_preprocessed.csv` (18 kolona për analizën) dhe `dataset/listings_model_ready.csv` (veti të zgjedhura dhe të standardizuara, `price_log` dhe përbërësit PCA; kolonat shpjegohen te seksioni 11 i notebook-ut). Të tre përjashtohen nga Git; të gjithë kanë kolonën `id`, me të cilën bashkohen me `listings_features.csv` të notebook-ut 03. Dataset-i origjinal nuk ndryshohet.

Skriptet ekzistuese në `scripts/` mbeten si rrjedhë alternative dhe japin të njëjtin rezultat si notebook-et në pastrim (59,846 rreshta pas pastrimit); transformimi, zgjedhja e vetive dhe PCA ekzistojnë vetëm te notebook-u 02. Raporti `reports/listings_cleaning.txt` është rigjeneruar nga dataset-i aktual me 91,954 rreshta (Londër); një version i vjetër i tij vinte nga një dataset tjetër (77,679 rreshta). Për rezultatet e kësaj pjese përdorni notebook-et dhe `reports/preprocessing_summary.md`.

## Kufizime të metodës

- Rreshtat pa çmim largohen sepse çmimi është variabla kryesore; analiza e çmimit përfaqëson vetëm listimet me çmim të njohur.
- Vlerat e `bathrooms`, `bedrooms` dhe `beds` që mbeten bosh plotësohen me medianë sipas kapacitetit. Këto janë vlerësime, jo matje origjinale.
- Çmimet mbi percentilin 99.9 të secilit lloj dhome (59 listime) hiqen si të pabesueshme; ky kufi është statistikor, ndaj disa mund të ishin listime të vërteta luksoze. Çmimet mbi percentilin 99 të mbetur vetëm shënohen, nuk fshihen.
- `price_band` është krijuar nga çmimi. Nuk duhet përdorur si hyrje për një model që parashikon çmimin; për të njëjtën arsye nuk futen te vetitë `price_quote_*` dhe `estimated_revenue_l365d`.
- Logaritmi, standardizimi, zgjedhja e vetive dhe PCA te `listings_model_ready.csv` janë llogaritur mbi të gjitha rreshtat. Një model me ndarje trajnim/test duhet t'i përsërisë mbi setin e trajnimit.
- `review_scores_rating` mbetet bosh për listimet pa vlerësim. Kjo mungesë ka kuptim dhe nuk plotësohet artificialisht.
