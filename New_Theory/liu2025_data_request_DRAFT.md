# RASCUNHO — pedido de dado bruto aos autores do Liu 2025

> ## ❌ CANCELADA pelo professor em 2026-08-01
>
> Decisão em sessão: *"não quero carta a autores, substitua os artigos que
> não tiver acesso"*. A carta NÃO será enviada; a rota vira **substituição
> de fontes** (caça a papers OA com curvas digitalizáveis cobrindo os
> papéis que a fila precisa). O texto abaixo fica como REGISTRO das
> perguntas técnicas que o dado do Liu 2025 deixa em aberto (item 4 = a
> inconsistência D-N⊥curvas medida em `s1_amp_gate_resultado.md`) — útil
> se a política mudar ou se outro grupo publicar com o mesmo rig.

**Contexto e escopo honesto do pedido.** A medição de 2026-07-28
(`liu2025_ramp_v2_results.md`) mostrou que este dado **não** resgata o tripé
vertical de nenhuma curva — no colapso quase-vertical, `res.máx < 0,10` exigiria
acertar o instante da fratura em ±0,05 % da vida, e o scatter de espécime da
própria fonte é 44 %. O pedido continua valendo por **três** razões diferentes:

1. **As 6 curvas da Fig. 3 são data-limited de verdade** — o eixo Y termina em
   20 kN (= 0,333·F₀) e a cauda nunca foi publicada. Só os autores a têm.
2. **Medir o scatter de espécime** — hoje ele é inferido de 2 ensaios na mesma
   amplitude nominal (`fig2` 10 k vs `amp0p8` 14,4 k). Com réplicas, ele vira
   número, e a claim "prever a vida" ganha uma banda em vez de um veredicto.
3. **A 200 Hz, o trecho vertical deixa de ser vertical** — a 1 Hz-classe de
   excitação, 200 Hz dá ~200 amostras/ciclo; o colapso que a figura resolve em
   5 pontos passaria a ter milhares.
4. **(NOVO 2026-08-01, medido em `s1_amp_gate_resultado.md`)** A **D-N da
   Fig. 4 e as curvas das Figs. 2–3 discordam do N₉₅ em 3–5×, nas DUAS
   direções** (0,4 mm: curva cruza 0,95·F₀ em ~2.000 ciclos, a D-N marca
   9.099; 0,25 mm: curva ~62.500, D-N 16.157). Construímos uma forma de
   modelo que reproduz QUALQUER uma das duas escadas (6/6 dentro de 1,7×) —
   mas nenhum modelo satisfaz as duas ao mesmo tempo. Saber a referência de
   F₀ da Fig. 4 (nominal? 1º pico? por espécime?) e se os pontos D-N vêm de
   ESPÉCIMES distintos dos plotados nas Figs. 2–3 destravaria a
   parametrização inteira da fonte.

**O que NÃO pedir** (para o pedido ser pequeno e respondível): não pedir o
tratamento, o modelo, nem os dados de FE — só a série temporal de força de aperto.

---

## Carta (EN)

**Subject:** Request for raw clamp-force time series — *Sci. Rep.* 15 (2025),
DOI 10.1038/s41598-025-02936-6

Dear Dr. Liu and co-authors,

I am a researcher at the Federal University of Uberlândia (Brazil) working on
physics-based modelling of bolted-joint self-loosening. We are validating an
energy-based model against a library of published loosening curves, and your
2025 *Scientific Reports* paper is one of the most informative sources in it —
in particular because you report tests carried on **to fracture**, which very
few transverse-vibration studies do.

We have digitised Figs. 2 and 3 and our model reproduces the plateau and the
onset of the fatigue-fracture stage well. We are, however, limited by what the
figures can show, and we would be grateful for help with the following.

**1. Raw clamp-force series (main request).** Would you be willing to share the
DH5902N recordings (200 Hz) for the six amplitude tests of Fig. 3 and for the
single test of Fig. 2? Even decimated — say, one point per 100 cycles, and full
rate only over the last 5 % of life — would be enough for us. The reason is
specific: in Fig. 3 the ordinate stops at 20 kN, so the final descent of the
0.4–0.8 mm curves leaves the plotted frame and the last ~70 % of the measured
preload loss is not recoverable from the figure.

**2. Cycles-to-fracture for any replicates.** Fig. 2 and the 0.8 mm test of
Fig. 3 are at the same nominal amplitude yet end at ~1.0×10⁴ and ~1.4×10⁴
cycles. If you ran further replicates, even just the fracture-cycle counts
(without curves) would let us quantify specimen scatter, which currently
dominates our uncertainty in loosening-life prediction.

**3. Two numbers not stated in the paper.** (a) The **excitation frequency** of
the transverse actuator — the paper reports the 200 Hz sampling rate but not the
test frequency; (b) the **surface condition / roughness class** of the bearing
faces, which sets the embedding depth in our model.

**4. The F₀ reference of Fig. 4 (D-N).** When we extract the cycles to 95 %
residual preload from the digitised curves of Figs. 2–3 and compare them with
the D-N points of Fig. 4, the two disagree by a factor of 3–5, in **both**
directions (e.g. at 0.4 mm the curve crosses 0.95·F₀ at ≈2×10³ cycles while
Fig. 4 marks ≈9×10³; at 0.25 mm the curve gives ≈6×10⁴ against ≈1.6×10⁴ in
Fig. 4). Could you tell us (a) which F₀ the 5 % criterion of Fig. 4 refers to
(nominal 60 kN, first recorded peak, or per-specimen), and (b) whether the
Fig. 4 points come from the same specimens as the curves of Figs. 2–3 or from
separate runs? Either answer would resolve what currently blocks a single
parametrisation of your dataset in our model.

We would of course cite the data as a personal communication, or in any form you
prefer, and we are glad to share our digitised curves and model results with you
— including where our model **fails** against your data, which may be of interest
given your loosening-life formulation.

Thank you for considering this, and for a very useful paper.

With best regards,

Prof. Leonardo Rosa Ribeiro da Silva, PhD
School of Mechanical Engineering, Federal University of Uberlândia (âncora interna), Brazil
leorrs@ancora_interna.br

---

## Checklist antes de enviar

- [ ] confirmar o autor correspondente e o e-mail no PDF (`pdfs_open_access/liu2025_scirep_M16.pdf`)
- [ ] decidir se anexa as curvas digitalizadas (gesto de reciprocidade; são nossas)
- [ ] decidir se menciona o nome do software (BAS V2) ou fica genérico
- [ ] se houver resposta com dado: **não** substituir CSV canônico sem gate + re-carimbo de fingerprint
