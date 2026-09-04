# Diagnóstico dos marginais maxerr>0.1 (tratáveis de baixo rendimento)

Data: 2026-07-15. Tarefa 100% leitura: resultados canônicos do
`validation_store.json` (fingerprints `45d809ef`/`403470cb`; engine atual
`ff54f04d` — sem re-fit) + CSVs da biblioteca com a convenção exata do runner
(`csv_x_offset`/`csv_x_scale`, trim `ratio<0.10`, normalização e alinhamento do
modelo no 1º ciclo do dado). Resíduo assinado = modelo − dado nos pontos do
dado. Única re-simulação: `li2022ti_axialmin_10Hz` (verificação de paridade —
a curva decimada do store, 400 pts/200k ciclos, distorce o alinhamento em
N=200; a re-sim reproduziu o store bit-a-bit: mae 0.0886, maxerr 0.1119).
Pré-registros consultados: `docs/superpowers/specs/2026-07-11-mem-iter4-preregistrations.md`
(PR-11/11b/12…12g/14/19/20/22/36 e síntese de quase-estacionariedade).

Classes: **(a)** knob-alcançável (alavanca existente, com leitura concreta) ·
**(b)** forma-limitada · **(c)** artefato de dado.

---

## bauer2024_M8_fig6_rep1 — maxerr 0.1259 @N=126 (fim do eixo), sinal −

mae 0.0431; meio N20–52 res≈0 (o `tr_loose_gain=2.2` per-espécime do PR-22
acerta o corpo da curva); de N56 em diante o kernel torque-runaway acelera e o
modelo chega ao piso (0.05) cedo: modelo 0.06 vs dado 0.19 no último ponto
mantido (o dado segue caindo abaixo de 0.10 — 1 pt trimado, não há platô a
ler). Reduzir o gain conserta a cauda mas quebra o meio (o min-max já foi
feito; PR-22 eliminou a divergência oposta +0.34 do kernel linear).
**Classe (b) forma-limitada** — cauda quase-linear do dado vs runaway
acelerante; per-espécime já gasto. Rótulo: classe kernel (fila consolidada).

## bauer2024_M8_fig6_rep4 — maxerr 0.1709 @N=190 (frac 0.89), sinal −

mae 0.0783; forma em S dos dois lados: modelo lento no 1º semieixo (+0.11
@N52) e rápido no 2º (−0.15 @N164–202); atinge o floor 0.05 em N≈190 enquanto
o dado só cruza 0.10 em N≈220–230 (3 pts trimados). Dado ~linear; kernel único
não faz meio E cauda. Já rotulado no pré-registro (síntese 2026-07-15):
"modelo chega ao floor cedo demais" = **CLASSE TERMINAL**
(mergulho/aproximação suave). **Classe (b) forma-limitada** — sem knob; entra
na decisão de kernel desacelerante da fila.

## bauer2024_M8_fig6_rep5 — maxerr 0.1116 @N=231 (frac 0.95), sinal −

mae 0.0494; mesma assinatura de rep1/rep4 atenuada: +0.07 no meio (N27),
−0.10 na cauda (N229; modelo 0.08 vs dado 0.18; dado segue <0.10, 1 pt
trimado). N75 dado 72 vs modelo 86. Marginal (0.11, logo acima da barra) e
irredutível pelo mesmo motivo: gain per-espécime (1.6) já centrado no meio;
acelerar quebra o corpo. **Classe (b) forma-limitada** — scatter de ensemble
sobre kernel único (mesma família rep1/rep4).

## bauer2024_M8_fig6_rep6 — maxerr 0.1300 @N=171 (frac 0.57, MEIO), sinal +

mae 0.0757; extremos pinados (res final +0.005; N300 modelo 0.18 = dado 0.18)
e bolha positiva no meio inteiro (+0.08…+0.13, N55–239): dado LINEAR, kernel
torque faz S (lento no meio, rápido no fim). Documentado 2× no pré-registro:
PR-12g (kernel linear fechou rep6 em 0.126 mas divergia rep1) e PR-22 ("dois
regimes de colapso; kernel único não faz os dois"). **Classe (b)
forma-limitada** — regime linear×runaway do ensemble; não repropor kernel
linear nem per-espécime extra.

## bauer2024_M12_fig8_test2 — maxerr 0.1795 @N=1162 (último ponto), sinal −

mae 0.0290; joelho CASADO (N75 dado 736 vs modelo 731 — o espectro lido
18×80+2×155 µm + `k_loose_graded=0.03` min-max do PR-12e acertam o timing);
a divergência é só a taxa pós-joelho: modelo colapsa ~1.7× mais rápido
(0.00136 vs 0.00081/ciclo) → fim 0.32 vs 0.50. test3 diverge no sentido
OPOSTO com o mesmo k ⇒ scatter do ensemble em torno do k compartilhado; k
per-teste = o overfit que o PR-12e rejeitou. **Classe (b) forma-limitada** —
"joelho de espectro" (já classificada; 3 fig8 na fila).

## bauer2024_M12_fig8_test3 — maxerr 0.1198 @N=1140 (último ponto), sinal +

mae 0.0241; espelho do test2: joelho do modelo atrasado (N75 741 vs dado 667)
e cauda mais lenta (fim modelo 0.36 vs dado 0.24; +0.12). Corpo da curva
excelente (|res|≤0.02 até N≈800). Sinais opostos test2/test3 sob config única
= scatter de timing do joelho, não viés sistemático. **Classe (b)
forma-limitada** — mesma classe do test2 (joelho de espectro, min-max
centrado no ensemble).

## rousseau2025_steel_t10 — maxerr 0.1881 @N=170 (fim), sinal +

mae 0.0866; dupla falha de forma: modelo RÁPIDO no início-meio (−0.07…−0.08,
N20–100; N75 modelo 70 vs dado 87 — assentamento front-loaded) e TRAVADO no
fim: dado mergulha (0.137, ainda caindo; 1 pt <0.10 trimado) enquanto o
modelo desacelera para 0.325 (+0.19). Já rotulado TERMINAL no pré-registro
("dado MERGULHA no fim, modelo trava — runaway grip-dependente #10").
`c_bend=0.3` per-rig e emb 1.0 µm (PR-25) já lidos/ajustados. **Classe (b)
forma-limitada/terminal** — mergulho não representado; fila do kernel.

## rousseau2025_hdpe_t10 — maxerr 0.1529 @N=145 (frac 0.36, MEIO), sinal +

mae 0.0579; extremos pinados (fim −0.013; floor 0.2 do grupo ≈ platô do dado
0.212 — leitura de floor já correta) e bolha no meio (+0.11…+0.15, N115–190):
o estágio médio do dado é mais íngreme que o kernel CM desacelerante; o
modelo recupera no fim. Níveis já fechados pelo PR-14 (amplitude da Tabela 2 +
GA_member); resta a forma do meio. **Classe (b) forma-limitada** (aproximação
suave/joelho de meio) com sub-alavanca marginal: re-grid min-max do
`tr_loose_gain`/`c_bend` do grupo ROUSSEAU_HDPE pontuando o MEIO (ganho
~0.03–0.05; gates PR-14: finais/ordem t10<t12<t14 e t14 intactos). Contexto:
par polimérico — fora do domínio metálico declarado (caveat registrado).

## rousseau2025_hdpe_t12 — maxerr 0.1375 @N=250 (frac 0.62), sinal +

mae 0.0642; mesma assinatura do t10 deslocada para a direita: meio +0.09…+0.14
(N160–285), fim −0.020 (modelo 0.301 vs dado 0.321, floor não-vinculante).
Qualquer aceleração do grupo que feche o meio do t10/t12 derruba a cauda do
t12 (res final já levemente negativo) — é o mesmo trade-off de forma.
**Classe (b) forma-limitada** — idem t10 (aproximação suave; mesma
sub-alavanca marginal de grupo, mesmo risco).

## karlsen2022_M30_HVtorqued_run14p2 — maxerr 0.2363 @N=269 (fim), sinal +

mae 0.0898; início casado (−0.01 @N49) e défice CRESCENTE: a taxa do dado
ACELERA 2.7× ao longo do ensaio (0.0016→0.0043/ciclo) enquanto o modelo fica
~plano (0.0016→0.0025) → fim modelo 0.48 vs dado 0.24. Um dreno linear
(k_ratchet per-espécime, classe run7p1/run2p2) desloca o nível mas NÃO produz
aceleração — quebraria o início casado sem fechar a cauda (por isso o
pré-registro o rotulou TERMINAL, "mergulho", junto com steel_t10, e não deu
exceção). **Classe (b) forma-limitada/terminal** — colapso acelerante
não-runaway; fila do kernel.

## karlsen2022_M42_HV_run20p0 — maxerr 0.1235 @N=339 (fim), sinal +

mae 0.0443; aqui o défice de taxa é QUASE-CONSTANTE (~15%: dado
0.0018→0.0030, modelo 0.0020→0.0024/ciclo), N75 casa (122 vs 127) e o resíduo
cresce ~linear até +0.12 — assinatura de dreno linear faltante, a mesma dos
run7p1/run2p2 (exceções per-espécime k_ratchet 0.005/0.003 já autorizadas
2×). **Classe (a) knob-alcançável**: exceção per-espécime
`KARLSEN_2022_run20p0` com `k_ratchet≈0.001` (gap 0.12 ≈ ⅓ do gap que
k=0.003 fechou no run2p2); gate: 10 demais Karlsen bit-idênticos. Caveat: a
assinatura na janela cedo é fraca (res +0.01 @N119) — a leitura preditiva
à PR-11b tem pouco poder aqui; se não predizer, rotular scatter HV.

## li2022ti_axialmin_10Hz — maxerr 0.1119 @N=200000 (fim), sinal +

mae 0.0886, resid_std 0.034 (≈offset). Alinhado em N=200, o modelo fica ACIMA
e mais PLANO que o dado: perde 6.7% de N200→200k vs 17.9% do dado. O erro é
ordenado por frequência (10Hz 0.112 > 15Hz 0.075 > 20Hz 0.024) e o dado perde
MAIS a menos freq (finais 0.821/0.858/0.911) com durações 20000/9333/4000 s ⇒
canal de TEMPO/dwell que o modelo sub-representa (grupo `LI_2022_TRIBOINT`
com cfg VAZIO — roda default+shared; C_creep da âncora interna é por-par, §4.7, e este par
é Ti). Nota: emb data-implied 2.47 µm vs VDI 9.5 µm existe, mas o alinhamento
em N=200 absorve o nível — NÃO é a alavanca (não repropor o emb do PR-20
aqui). **Classe (a) knob-alcançável (baixo rendimento)**: `C_creep` per-par
fitado-this-rig no grupo (curvas CHEIAS, precedente do bloco axial
2026-07-08) ou adoção do `fret_freq_exp` (capability default-inerte) com
f_ref ancorado no 20Hz; gate: 15/20Hz não pioram (>0.01).

## yang2019_M10_varamp_small_to_large — maxerr 0.2125 @N=3800 (fim), sinal +

mae 0.0686; o runner alimenta 0.5 mm CONSTANTE, mas o ensaio é de BLOCOS
crescentes (Fig 10): o dado fica chato no(s) bloco(s) pequeno(s) (0.98@200 →
0.87@3000; modelo −0.09 já em N200) e despenca no bloco grande final
(0.84→0.65 após N≈3300; raw até 0.073, 1 pt trimado) que o modelo não tem
(0.86 flat → +0.21). **Classe (a) input-alcançável**: `delta_spectrum` lido
da Fig 10 do PDF (maquinaria PR-12 já no runner; blocos one-shot cobrindo
n_max) em grupo `YANG_2019_varamp_small_to_large`; zero constante nova; gate:
3 casos constantes YANG_2019 bit-idênticos. Caveats: (c) parcial — CSV começa
em 1.085 (banda de overshoot de aperto; âncora do 1º ponto incerta ±0.01) e o
embedding amplitude-cego (§4.6) deixa resíduo cedo ~−0.04 mesmo com espectro.

## yang2019_M10_varamp_large_to_small — maxerr 0.1641 @N=3000 (fim), sinal +

mae 0.0573; mesma causa: dado tem degrau no switch ~N1550 (0.84→0.80, nota do
manifest) e queda final 0.79→0.70, modelo constante-0.5mm liso termina 0.86
(+0.16). Sem artefato de âncora (y0=1.000). Resíduo cedo −0.06 (modelo rápido
no 1º bloco) sugere que o 1º bloco "large" real é ≠0.5 mm — os
comprimentos/amplitudes dos blocos precisam ser digitalizados da Fig 11 (não
estão na nota de aparato). **Classe (a) input-alcançável**: `delta_spectrum`
lido da Fig 11 (mesmo grupo/gates do small_to_large). A nota do aparato já
enquadra os varamp como benchmark de REGRA DE ACUMULAÇÃO — exatamente o que o
espectro testa, sem fit novo.

---

## Tabela-resumo

| Caso | maxerr @N (frac) | Classe | Alavanca / rótulo |
|---|---|---|---|
| bauer2024_M8_fig6_rep1 | 0.126 @126 (fim) | (b) forma | cauda runaway vs dado linear; per-espécime já gasto (PR-22) — fila kernel |
| bauer2024_M8_fig6_rep4 | 0.171 @190 (0.89) | (b) forma | TERMINAL: S dos 2 lados, floor cedo demais (já rotulado) — fila kernel |
| bauer2024_M8_fig6_rep5 | 0.112 @231 (0.95) | (b) forma | mesma família rep1/rep4, marginal 0.11 — sem knob |
| bauer2024_M8_fig6_rep6 | 0.130 @171 (0.57 MEIO) | (b) forma | dado linear × kernel S; dois regimes documentados (PR-12g/22) |
| bauer2024_M12_fig8_test2 | 0.180 @1162 (fim) | (b) forma | joelho casado, taxa pós-joelho 1.7× rápida; scatter do k=0.03 (k per-teste=overfit) |
| bauer2024_M12_fig8_test3 | 0.120 @1140 (fim) | (b) forma | espelho do test2 (joelho atrasado, cauda lenta) — joelho de espectro |
| rousseau2025_steel_t10 | 0.188 @170 (fim) | (b) forma | TERMINAL: dado mergulha, modelo trava (runaway grip #10, já rotulado) |
| rousseau2025_hdpe_t10 | 0.153 @145 (0.36 MEIO) | (b) forma | meio íngreme vs kernel suave; sub-alavanca: re-grid min-max grupo HDPE (~0.03–0.05) |
| rousseau2025_hdpe_t12 | 0.138 @250 (0.62 MEIO) | (b) forma | idem t10; acelerar grupo derruba cauda do t12 (trade-off de forma) |
| karlsen2022_M30_HVtorqued_run14p2 | 0.236 @269 (fim) | (b) forma | TERMINAL: taxa do dado acelera 2.7×, ratchet linear não faz (já rotulado) |
| karlsen2022_M42_HV_run20p0 | 0.124 @339 (fim) | (a) knob | k_ratchet≈0.001 per-espécime (classe autorizada run7p1/2p2); caveat: leitura preditiva fraca |
| li2022ti_axialmin_10Hz | 0.112 @200k (fim) | (a) knob | canal de tempo: C_creep per-par fitado-this-rig OU fret_freq_exp (f_ref=20Hz); gate 15/20Hz |
| yang2019_M10_varamp_small_to_large | 0.213 @3800 (fim) | (a) input (+c) | delta_spectrum lido da Fig 10 (maquinaria PR-12); âncora 1.085 = caveat de dado |
| yang2019_M10_varamp_large_to_small | 0.164 @3000 (fim) | (a) input | delta_spectrum lido da Fig 11 (blocos a digitalizar do PDF); zero constante nova |
