# PREREG — `lu2024_M8_fig20_T28Nm`: o piso LIDO do terminal publicado + chegada fitada-declarada

**2026-08-20 (12:0x)** · **gates congelados neste commit** · mandato das 12:02:
*"conseguimos atacar os 12 casos declarados, individualmente?"* sob a delegação
de decisões de 08-14 — 1º ataque do mapa das 18 declaradas (a T28 é órfã de
protocolo do item F, sem piso de réplica válido ⇒ a única rota é fechar por
MODELO; precedente K6: declarada que fecha por mérito tem a declaração
RETIRADA com prova preservada).

## 1. O pacote (per_case `fig20_t28nm`)

| campo | valor | procedência |
|---|---|---|
| `loose_arrest_floor` | **0,2414** | **LIDO** (`arrest_floor_from_curve`, plateau=False ⇒ limite inferior declarado — estatuto do precedente SUN/T10) e ancorado no **terminal PUBLICADO** (Tabela 9: retenção 0,234 em c100; p.19 dá 3 523 N) — coincidem a **3,2 %**, a mesma classe da T10 (3,4 %) |
| `arrest_approach_exp` | **1,4** | **FITADO-DECLARADO** (sem âncora — estatuto D-Z). Região que fecha: **9 células** (floor {0,234; 0,2414} × aexp 1,1–1,6), interior, não fio de navalha. Célula pela regra de CENTRALIDADE (empate 4-way em vizinhança Moore; desempate pela pior perna: 0,72×). ⚠️ A regressão do expoente NO DADO foi TENTADA e registrada: slope 0,863, r² 0,515 — **não suporta leitura** (suspeita: taxa de fundo de creep distorce o log-log para baixo; fica anotado, não vira ajuste de instrumento) |

A lei de pressão do grupo (`emb_pressure_exp=3,0`) é INERTE aqui por construção
(T28 tem p ≥ p_ref ⇒ S=1 exato — isolamento estrutural do `min(1,·)`).

## 2. Medições sandbox (já feitas)

- Só floor lido (aexp=1,0): 0,1008/0,1969/0,0862 → 0,0229/0,0495/**0,0265** —
  MAE e res.máx fecham com folga, σ a 6 % do limite. O aexp é a peça que falta.
- Célula escolhida: **0,0338/0,0649/0,0181 — FECHA** (0,68×/0,65×/0,72×).
- G2 sandbox: **12 irmãs LU bit-idênticas** (token `fig20_t28nm` casa só ela).

## 3. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha ao dígito | 0,0338/0,0649/0,0181 pelo caminho canônico |
| **G2** | fonte | as 12 irmãs LU bit-idênticas (medido em sandbox; conferido no canônico) |
| **G3** | isolamento | Δ=0 exato fora do LU_2024 no re-stamp |
| **G4** | re-stamp íntegro | fingerprint único nos 210 (gotcha do sintético) |
| **G5** | censo | **159 → 160/205** · declaradas 18 → 17 (retirada K6 da T28 com prova preservada + guarda anti-dupla-contagem) |
| **G6** | sincronização | retirada em `_DECLARADAS` com prova preservada · triagem · docs vivos · aging verde · HTML |

## 4. Predições registradas

1. G1 ao dígito. 2. A T28 é a **1ª órfã de protocolo a fechar por modelo** — a
mesma estrutura T10 (floor lido do terminal publicado) + 1 fitado-declarado.
3. Das 6 órfãs restantes: T16 **não fecha** com estas alavancas (grade medida:
mx nunca cai de 0,148 — defeito de forma no MEIO da rampa, não na chegada);
amp1p5/amp0p5 **pioram** com floor per-case (o floor 0,10 do grupo já as
serve); amp0p25_long **Δ=0 exato** (canal rotacional não carrega a perda dela —
floor não alcança). Registrado para o mapa de ataque, não como gate.

## Estado

EXECUTADO 2026-08-20 (12:1x-13:2x): G1 ao digito (0,0338/0,0649/0,0181 — FECHA), G2 12 irmas bit-identicas, G3 isolamento exato (so as curvas dos preregs do dia no diferencial), G4 fingerprint unico 210 (df35fd990380, consolidado com IJPEM+amp1p5), G5 censo 159->162 no carimbo consolidado · declaradas 18->15 (retirada K6 com prova em _DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO), G6 sincronizado.
