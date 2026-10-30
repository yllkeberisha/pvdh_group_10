# Përmbledhje e para-procesimit · London Airbnb

Rezultatet më poshtë janë nxjerrë nga `dataset/listings.csv.gz` me notebook-et e Pjesës I. Ekzekutimi përdor skedarin aktual lokal; nëse ai ndryshon, ekzekutoni notebook-et sërish.

| Treguesi | Fillimi | Tabela e analizës |
|---|---:|---:|
| Rreshta | 91,954 | 59,905 |
| Kolona | 90 | 18 |
| Qeliza boshe | 1,933,263 | 12,258 |
| Rreshta identikë | 0 | — |
| ID të përsëritura | 0 | 0 |

**Gjetjet dhe vendimet**

1. Nga 15 kolona plotësisht bosh, 14 u hoqën. `bathrooms` u ruajt dhe u rindërtua nga `bathrooms_text`.
2. `price` ishte tekst i formatuar. Ai u kthye në numër; 32,049 listime pa çmim u hoqën nga analiza e çmimit. Nuk u gjetën çmime jo pozitive pas konvertimit.
3. Mungesat e mbetura në `bathrooms`, `bedrooms` dhe `beds` u plotësuan me medianën e grupit me të njëjtin `accommodates`, pastaj me medianën e përgjithshme.
4. U krijuan `has_reviews`, `is_superhost`, `amenity_count`, `price_band` dhe një shenjë për çmimin mbi percentilin 99. Ky kufi është 1,272.16; 600 listime janë mbi të. Ato u ruajtën.
5. Tabela e zgjedhur për analizë ka 18 kolona. Mungesat e saj janë vetëm 12,258 vlera të `review_scores_rating`, të lëna bosh me qëllim. Listimet pa komente nuk kanë rezultat vlerësimi.
6. Si agregim përshkrues, çmimi median është 227.00 për `Entire home/apt` (40,521 listime), 187.50 për `Hotel room` (134), 80.00 për `Private room` (19,085) dhe 36.00 për `Shared room` (165).
7. Mostra eksploruese 10% sipas `room_type` ka 9,195 rreshta. Rezultati final përdor të gjitha 59,905 listimet me çmim të vlefshëm.

**Integrimi:** nuk u bë bashkim tabelash, sepse ky projekt aktualisht ka vetëm një dataset. **Reduktimi i dimensionit:** u hoqën kolonat krejt bosh dhe për analizën u zgjodhën 18 kolona të lidhura me pyetjen kërkimore. **Transformimi:** tipet e çmimit, datave dhe fushave logjike u korrigjuan; kodimi 0/1, standardizimi dhe transformimet e tjera bëhen te notebook-et 03 dhe 04, jo te notebook-u 02.

Grafikët për mungesat, mostrën dhe çmimet shfaqen drejtpërdrejt në dy notebook-et pas ekzekutimit të qelizave përkatëse; nuk krijohen skedarë imazhi.
