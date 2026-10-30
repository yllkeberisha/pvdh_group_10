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

**Integrimi:** u bashkuan `reviews.csv.gz` (numri dhe datat e komenteve; përputhen 100% me kolonat ekzistuese) dhe `calendar.csv.gz` (disponueshmëria e fundjavës; `calendar_available_days` përputhet me `availability_365` te 99.6% e listimeve). Asnjë listim nuk humbi. **Reduktimi i dimensionit:** u hoqën kolonat krejt bosh dhe për analizën u zgjodhën 18 kolona të lidhura me pyetjen kërkimore; zgjedhja me numra (korrelacione, PCA) pritet te notebook-u 04. **Transformimi:** tipet e çmimit, datave dhe fushave logjike u korrigjuan; kodimi 0/1, diskretizimi dhe vetitë e reja bëhen te notebook-u 03, ndërsa logaritmi dhe standardizimi pritet të bëhen te notebook-u 04.

**Strategjia për mungesat (notebook-u 02, seksioni 7.3):** tabela ka një rresht për çdo kolonë që kishte mungesa, 54 nga 93 kolonat (90 fillestare dhe 3 të krijuara nga integrimi): 14 u hoqën, 6 u plotësuan, te 10 mungesat ishin vetëm te rreshtat e hequr pa çmim dhe 24 u lanë bosh me qëllim, secila me arsyen e vet. Të tjerat 39 kolona nuk kishin mungesa dhe nuk kanë nevojë për vendim.

**Pjesa e Alketës (pastrimi, integrimi, mungesat, vlerat ekstreme).** Notebook-u 02 e kthen skedarin origjinal në një tabelë pa dublikatë dhe me çmim të vlefshëm, pa e ndryshuar atë. U integruan `reviews` dhe `calendar` me `id` (pa humbur asnjë listim), dhe mungesat e reja u trajtuan menjëherë. Listimet pa çmim u hoqën, sepse janë kryesisht jashtë shitjes (92.7% nga një mbledhje e vjetër, 87.3% pa ditë të lira kundrejt 0.5% te listimet me çmim); 2,587 listime me çmim por nga mbledhja e vjetër u mbajtën dhe u shënuan. Çmimet shumë ekstreme (mbi percentilin 99.9 të llojit të dhomës, 59 listime) u hoqën dhe ato mbi percentilin 99 u shënuan; `maximum_nights` u kufizua në 1,125, ndërsa anomalitë e tjera (`bedrooms` mbi `accommodates`, `host_listings_count`) u shënuan ose u dokumentuan pa u ndryshuar. Kufizim: plotësimet e `bathrooms`, `bedrooms` dhe `beds` janë vlerësime me medianë, dhe analiza e çmimit përfaqëson vetëm listimet me çmim të njohur.

Grafikët për mungesat, mostrën dhe çmimet shfaqen drejtpërdrejt në notebook-et pas ekzekutimit të qelizave përkatëse; nuk krijohen skedarë imazhi.
