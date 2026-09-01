# PREREG — forma `loose_runaway_*` no engine + per_case da `zhang2006_fig3` (caso didático fora-do-censo)

**2026-08-20 (14:2x)** · **gates congelados neste commit** · mandato das 14:18:
*"forma na engine"*, na sequência de *"faça da maneira mais robusta"* — a
rota robusta provou a forma faltante com constantes lidas
(`zhang2006_fig3_estudo_do_caso.md` §9) e o professor autorizou a forma.

## 1. A forma (já implementada, TDD 5/5)

`loose_runaway_{frac,gain,sharpness}` — transição lei-de-potência → runaway
no ramo graded: boost Hill `1 + gain·fc^k/(fc^k + r^k)` sobre `d_theta`,
r = F₀/F₀_init. Física: o auto-travamento residual (torque de atrito ∝ F)
deixa de segurar o backoff abaixo de r_c. Espelho do `crash_trigger` (que
suprime antes do gatilho): aqui a taxa do meio fica INTACTA. Default frac=0
OU gain=0 = **OFF exato** (nem computa; `test_loose_runaway`, 5 invariantes,
incl. bit-idêntico e inerte-no-kernel-torque).

## 2. O per_case `fig3` (ZHANG_2006) — célula LIDA PURA

| campo | valor | procedência |
|---|---|---|
| `loose_rate_mode`/`s_crit_loose`/`loose_amp_exp` | graded / 0 / 0 | pacote P-13 |
| `loose_F_exp` | **5,80** | **LIDO** — regressão da lei de taxa no traço θ digitalizado (r²=0,74, INDEPENDENTE da escala), concordante com a regressão independente do P (5,93, r²=0,99) |
| `loose_runaway_frac` | **0,25** | **LIDO** — o paper define o fim do Estágio II em P=25 % |
| `loose_runaway_gain` | **13,0** | **LIDO** — razão de taxas do disparo (~14×) − 1 |
| `loose_runaway_sharpness` | default 6,0 (não setado) | células com sharpness fitado melhoram σ só marginalmente (0,0390→0,0350) e não fecham — não vale 1 fitado |
| `slip_onset_W` | 200 | ancorado no N_onset=161 (demarcação DESENHADA na figura) |
| `k_loose_graded` | **0,009** | FITADO — mas dentro da banda ±30 % da escala do θ (0,0074·1,3 = 0,0096) |
| `c_bend` | 1,0 | FITADO (destrava o slip; ótimo interior da varredura 0,3–5) |
| `k_wear_spec`/`K_archard` | 0 / 0 | **LEITURA do texto**: Estágio II é *backoff da porca*, não desgaste |
| `loose_arrest_floor` | 0,0 | LIDO — o dado afrouxa total |

Contagem honesta: **2 fitados** (c_bend, K — este dentro da incerteza de
leitura), o resto lido/ancorado. Sandbox: **0,2110/0,6608/0,2215 →
0,0320/0,0875/0,0390** — MAE e res.máx FECHAM; σ 1,56× é o piso da curva
(6 eixos varridos).

## 3. Estatuto — declarado ANTES

A fig3 é DECLARADA por proveniência ("Illustration") e **continua declarada**
— σ não fecha e a proveniência não muda com o ajuste. A adoção é de **caso
didático fora-do-censo**: o report/galeria passam a mostrar o modelo
reproduzindo os 2 estágios canônicos da literatura com constantes lidas.
**Censo INALTERADO por construção.**

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | célula ao dígito | 0,0320/0,0875/0,0390 pelo canônico |
| **G2** | irmãs | fig16_runout e fig12 (se no store) bit-idênticas — token `fig3` casa só ela |
| **G3** | isolamento | Δ=0 exato fora do ZHANG_2006 no re-stamp |
| **G4** | fingerprint único nos 210 (gotcha do sintético) | |
| **G5** | censo | **162/205 INALTERADO** · declaradas 15 INALTERADO |
| **G6** | sincronização | suíte com os 3 testes novos verde · VarSpecs (127? = 124 campos cobertos) · ledger DOF · estudo §10 · docs |

## Estado

EXECUTADO 2026-08-20 (14:2x-15:0x): G1 ao digito (0,0320/0,0875/0,0390), G2 fig16 bit-identica, G3 isolamento EXATO (so a fig3 no diferencial vs HEAD), G4 fingerprint unico 25be50adbc05 nos 210, G5 censo 162/205 INALTERADO (a fig3 segue declarada — caso didatico fora-do-censo), G6 guardas 16/16 + ledger DOF (teto 125, sharpness dormente) + VarSpecs 124/124.
