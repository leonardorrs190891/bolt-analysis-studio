# Recuperação ROUSSEAU — HDPE prevê condição NOVA no tripé; aço re-fitado com gate FALHADO declarado

**2026-08-01** · execução do prereg `2026-08-01-rousseau-recuperacao`
(+ emenda pré-fit). Fase 1 (digitalizar) → 2 (re-fit do aço) → 3
(held-out). Resposta ao "qual próximo passo": era a única rota 100 %
campanha, e rendeu o **melhor teste preditivo que a fonte já teve**.

## Fase 0 — a emenda que salvou o plano (vetagem na IMAGEM)

O held-out planejado era a **Fig. 10**. Ao abrir a página: é um **laço de
histerese** (força transversal × deslocamento, 3 amplitudes) — não é curva
F/F₀-vs-N; Figs. 7–8 idem (% de perda vs rigidez). Held-out trocado para a
**Fig. 6** ANTES de qualquer fit. Segunda vez no dia que caption/resumo
engana e a imagem corrige.

## Fase 1 — Fig. 6 digitalizada (2 curvas, condição INÉDITA)

`New_Theory/digitize_rousseau2025_fig6.py`. A Fig. 6 roda **os dois
materiais na MESMA condição**: t10, **0,2 mm**, **F₀ ≈ 3,5 kN** — contra
Fig. 4 (HDPE 4 kN/0,5 mm) e Fig. 5 (aço 10 kN/0,05 mm). É condição nova
para os dois ramos.

G1 passou com asserts: steel F₀ 3511 N → fim 573 N (97 pts); hdpe 3515 N →
2806 N (99 pts); span 0–99 ciclos; overlay conferido.

**Dificuldade real do tracer** (registrada porque é reutilizável): as
curvas de **rotação dividem as cores** com as de preload (vermelha
tracejada, preta traço-ponto) e **cruzam** o preload. Resolvido por
**forma, não por cor**: preload só desce (y do pixel só cresce) ⇒ o tracer
só aceita runs monotônicos. Dois defeitos medidos e consertados: máscara
de legenda larga demais engolia 52 colunas da curva vermelha (morria em
x=958 de 1896) → máscara **por cor**; e salto fixo de 30 px matava o
tracer após qualquer vão → **salto proporcional ao vão** (`30 + 1,2·vão`).

## ⚠️ Armadilha de token — o "held-out" quase nasceu inválido

Primeira simulação do HDPE novo: **rodou a 0,5 mm em vez de 0,2** — o dict
`delta_amp_mm` do cfg casa por SUBSTRING e o token `t10` da série da
Fig. 4 pegou `rousseau2025_hdpe_t10_amp0p2`. O resultado "ótimo" (MAE
0,030) era 2,5× o drive real. **Consertos:** matcher passou a
**token-mais-longo-vence com erro em empate** (era o *primeiro do dict* —
dependia da ordem de inserção; mesma classe do empate YANG_2019) e token
explícito `t10_amp0p2: 0.2` no cfg. As 3 curvas antigas ficam com
0,5/0,49/0,38 (verificado).

## Fase 3 — resultado (o que importa)

| curva | condição | antes | depois | veredito |
|---|---|---|---|---|
| **hdpe_t10 @0,2 mm** (held-out) | NOVA | — | **0,0267 / 0,0755 / 0,0245** | **TRIPÉ, zero-refit** |
| steel_t10 @0,2 mm (held-out) | NOVA | 0,2154 | 0,1329 | G2 **FALHOU** (bar 0,10) |
| steel_t10 @0,05 mm | Fig. 5 | 0,304 | **0,107** | melhora |
| steel_t12 @0,05 mm | Fig. 5 | 0,078 | **0,041** | melhora |
| steel_t14 @0,04 mm | Fig. 5 | 0,020 | 0,020 | idêntica (stick) |

**O HDPE previu uma condição nova, 2,5× fora da amplitude do fit, dentro
das TRÊS pernas, sem tocar em um número.** É a validação mais forte que a
forma `k_member_shear` (PR-14) recebeu — e vem de um dado que só existe
porque o erratum mandou ler o PDF.

## O aço: adoção POR PROCEDÊNCIA, não por predição

Fit de **1 número** (c_bend 0,3 → **3,0**) só na Fig. 5; o 2º candidato
(`emb_depth`) não ajudou e ficou onde estava. O valor anterior tinha
**procedência void** (fitado sob drive 10× errado). Adotado — e o
**G2 falhado está escrito na própria adoção** (`prov`/`verdict` do cfg):
a claim é *"fit com procedência válida"*, **não** *"prevê nova
amplitude"*.

**O residual é o achado de física:** a 4× a amplitude do fit o modelo
**retém 0,313 contra 0,164 medido** — déficit de resposta à amplitude, a
MESMA classe do N₉₅ do LIU_2025, agora medida com **dado internamente
consistente** (mesmo rig, mesmo paper, duas amplitudes). Isto é o
candidato mais limpo que existe hoje para a forma de amplitude, e vale um
prereg próprio.

## Fase 4 (mesma sessão) — a hipótese de amplitude MORREU NA TABULAÇÃO

O prereg seguinte (`forma-amplitude-rousseau`) ia abrir forma de
resposta à amplitude com esta âncora. **Ao tabular os dois pontos antes
de fitar, a hipótese caiu:**

| condição | dado (fim) | modelo (fim) |
|---|---:|---:|
| 0,05 mm (fitada) | 0,137 | 0,301 |
| 0,20 mm (held-out) | 0,164 | 0,313 |

O dado **quase não muda** com 4× de amplitude — e o modelo também não.
Não há déficit de *inclinação*; há déficit de **nível**, o mesmo nas
duas (o modelo retém ~2× o medido). Abrir forma de amplitude seria fitar
uma inclinação que o dado não pede. **Nenhuma forma foi aberta.**

### O que o dado pedia, e a constante tinha procedência de APARATO

Decomposição: o canal dominante é **afrouxamento rotacional (67–79 %)**.
Varredura das constantes de nível (G1): `tr_loose_gain` e `mu` pioram
tudo; **`loose_arrest_floor` = 0** dá **−22 %** na soma dos MAE do aço
com **zero curvas piores**, e é **ótimo de fronteira monótono**
(0,00→0,233 · 0,02→0,250 · 0,05→0,276 · 0,10→0,315 · 0,15→0,351) — não há
mínimo interior para ajustar.

**A procedência não é o fit, é o rig:** o paper apoia o membro móvel em
**roletes INA-HYDREL FE, declaradamente para remover o atrito parasita**.
Sem esse atrito não existe o auto-travamento que o floor representa —
*runaway* puro é o enunciado físico do aparato, e o dado concorda (o aço
perde 86 % em 180 ciclos). O `0,08` que estava valendo vinha do **pack**,
não de leitura do rig.

Resultado do aço com a adoção (store re-carimbado,
fingerprint `a410d6537c83`): **t10 0,107→0,0725 · t12 0,041→0,0451 ·
t14 0,020 · held-out 0,133→0,0957**.

⚠️ **Nota honesta sobre o G2**: com as DUAS adoções (c_bend + floor) o
held-out passa a barra de 0,10 que o G2 reprovara com o c_bend sozinho.
Isso **não** re-escreve o veredicto — o gate foi avaliado no que ele
media, e o registro fica. O que a barra atravessada diz é que a claim
"prevê a condição nova" ficou **defensável para o aço também**, agora
por uma constante de aparato, não por ajuste.

## Efeito no censo

+2 comparáveis (205), +1 tripé (o HDPE novo), aço melhora sem fechar.
Fingerprint muda (cfg tocado) ⇒ re-stamp uniforme. Números finais no
commit.
