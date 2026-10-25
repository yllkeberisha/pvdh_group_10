# London Airbnb Listings · Para-procesimi (Pjesa I)

Ky projekt analizon si ndryshon çmimi për natë i listimeve Airbnb në Londër sipas llojit të dhomës, lagjes dhe kapacitetit. Burimi i deklaruar është Inside Airbnb; një rresht përfaqëson një listim. Dataset-i lokal është `dataset/listings.csv.gz` (nuk ruhet në Git). Para dorëzimit, shtoni në raport datën dhe lidhjen e saktë të shkarkimit të versionit që përdorni.

## Notebook-et

1. [`notebooks/01_inspektimi_dhe_kualiteti.ipynb`](notebooks/01_inspektimi_dhe_kualiteti.ipynb) — mbledhja dhe kuptimi i të dhënave, tipet, kualiteti, mungesat, dublikatat, agregimi dhe mostrimi.
2. [`notebooks/02_pastrimi_dhe_transformimi.ipynb`](notebooks/02_pastrimi_dhe_transformimi.ipynb) — pastrimi, strategjia për mungesat, vlerat ekstreme, zgjedhja/krijimi i vetive, diskretizimi, binarizimi, transformimi dhe krahasimi para/pas.

Çdo notebook ka shpjegime në shqip dhe kode që mund të ekzekutohen qelizë pas qelize. Grafikët shfaqen brenda notebook-ut kur ekzekutohen qelizat; nuk ruhen si skedarë imazhi. Rezultatet kryesore të ekzekutimit aktual janë te [`reports/preprocessing_summary.md`](reports/preprocessing_summary.md).

## Nisja

Nga rrënja e projektit, me Python 3.10 ose më të ri:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m jupyter lab
```

Hapni notebook-et sipas rendit dhe zgjidhni kernel-in e mjedisit `.venv`. Ato gjejnë automatikisht `dataset/` kur kernel-i nis nga rrënja e projektit ose nga dosja `notebooks/`. Notebook-u 02 krijon `dataset/listings_preprocessed.csv`, i cili përjashtohet nga Git. Dataset-i origjinal nuk ndryshohet.

Skriptet ekzistuese në `scripts/` mbeten si rrjedhë alternative. Raporti i vjetër `reports/listings_cleaning.txt` u krijua nga një version tjetër i dataset-it (77,679 rreshta), ndaj **mos i përdorni numrat e tij** për versionin aktual me 91,954 rreshta. Për rezultatet e kësaj pjese përdorni notebook-et dhe `reports/preprocessing_summary.md`.

## Kufizime të metodës

- Rreshtat pa çmim largohen sepse çmimi është variabla kryesore; analiza e çmimit përfaqëson vetëm listimet me çmim të njohur.
- Vlerat e `bathrooms`, `bedrooms` dhe `beds` që mbeten bosh plotësohen me medianë sipas kapacitetit. Këto janë vlerësime, jo matje origjinale.
- Çmimet mbi percentilin 99 vetëm shënohen, nuk fshihen; mund të përfshijnë listime të vërteta luksoze.
- `price_band` është krijuar nga çmimi. Nuk duhet përdorur si hyrje për një model që parashikon çmimin.
- `review_scores_rating` mbetet bosh për listimet pa vlerësim. Kjo mungesë ka kuptim dhe nuk plotësohet artificialisht.
