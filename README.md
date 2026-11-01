# London Airbnb Listings · Para-procesimi (Pjesa I)

Ky projekt analizon si ndryshon çmimi për natë i listimeve Airbnb në Londër sipas llojit të dhomës, lagjes dhe kapacitetit. Të dhënat vijnë nga [Inside Airbnb](https://insideairbnb.com/get-the-data/), snapshot-i i Londrës i datës 2026-09-17; një rresht përfaqëson një listim.

## Notebook-et

1. [`notebooks/01_inspektimi_dhe_kualiteti.ipynb`](notebooks/01_inspektimi_dhe_kualiteti.ipynb) — mbledhja dhe kuptimi i të dhënave, tipet, kualiteti, mungesat, dublikatat, agregimi dhe mostrimi.
2. [`notebooks/02_pastrimi_dhe_transformimi.ipynb`](notebooks/02_pastrimi_dhe_transformimi.ipynb) — burimi i të dhënave, pastrimi, integrimi me `reviews` dhe `calendar`, strategjia për mungesat, vlerat ekstreme dhe tabela e analizës me 18 kolona.
3. [`notebooks/03_krijimi_vetive_dhe_kodimi.ipynb`](notebooks/03_krijimi_vetive_dhe_kodimi.ipynb) — krijimi i vetive të reja, grupimi i llojit të pronës dhe i pajisjeve, diskretizimi, binarizimi dhe kodimi i kategorive. Lexon `listings_clean_full.csv` nga notebook-u 02 dhe krijon `listings_features.csv`.
4. [`notebooks/04_transformimi_dhe_reduktimi.ipynb`](notebooks/04_transformimi_dhe_reduktimi.ipynb) — asimetria, transformimi me logaritëm dhe rrënjë katrore, shkallëzimi min-max dhe z-score, zgjedhja e vetive me korrelacion dhe variancë, PCA dhe nënbashkësia finale. Lexon `listings_features.csv` dhe krijon `listings_transformed.csv` dhe `listings_model_ready.csv`.

Çdo notebook ka shpjegime në shqip dhe kode që mund të ekzekutohen qelizë pas qelize. Grafikët shfaqen brenda notebook-ut kur ekzekutohen qelizat; nuk ruhen si skedarë imazhi. Rezultatet dhe përfundimet e secilit hap janë shkruar brenda notebook-eve.

## Nisja

### Mjedisi

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

### Të dhënat

Projekti përdor tre skedarë të snapshot-it të Londrës (2026-09-17): `listings.csv.gz` (listimet), `reviews.csv.gz` dhe `calendar.csv.gz` (për integrimin në notebook-un 02). Shkarkojini në dosjen `dataset/` nga rrënja e projektit (`curl` është i disponueshëm edhe në Windows 10 e më të ri):

```bash
BASE=https://data.insideairbnb.com/united-kingdom/england/london/2026-09-17/data
curl -L -o dataset/listings.csv.gz $BASE/listings.csv.gz   # rreth 49 MB
curl -L -o dataset/reviews.csv.gz  $BASE/reviews.csv.gz    # rreth 287 MB
curl -L -o dataset/calendar.csv.gz $BASE/calendar.csv.gz   # rreth 82 MB
```

Skedarët e të dhënave nuk përfshihen në Git, sepse janë shumë të mëdhenj (GitHub nuk pranon skedarë mbi 100 MB); ata janë te `.gitignore`. Dataset-i origjinal nuk ndryshohet nga notebook-et.

### Ekzekutimi

Hapni notebook-et sipas rendit dhe zgjidhni kernel-in e mjedisit `.venv`. Ato gjejnë automatikisht `dataset/` kur kernel-i nis nga rrënja e projektit ose nga dosja `notebooks/`. Notebook-u 02 krijon `dataset/listings_clean_full.csv` (tabela e plotë e pastruar, hyrja e notebook-ut 03) dhe `dataset/listings_preprocessed.csv` (18 kolona për analizën). Notebook-u 03 krijon `dataset/listings_features.csv`, hyrjen e notebook-ut 04. Notebook-u 04 krijon `dataset/listings_transformed.csv` (me kolonat `_log`, `_sqrt`, `_minmax` dhe `_z`) dhe `dataset/listings_model_ready.csv` (nënbashkësia finale e vetive dhe komponentët e PCA). Të gjitha përjashtohen nga Git.

Rendi i ekzekutimit është 02 → 03 → 04, sepse secili lexon skedarin e krijuar nga i mëparshmi. Notebook-u 01 lexon vetëm dataset-in origjinal dhe mund të ekzekutohet më vete.

## Kufizime të metodës

- Rreshtat pa çmim largohen sepse çmimi është variabla kryesore; analiza e çmimit përfaqëson vetëm listimet me çmim të njohur.
- Vlerat e `bathrooms`, `bedrooms` dhe `beds` që mbeten bosh plotësohen me medianë sipas kapacitetit. Këto janë vlerësime, jo matje origjinale.
- Çmimet mbi percentilin 99.9 të secilit lloj dhome (59 listime) hiqen si të pabesueshme; ky kufi është statistikor, ndaj disa mund të ishin listime të vërteta luksoze. Çmimet mbi percentilin 99 të mbetur vetëm shënohen, nuk fshihen.
- `price_band` është krijuar nga çmimi. Nuk duhet përdorur si hyrje për një model që parashikon çmimin; për të njëjtën arsye duhen përjashtuar `price_quote_*` dhe `estimated_revenue_l365d` (saktësisht çmimi × zënia e vlerësuar).
- `review_scores_rating` mbetet bosh për listimet pa vlerësim. Kjo mungesë ka kuptim dhe nuk plotësohet artificialisht.
- Edhe `price_per_person` është nxjerrë nga çmimi. Përdoret vetëm për përshkrim dhe përjashtohet nga nënbashkësia finale.
- Flamujt e pajisjeve (`has_wifi`, `has_parking` etj.) gjenden me fjalë kyçe në tekstin e lirë të host-eve; shkrime të rralla mund të mos kapen.
- `borough_frequency`, min-max dhe z-score llogariten mbi të gjitha listimet, sepse qëllimi është përshkrues. Për një model, këto statistika llogariten vetëm në setin e trajnimit. Prandaj `listings_model_ready.csv` i ruan vetitë numerike të transformuara, por të pashkallëzuara.
- PCA përdor vetëm listimet me të gjitha vlerat numerike (47,317 nga 59,846). Listimet pa komente nuk kanë komponentë PCA.
- Kufijtë e zgjedhjes së vetive (|ρ| ≥ 0.8 për korrelacionin, mbi 98% për vlerën më të shpeshtë) dhe radha e kolonave brenda grupeve janë zgjedhje të zakonshme, jo rregulla absolute. Me kufij të tjerë, nënbashkësia do të ndryshonte pak.

## Kontribuesit

- [Alketa Zekaj](https://github.com/AlketaZekaj)
- [Yllka Berisha](https://github.com/yllkeberisha)
- [Zana Ademi](https://github.com/Zanaad)
