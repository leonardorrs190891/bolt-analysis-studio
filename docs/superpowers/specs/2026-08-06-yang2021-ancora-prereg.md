# Prereg — re-ancoragem das 6 digitalizações originais do YANG_2021

**2026-08-06** · decisão **D-U** (por delegação, MANDATO PERMANENTE) · classe
**dado**, molde D-S/D-R · gates escritos **antes da execução** (dry-run
permitido, escrita não). Fingerprint de partida `b70276f2fa43` (não muda — CSV
não entra no hash ⇒ validação por re-simulação, nunca por hash). Diagnóstico:
subagente da campanha FAXINA-E-ANATOMIA, tick 5 do ledger.

## O defeito, medido do VETOR (figuras são vetoriais: 12k–56k segmentos)

**As 6 digitalizações originais ancoram o 1º ponto (x=0) na BORDA SUPERIOR da
banda de oscilação** — duas delas 0,20–0,36 kN **acima do máximo desenhado** —
enquanto todos os demais pontos seguem o **CENTRO** da banda. Os traços
publicados começam em N≈100–750, não em N=0: o ponto x=0 é **extrapolação
inventada**. E o runner divide a curva pelo 1º ponto ⇒ cada curva carrega
deflação multiplicativa de **−2 % a −9,4 %**.

| CSV | âncora CSV(0) | topo da banda no início | centro |
|---|---:|---:|---:|
| fig2 | 14,50 | 14,30 (**+0,20 acima!**) | 13,38 |
| amp1p0 | 14,70 | 14,66 | 13,53 |
| amp0p8 | 14,50 | 14,14 (**+0,36 acima!**) | 13,52 |
| r1 | 14,30 | 14,36 | 13,82 |
| amp0p7 | 15,50 | 15,80 | 14,04 |
| amp0p5 | 15,00 | 15,14 | 14,74 |

`r2`/`r3` (digitalizadas 2026-07-31 com prereg) usam a convenção correta —
são os **controles bit-idênticos**. Item (e) da fila do professor respondido de
passagem: o 1º ponto da `amp0p7` (+9,93 %) **existe no impresso mas é topo de
banda** (banda = carga axial 11,2 kN transmitida, Φ≈0,15), não overshoot de
aperto. Segundo defeito na mesma curva: o meio do platô corre **+0,5 kN acima
do centro** (8 de 11 pontos, unilateral — classe CACCESE rep2); a
re-digitalização por centros o conserta por construção.

## Escopo

* Substituir **6 CSVs** (fig2_typical, amp1p0, amp0p8, r1, amp0p7, amp0p5)
  pelos **centros de banda** da extração vetorial
  (`vector_extractions/yang2021_fig2_fig6_vector.json`, preservada): grade x =
  a grade ANTIGA restrita a `[início visível do traço, xmax]` (predições foram
  medidas nesta grade — mesma razão do D-R), y = centro interpolado,
  normalizado pelo centro no 1º ponto da grade. **Sem x=0 inventado.**
* **Não tocar**: r2, r3 (controles), os 202 casos de outras fontes, configs.
* **Fora de escopo declarado**: envelope inferior como observável (precedente
  D-P `F_B,min`) — mudaria o observável, é outra decisão; oscilação/banda como
  dado (o modelo prevê médio/mínimo por ciclo, não a banda).

## Gates (IMUTÁVEIS)

- **G0 (instrumento):** extração vetorial com calibração por ticks (r²=1,0
  medido) e **atribuição DOCUMENTAL pelos rótulos de painel impressos**
  ("1.0–2" → amp1p0_ax2kN etc.), não por min-RMS — a matriz crua de RMS não é
  unívoca (amp0p7 e r2 colidem no mesmo traço por min-RMS bruto) e o rótulo
  impresso é identidade, não semelhança. RMS pós-shift vira **verificação**:
  todos ≤ 0,03 em F/F₀.
- **G1 (fidelidade, não-vácuo):** (a) o 1º x de cada CSV novo ≥ início visível
  do traço (**zero pontos inventados**); (b) todo y do CSV novo dentro da banda
  `[centro−meia-largura, centro+meia-largura]` do traço no mesmo x; (c) vidas
  CSV novo ↔ traço ≤ 1,3 % (já medido nos velhos; não pode piorar).
- **G2 (a métrica PODE piorar — e a predição registrada diz exatamente o quê):**

  | curva | store hoje (mae/mx/σ) | PREVISTO pós-conserto | leitura |
  |---|---|---|---|
  | fig2 | 0,099/0,163/0,060 | 0,061/0,197/0,061 | fora, viés flipa p/ + |
  | amp1p0 | 0,058/0,092/0,048 | 0,054/0,153/0,045 | fora (σ+mx) |
  | amp0p8 | 0,094/0,142/0,055 | 0,074/0,208/0,061 | fora, viés flipa |
  | **r1** | 0,027/0,042/0,022 | 0,026/**0,101**/**0,032** | **SAI do tripé** |
  | amp0p7 | 0,017/0,062/0,022 | **0,013/0,047/0,017** | melhora nas 3 pernas |
  | amp0p5 | 0,055/0,095/0,046 | 0,043/0,130/0,044 | fora (σ+mx) |

  **Custo declarado ANTES: censo 138→137** (r1 sai; rigor contra nós,
  precedente CACCESE — a curva estava dentro por artefato de âncora). As
  predições foram medidas na grade da métrica; o árbitro é a re-simulação.
  Tolerância da predição: ±0,02 por perna (acima disso ⇒ INCONCLUSIVO,
  investigar antes de adotar).
- **G3 (isolamento):** r2/r3 e TODAS as curvas de outras fontes bit-idênticas
  na re-simulação da fonte + fingerprint inalterado nos 210.
- **G5 (piso re-medido):** predição: MAE do piso da família 0,6 mm cai ~2×
  (estava inflado pela âncora), σ ≈ igual, `limite_sres` fica 0,025.
- **G6 (nota de aparato, mesmo commit):** (a) "overshoot 15,5 kN" → topo de
  banda de carga, não aperto; (b) gêmeos Fig. 6(a2)≡(a3) do próprio paper
  (centros idênticos a 0,036 kN, vidas iguais a 0,2 ciclo, larguras 2,4×
  diferentes — um rótulo errado na origem; não afeta o store, 0.8–4 nunca foi
  digitalizado); (c) fig2 é medição INDEPENDENTE de amp0p8 (fins 5980 vs 5655,
  offset +0,17 kN — não é duplicata), condição não-rotulada no paper.
- **G7 (sincronia):** store re-simulado (fonte inteira), reports, censo, docs
  vivos e testes no MESMO commit da execução.

### Ramos

- **ADOTA** — G0/G1/G3 passam e as predições ficam na tolerância. A piora de
  curvas e a saída da r1 NÃO reprovam (G2 declarado).
- **INCONCLUSIVO** — predição erra >±0,02 em alguma perna: parar e investigar
  (instrumento ou leitura), sem escrever.
- **NÃO ADOTA** — G1 falha (fidelidade irrecuperável).

## ⚠️ EMENDAS de instrumento, declaradas no DRY (antes de qualquer escrita)

O dry-run reprovou 4/6 no G0 como escrito, e a reprovação era do **instrumento**,
três vezes:

1. **Unidades**: a checagem de banda comparava CSV adimensional com centros em
   kN (100 % "fora da banda", absurdo). Corrigido para espaço normalizado pelo
   mesmo anchor.
2. **Janela**: meu RMS varria a curva inteira **incluindo o colapso**, onde
   ruído de x numa curva quase-vertical vira erro gigante de y; o RMS do
   diagnóstico (0,0015–0,0293) era no **platô**.
3. **ESTRUTURAL, e vale para a campanha**: RMS contra o CSV velho **não pode
   gatear atribuição** — ele não separa "traço errado" de "traço certo,
   digitalização ruim", porque nas curvas piores o defeito é grande **por
   definição** (a amp0p7 tem o meio do platô correndo pela borda: desvio
   concentrado que sobrevive à remoção de translação). Atribuição exige
   evidência de **identidade independente do arquivo defeituoso**: (i) rótulo
   de painel impresso (documental); (ii) **vida** do traço vs CSV (≤3 %;
   medido 0,003–0,010); (iii) **ini_max** do traço contra a tabela do
   diagnóstico (±0,05 kN; 6/6 exatos). O RMS de forma vira informação impressa.

Nenhuma emenda afrouxa barra: as três trocam um gate que media a coisa errada
por gates que medem identidade. Resultado do dry final: **G0 PASSA · G1 PASSA**,
zero escritas.

## O que este conserto NÃO faz

Não fecha nenhuma curva nova (amp0p5/amp1p0 continuam fora — a anatomia sob
dado fiel CONFIRMA o rótulo classe_parada delas: σ manda, aceleração tardia; o
"nível" do mapa era artefato de âncora). É sobre **estar certo**: viés honesto
com sinal correto nas 6, piso de réplica honesto, e a exceção F5 §C das duas
grandes fica **mais** justificada, não menos.
