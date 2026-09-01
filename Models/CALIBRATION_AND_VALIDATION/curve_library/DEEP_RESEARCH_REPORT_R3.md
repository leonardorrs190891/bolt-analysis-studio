# Rodada 3 — busca de novas fontes (2026-07-02)

Rodada focada nas lacunas apontadas pela R2: reaperto/embedding-renewal, creep/termico,
locking devices, e novas fontes transversais 2020-2026. Os candidatos abaixo foram
verificados via Crossref/Unpaywall/busca web; **nenhum e open-access baixavel por bot**
(SAGE/ScienceDirect/Wiley bloqueiam fetch automatizado) — todos vao para a lista de
download manual via acesso institucional (Scopus/ScienceDirect/Springer do usuario).

## Candidatos qualificados (download manual)

| # | Paper | DOI | Lacuna | Por que vale |
|---|---|---|---|---|
| 1 | **"The effect of tightening again on bolt loosening under transverse load: Experimental and finite element analysis"**, *Structures* 45 (2022) | [10.1016/j.istruc.2022.08.049](https://doi.org/10.1016/j.istruc.2022.08.049) | **reaperto** (next-priority #5: embedding renewal) | Curvas F-N experimentais apos reapertos sucessivos; reporta que apos o 3o reaperto o afrouxamento acelera e no 4o a forca colapsa — exatamente o comportamento reaperto/TP7 que o surface_damage D captura. Melhor alvo novo da rodada. |
| 2 | **"A combined theoretical and experimental study on contact creep-induced clamping force relaxation of bolted joints at ambient temperature"**, *Marine Structures* (2022) | [10.1016/j.marstruc.2022.103263](https://doi.org/10.1016/j.marstruc.2022.103263) | **creep** (cauda k_creep sem fonte dedicada) | Relaxacao por creep de contato SEM vibracao a temperatura ambiente — isola `k_creep_scale`/Norton do resto. |
| 3 | **"Research on bolt pre-tightening and relaxation mechanism under transverse load"**, *Advances in Mechanical Engineering* 12(12) (2020) | [10.1177/1687814020975919](https://doi.org/10.1177/1687814020975919) | transversal + relaxacao | Gold OA (SAGE), mas host bloqueia bots — baixar manualmente no navegador (gratuito). |
| 4 | **"Review on anti-loosening methods for threaded fasteners"**, *Chinese Journal of Aeronautics* 35(2) (2022) | [10.1016/j.cja.2020.12.038](https://doi.org/10.1016/j.cja.2020.12.038) | locking devices (referencia) | Gold OA no ScienceDirect (bloqueado p/ bot; gratuito no navegador). Compila curvas Junker de multiplos dispositivos — bom p/ `locking_device_type`. |
| 5 | **"Effect of frequency on the fatigue performance of bolted joints under axial excitation"**, *Tribology International* 176:107933 (2022) | [10.1016/j.triboint.2022.107933](https://doi.org/10.1016/j.triboint.2022.107933) | axial + frequencia | Completa o trilho axial de Liu 2017 com o eixo frequencia (Li et al., mesmo grupo). |
| 6 | **"Time–temperature-dependent response and analysis of preload relaxation in bolted composite joints"** (2018) | ver Crossref | termico/composito | Curvas de relaxacao F(t) vs temperatura p/ juntas compositas. |
| 7 | **Tong 2024, "Preload relaxation behavior... CFRTP-SMC joints"**, *Polymer Composites* | [10.1002/pc.28378](https://doi.org/10.1002/pc.28378) | termico/composito | Relaxacao vs temperatura e preload inicial, 240 h. |

## Ja pendente da Rodada 1

- **Yang/Jeong/Lim 2023, IJPEM** [10.1007/s12541-023-00783-x](https://doi.org/10.1007/s12541-023-00783-x)
  (Springer, paywall) — unico item do checklist original ainda nao baixado.

## Nota de execucao

A rodada 3 foi executada de forma reduzida (limite de gasto da org atingiu os agentes de
busca em paralelo); as queries cobriram: transversal/Junker 2020-2026, reaperto/embedding
renewal, creep/termico, locking devices (Nord-Lock/serrilhada), axial. Uma varredura
adicional (Scopus institucional, por citacao dos 10 papers-base) pode render mais fontes —
sugerida como rodada 4 manual.
