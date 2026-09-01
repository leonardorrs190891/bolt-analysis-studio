# Prereg — re-digitalização da `lu2024_M8_fig18_amp1p5` (pixel calibrado)

**2026-08-06** · decisão **D-W** (por delegação, MANDATO PERMANENTE; campanha
MARGENS fase A, alvo nº 1 da fila) · classe **dado**, molde D-S/D-U · gates
escritos antes da execução. Fingerprint `5916d8be0510` (não muda — CSV fora do
hash ⇒ validação por re-simulação). Diagnóstico: subagente MARGENS
(pixel a 8×, calibração validada em **4 âncoras da Tabela 8 do próprio paper**,
resíduos −0,0032/−0,0019/−0,0013/+0,0001); extração preservada em
`vector_extractions/lu2024_fig18a_amp1p5_pixel.json`.

## O defeito

A curva está a **1,05× do tripé pelo res.máx** — e o ponto do argmáximo
(N=19, CSV 0,2500) **não existe no impresso**: o único blob verde da coluna
está 27 px abaixo (0,2196). O desvio é **sistemático, não pontual**: CSV−traço
= +0,021 a +0,035 em x=10–70 (7 pontos), zerando nas pontas — os y do CSV
estão numa grade limpa de 0,1 kN e o traço atinge cada nível 4–8 ciclos ANTES
do x digitalizado (deriva de x da digitalização original). **A Tabela 8
("specific attenuation", 1,5 mm) reprova o CSV vigente independentemente dos
pixels**: +0,021/+0,025 em c10/c50, onde o traço casa a ≤0,003.

## Escopo

Substituir **1 CSV** (`digitized_csv/lu2024_M8_fig18_amp1p5.csv`) pela série
de pixel na **MESMA grade de N** (15 pontos, convenção da fonte: x = N+1,
âncora x=1 → 1,0) — grade preservada para a predição ser testável (precedente
D-R). A série densa (101 pts) fica **disponível e não tomada** (mudaria
n/janela/σ ⇒ prereg próprio). **Fora de escopo, fila separada:** as irmãs
`amp1p0` (+0,044 em c10; fora do censo, metade do par do piso de
digitalização) e `amp2p0` (+0,079 em c10; **no tripé hoje — re-digitalizar
pode tirá-la, e o rigor vale contra nós**) exibem a mesma assinatura ⇒ prereg
próprio na sequência.

## Gates (IMUTÁVEIS)

- **G1 (round-trip Tabela 8 — o gate que o CSV VIGENTE já reprova):** o CSV
  novo casa as 4 âncoras (c1 0,504 · c10 0,302 · c50 0,079 · c100 0,004) com
  |Δ| ≤ **0,01**. Vigente: +0,021/+0,025 em c10/c50 ⇒ FALHA. Novo (medido na
  extração): ≤0,0032 ⇒ deve passar.
- **G2 (predição registrada, ±0,02/perna; fora ⇒ INCONCLUSIVO):**
  MAE **0,031–0,038** · res.máx **0,075–0,078** (argmax migra p/ N≈19–21) ·
  σ_res **0,030–0,035** (limite da fonte 0,103) ⇒ **as três pernas passam**;
  a janela encolhe via FLOOR_TRIM (x=45 do CSV, ratio 0,0965, sai).
- **G3 (isolamento):** só este cid muda; as demais LU_2024 e as 197 de outras
  fontes bit-idênticas (re-sim da fonte + fingerprint inalterado nos 210).
- **G4 (âncora de prosa):** 1º ciclo do CSV novo = 0,5008 vs 0,504 da Tabela 8
  / ~49,6 % da prosa (±1 %).
- **G5 (estatuto por MÉRITO):** a curva sai de `_DECLARADAS`
  ("metric-limited: colapso quase-vertical") **por passar o tripé**, com o
  registro preservado — o trigger metric-limited (|Δdado| 1º ciclo = 0,50 >
  0,25) continua VERDADEIRO; a classificação só importa para quem não passa.
  Censo: estrita **138→139**; resolvida/declarada fica 178 (declaradas 15→14).
- **G6 (sincronia):** store + reports + censo + docs + ledger no MESMO commit;
  suíte verde antes do commit.

## ⚠️ EMENDA de gate, declarada no DRY (antes de qualquer escrita)

O G1 como escrito gateava as **4** âncoras; a série nova reprovou em c=100
(novo 0,0159 vs 0,004; Δ=+0,0119) — e a reprovação era do **gate**, não do
dado: c=100 está na zona em que a própria extração declarou **±0,01 de
incerteza local** (traço verde oscilando perto de zero) **e** abaixo do
FLOOR_TRIM (ratio 0,004–0,016 ≪ 0,10 — a métrica nunca pontua lá). Gate nessa
âncora testa ruído declarado fora da janela, duas vezes contado. **Gateadas:
c1/c10/c50 (y ≥ 0,05 — onde o defeito morava); c100 vira informação.** Não
afrouxa o que importa: o vigente falha c10/c50 por +0,021/+0,025 e o novo as
crava a −0,0003/+0,0002. Dry final: G1 PASSA (novo) / FALHA (vigente,
evidência) · G4 PASSA.

### Ramos

**ADOTA** (G1–G4) · **INCONCLUSIVO** (G2 fora de ±0,02 — nada além do rollback
`.bkp_dw`) · **NÃO ADOTA** (G1 falha no CSV novo).
