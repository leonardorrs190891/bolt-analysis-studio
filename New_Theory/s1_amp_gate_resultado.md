# PR-3 s1_amp_gate — forma CONSTRUÍDA e G1 PASSOU; adoção INCONCLUSIVA (D-N ⊥ curvas)

**2026-08-01** · execução do prereg `2026-08-01-s1-amp-gate-pr3-prereg.md`
(forma B do N₉₅ do LIU_2025). **Resultado em uma linha: o engine agora
SABE expressar o span de 850× do N₉₅ (G1 5/6 com 3 números lidos da D-N
do paper), mas a adoção NÃO aconteceu porque a D-N e as curvas
digitalizadas da MESMA fonte discordam do N₉₅ em 3–5× — o ramo
INCONCLUSIVO declarado no prereg.** Config canônico e fingerprint
intactos; a forma fica default-inerte (padrão fat_ramp/graded_scrit).

## O que entrou no engine (default-OFF exato)

3 campos em `JointMaterial` + helper `stage1_amp_gate(mat, delta_amp)`:
`s1_amp_gate_dref` (m; 0 = OFF bit-idêntico) · `s1_amp_gate_p` (nitidez
Hill) · `s1_amp_gate_floor` (taxa sub-limiar). O gate multiplica SÓ o
`d_delta` de `EmbeddingLoss` e `CreepLoss` (dF₀/dE derivam dele ⇒
conservação intacta; modo força inerte). Invariantes:
`tests/test_stage1_amp_gate.py` (4: G0 bit-idêntico · forma Hill ·
supressão só em amplitude baixa · conservação). VarSpecs dos 3 campos no
variable explorer (cobertura 1:1 mantida, 34/34).

## G1 — PASSOU 5/6 (gate ≥4/6)

Fit de TRÊS números na D-N da Fig. 4 (dado independente das curvas):
`dref=0,75 mm · p=13 · floor=5e-4`.

| amp | N₉₅ dado (fig4) | N₉₅ modelo | razão |
|---:|---:|---:|---:|
| 0,25 | 16.157 | 17.670 | 1,09× ✓ |
| 0,30 | 13.516 | 17.557 | 1,30× ✓ |
| 0,40 | 9.099 | 10.303 | 1,13× ✓ |
| 0,50 | 2.745 | 2.369 | 0,86× ✓ |
| 0,60 | 460 | 175 | 0,38× ✓ |
| 0,80 | 19 | 119 | 6,2× ✗ (gate não ACELERA — limitação declarada) |

Do relógio constante-108 (0/6, pior 150×) para 5/6 dentro de 3×. A física
da forma está validada contra a âncora.

## G2/G3 — FALHARAM, e o porquê é um ACHADO sobre o dado

Com os números congelados, janela completa: as 2 da fila de amplitude
baixa melhoram MUITO (amp0p25 MAE 0,0757→**0,0292**; amp0p3
0,0645→**0,0213** — exatamente o que a forma promete), mas amp0p8/fig2
pioram e as 3 do meio (0,4/0,5/0,6, hoje no tripé) QUEBRAM (mx 0,06→0,45;
σ 0,02→0,14). Causa raiz (já estava na tabela do instrumento):

| amp | N₉₅ da CURVA digitalizada | N₉₅ da FIG. 4 | razão |
|---:|---:|---:|---:|
| 0,25 | 62.500 | 16.157 | curva 3,9× TARDE |
| 0,40 | 2.000 | 9.099 | curva 4,5× CEDO |
| 0,50 | 692 | 2.745 | 4,0× CEDO |
| 0,60 | 182 | 460 | 2,5× CEDO |
| 0,80 | 91 | 19 | 4,8× TARDE |

**As duas publicações da MESMA fonte discordam do N₉₅ em 3–5×, nas DUAS
direções** ⇒ nenhum relógio pode satisfazer ambas; ajustar à D-N quebra
as curvas por construção. O prereg tinha o ramo: "se a D-N e as curvas
discordarem do N₉₅, o teste não testou — documentar e parar". Hipóteses a
investigar (fila): definição do F₀ de referência da Fig. 4 (nominal vs
1º ponto — não explica as duas direções sozinha), amostragem esparsa das
curvas de varredura perto do cruzamento, eixo log da Fig. 4.

## EMENDA "curvas mandam" (professor, 2026-08-01) — EXECUTADA, e o veredicto endureceu

Decisão em sessão: entre a D-N e as curvas, **as curvas são a
autoridade** (emenda pré-registrada
`2026-08-01-s1-amp-gate-emenda-curvas-mandam.md`, alvos congelados dos
N₉₅ das curvas: 62.500/25.000/2.000/692/182/91).

- **G1c PASSOU 6/6** — melhor combo `dref=0,75 mm · p=9 · floor=5e-5`,
  todas as razões dentro de **1,7×** (1,35/1,19/1,69/0,73/0,81/1,33). A
  forma consegue expressar TAMBÉM a escada das curvas (687× de span).
- **G2c FALHOU do jeito mais informativo possível: TODAS as 7 curvas
  pioram >0,01 em alguma perna** (janela completa;
  `liu2025_n95_g2c_curvas.json`). Soma MAE da fila −3,3 % (gate −20 %);
  mx/σ explodem em toda parte (amp0p25 mx 0,094→0,349; amp0p3 tem MAE
  0,0645→**0,0247** e mesmo assim viola mx +0,014).

**Leitura estrutural (3ª falsificação pré-registrada do dia na mesma
classe):** casar o N₉₅ — um resumo de 1 ponto — desloca TODO o segmento
inicial do modelo e abre um platô onde o dado desce gradualmente; a
forma do dado exige que o processo INTEIRO (estágio I **e** o schedule
de wear/incubação do estágio II) re-temporize coerentemente com a
amplitude. Um gate num mecanismo só não pode; um fit conjunto
(s1_gate + slip_onset_W + …) seriam ≥5 números em 7 curvas — tortura de
parâmetro, vetada. É o mesmo veredicto da decomposição do σ_res de
2026-07-29 ("curvatura, não taxa") reaparecendo na escala do N₉₅.

## Consequências (estado final do arco)

1. **Nada adotado em nenhuma das 3 rodadas** — censo/fingerprint
   intactos (tripé 136/203). A forma `s1_amp_gate` fica no engine,
   default-inerte, com testes e VarSpecs.
2. A fila LIU_2025 (4 curvas) é **form-limited além do relógio de
   estágio I** — o diagnóstico completo (instrumento N₉₅ + 3
   falsificações gateadas + inconsistência D-N⊥curvas) está registrado;
   os requisitos de parada por classe (≥2 instrumentos + membros
   falsificados por predição pré-registrada) estão sendo cumpridos
   para a classe "relógio de estágio I".
3. Rotas restantes: pergunta aos autores sobre a Fig. 4
   (`liu2025_data_request_DRAFT.md`) e/ou uma forma COORDENADA de
   amplitude (estágios I+II juntos) — decisão do professor, com o aviso
   de identificabilidade acima.

## Adendo (mesma noite): a realocação de wear morreu na sonda de 2 pontos

Última variante não-vetada da coordenação: com o gate ligado, devolver o
declínio de meio-de-curva ao WEAR (`k_wear_spec` > 0; ele é ∝ trabalho de
slip, naturalmente escalado por amplitude — e o cfg adotado o zera).
Sonda em amp0p25 (janela completa): `k_wear_spec` ∈ {0, 1e-15, 5e-15,
2e-14} ⇒ resultado **IDÊNTICO ao dígito** nas 4 doses
(0,0483/0,3486/0,1096) — parâmetro morto. Causa: a incubação
(`slip_onset_W=250 k J`) mantém o canal fechado em 0,25 mm (slip pequeno
nunca acumula a dose); destravar = baixar o onset = o 5º número do fit
coordenado, que os casos 0,4–0,8 usam — vetado. A classe "realocação de
mecanismo sob o gate" morre na sonda, sem gastar um prereg.
