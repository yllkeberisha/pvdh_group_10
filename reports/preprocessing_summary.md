# Përmbledhje e para-procesimit · London Airbnb

Rezultatet më poshtë janë nxjerrë nga `dataset/listings.csv.gz` me notebook-et e Pjesës I. Ekzekutimi përdor skedarin aktual lokal; nëse ai ndryshon, ekzekutoni notebook-et sërish.

**Burimi:** Inside Airbnb, Londër, snapshot 2026-09-17: `listings.csv.gz` (91,954 rreshta × 90 kolona), `reviews.csv.gz` (2,323,969 komente) dhe `calendar.csv.gz` (33,563,890 rreshta, një për listim dhe ditë). Lidhjet: `https://data.insideairbnb.com/united-kingdom/england/london/2026-09-17/data/` + emri i skedarit.

| Treguesi | Fillimi | Tabela e analizës |
|---|---:|---:|
| Rreshta | 91,954 | 59,846 |
| Kolona | 90 | 18 |
| Qeliza boshe | 1,933,263 | 12,226 |
| Rreshta identikë | 0 | — |
| ID të përsëritura | 0 | 0 |

**Gjetjet dhe vendimet**

1. Nga 15 kolona plotësisht bosh, 14 u hoqën. `bathrooms` u ruajt dhe u rindërtua nga `bathrooms_text`.
2. `price` ishte tekst i formatuar. Ai u kthye në numër; 32,049 listime pa çmim u hoqën nga analiza e çmimit. Nuk u gjetën çmime jo pozitive pas konvertimit.
3. Mungesat e mbetura në `bathrooms`, `bedrooms` dhe `beds` u plotësuan me medianën e grupit me të njëjtin `accommodates`, pastaj me medianën e përgjithshme.
4. U hoqën 59 çmime mbi percentilin 99.9 të llojit të dhomës (asimetria e çmimit ra nga 62.7 në 8.3). U krijuan `has_reviews`, `is_superhost`, `amenity_count`, `price_band` dhe një shenjë për çmimin mbi percentilin 99. Ky kufi është 1,203.38; 599 listime janë mbi të. Ato u ruajtën.
5. Tabela e zgjedhur për analizë ka 18 kolona. Mungesat e saj janë vetëm 12,226 vlera të `review_scores_rating`, të lëna bosh me qëllim. Listimet pa komente nuk kanë rezultat vlerësimi.
6. Si agregim përshkrues, çmimi median është 226.67 për `Entire home/apt` (40,481 listime), 187.50 për `Hotel room` (134), 80.00 për `Private room` (19,067) dhe 35.71 për `Shared room` (164).
7. Mostra eksploruese 10% sipas `room_type` ka 9,195 rreshta. Rezultati final përdor të gjitha 59,846 listimet me çmim të vlefshëm.
8. **Transformimi.** `price_log = log1p(price)` ul asimetrinë e çmimit nga 8.31 në 0.31. `log1p` u zbatua edhe te 20 kolona të tjera shumë asimetrike, pastaj kolonat e vazhdueshme u standardizuan (z-score).
9. **Zgjedhja e nënbashkësisë.** Nga 53 veti numerike u hoqën 4 kopje të sakta, 5 kolona pothuajse konstante (një vlerë në të paktën 95% të rreshtave) dhe 15 të përsëritura (korrelacion mbi 0.8). Mbeten 29: 26 të vazhdueshme dhe 3 me vlera 0/1. `estimated_revenue_l365d` u përjashtua, sepse është saktësisht `price` × `estimated_occupancy_l365d`.
10. **Reduktimi i dimensionit.** PCA mbi 19 veti pa mungesa: 13 përbërës mbajnë 91.9% të variancës. Tre të parët janë aktiviteti i komenteve (21.0%), madhësia e listimit (13.5%) dhe përvoja e host-it (9.7%).
11. **Rezultati për përdorim të mëtejshëm:** `dataset/listings_model_ready.csv`, me 59,846 rreshta × 47 kolona (`id`, `price`, `price_log`, `room_type`, `neighbourhood_cleansed`, 26 kolona `z_*`, 3 kolona 0/1 dhe `pc1`…`pc13`). Kolonat shpjegohen te seksioni 11 i notebook-ut 02; `id` e lidh me `listings_features.csv` të notebook-ut 03.

**Integrimi:** u bashkuan `reviews.csv.gz` (numri dhe datat e komenteve; përputhen 100% me kolonat ekzistuese) dhe `calendar.csv.gz` (disponueshmëria e fundjavës; `calendar_available_days` përputhet me `availability_365` te 99.6% e listimeve). Asnjë listim nuk humbi. **Reduktimi i dimensionit dhe zgjedhja e vetive:** seksionet 9 dhe 10 të notebook-ut 02 (zgjedhje me rregulla, pastaj PCA); tabela me 18 kolona shërben vetëm për leximin dhe agregimet. **Transformimi:** tipet e çmimit, datave dhe fushave logjike u korrigjuan; logaritmi dhe standardizimi bëhen te seksioni 8; kodimi 0/1 i kategorive, diskretizimi dhe vetitë e tjera të reja bëhen te notebook-u 03.

**Kufizim për modelim:** logaritmi, standardizimi, zgjedhja e vetive dhe PCA janë llogaritur mbi të gjitha rreshtat. Një model me ndarje trajnim/test duhet t'i përsërisë mbi setin e trajnimit.

Grafikët për mungesat, mostrën, çmimet dhe PCA shfaqen drejtpërdrejt në notebook-et pas ekzekutimit të qelizave përkatëse; nuk krijohen skedarë imazhi.
