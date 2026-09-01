# Rodada 6 — caça de SUBSTITUIÇÃO (diretiva: "substitua os artigos que não tiver acesso")

**2026-08-01** · professor cancelou a carta aos autores; a rota é substituir
fontes inacessíveis/deficientes por papers **OA com curvas digitalizáveis**
cobrindo os papéis que a fila precisa (réplicas M6–M8 · M16 amplitude baixa ·
Ti/superliga · espessura de membro). Varredura web + vetagem de figura na
página (lição do dia: resumo de modelo pequeno NÃO é leitura).

## ⭐ Candidato 1 — BAIXADO: Rousseau & Bouzid 2025 (Materials 18:462)

**"Effect of Clamped Member Material and Thickness on Bolt Self-Loosening
Under Transverse Loads"**, *Materials* 18(2):462, 2025-01-20, OA CC-BY,
DOI [10.3390/ma18020462](https://doi.org/10.3390/ma18020462), PMC11766740.
PDF: `pdfs_open_access/rousseau2025_materials_M12.pdf` (baixado via
browser+PoW; MDPI 403 no fetch direto e CORS no fetch da página).

- **É O MESMO GRUPO E RIG da nossa fonte ROUSSEAU** (ÉTS Montreal, M12×1,75,
  membros HDPE/aço) — extensão de um rig que JÁ modelamos com config
  adotado ⇒ candidato a **validação zero-refit** e a mais pontos para a
  forma `k_member_shear` (PR-14, item 10 do roadmap).
- Figuras com curvas (vetadas no HTML da página): Fig. 4 (HDPE por
  espessura — preload drop + rotação relativa), Fig. 5 (aço por
  espessura), Fig. 6 (HDPE vs aço 10 mm), Figs. 7–8 (perda por ponto de
  rigidez), **Fig. 9 (efeito da força transversal, 10/12 mm HDPE por
  faixa de ciclos)**, **Fig. 10 (efeito da amplitude, aço)**.
- ⚠️ Risco a resolver ANTES de registrar: **sobreposição com a fonte
  ROUSSEAU existente** (mesmos ensaios republicados? — precedente
  LU amp1p0≡T22). Mapear figura-a-figura contra os 6 CSVs atuais
  (hdpe/steel t10/t12/t14) ANTES de criar casos; o que for o MESMO teste
  fica fora do censo (piso de digitalização, não réplica).
- Próximo executor: extrair painéis (PyMuPDF 600 dpi), mapear, digitalizar
  o que for NOVO (Figs. 9–10 = varreduras de amplitude/força que não
  temos), registrar com prereg de round-trip (ferramental provado 3×).

## Candidatos 2–4 (vetados por título/abstract; PDF ainda não baixado)

| # | paper | papel | status |
|---|---|---|---|
| 2 | **Sensors 24(11):3306 (2024)** — "Prediction of Pre-Loading Relaxation of Bolt Structure ... under Tangential Cyclic Load" (OA) | relaxação sob carga tangencial — possível papel LIU_2025-adjacente | vetar figuras |
| 3 | **Materials 19(7):1414 (2026)** — "Behaviour of a Preloaded Asymmetric Multi-Bolted Connection Under Cyclic Loads" (OA) | multi-parafuso cíclico | ⚠️ provável grupo GRZEJDA (já na biblioteca) — dedupe primeiro |
| 4 | **Machines 13(2):80 (2025)** — "Bolt Loosening ... Sine-on-Random Coupling Vibration" (OA, M10) | vibração aleatória | **escopo duvidoso** (modelo é cíclico-determinístico) |

## Papéis ainda SEM candidato encontrado

- **Ti/superliga com réplicas** (papel CHU): nada OA com curvas repetidas
  achado nesta varredura (o rig GH159/GH4169 é nicho) — segue bancada.
- **M16 amplitude baixa com curvas densas** (papel LIU_2025): o único
  M16-sweep OA achado É o Liu 2025. Segue form-limited.

## Fontes descartadas na varredura (já na biblioteca)

Liu 2025 SciRep (é a nossa) · Yang 2019 S&V · companion IJPEM
(PMC11901137, só vidas) · Demir/Icmez EJRND (demir2024) · Sun EFA crimp
(sun2025) · JCSR 2023 anti-self-loosening (paywall e já catalogada).
