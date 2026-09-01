# PREREG — `lu2024_M8_fig20_T16Nm`: floor lido + embedding ANCORADO no 1º ciclo — a 5ª órfã cai

**2026-08-20 (15:4x)** · **gates congelados neste commit** · mandato das 15:42
(*"continue"*) — a última órfã de protocolo do LU com rota de leitura.

## 1. A releitura que destravou (o mapa da manhã estava errado)

O doc de rotas dizia *"defeito de forma no MEIO da rampa"* — o resíduo da
célula floor-lido mostra outra coisa: **o mx é o 1º CICLO** (modelo 0,424 vs
dado 0,588 em x=2; excesso de embedding −0,164) e dali o modelo CONVERGE ao
dado até −0,005 em c99 (o floor lido funciona). O defeito era o emb, não a
rampa. ERRATA aplicada ao doc de rotas.

## 2. O pacote (per_case `fig20_t16nm`)

| campo | valor | procedência |
|---|---|---|
| `loose_arrest_floor` | **0,195** | **LIDO** (leitor canônico 0,1950; terminal PUBLICADO Tabela 9: 0,187 — 4,3 %, classe T10/T28) |
| `emb_depth` | **4,0 µm** | **ANCORADO no 1º ciclo digitalizado**: o modelo dá c(x=2)=0,594 contra 0,588 do dado (1 %); o c1 PUBLICADO (Tabela 9: decay 35,9 % ⇒ 0,641 em x=1) é a âncora-mãe. Região 4,0–5,0 µm fecha (3 células conexas); o 4,0 é o que casa a âncora — quando há âncora, a âncora manda (precedente floor-lido) |

⚠️ Margem do σ DECLARADA: 0,0249 contra 0,025 — **0,4 % de folga** (precedente
D-V: margem de 0,4 % posta na mesa e aceita). O LU não tem piso de réplica
válido ⇒ limite global.

## 3. Sandbox (já medido)

0,1572/0,2384/0,0578 → **0,0226/0,0569/0,0249 — FECHA** (0,45×/0,57×/0,996×).

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo ao dígito | 0,0226/0,0569/0,0249 pelo canônico |
| **G2** | irmãs LU bit-idênticas (token `fig20_t16nm` só casa ela) | |
| **G3** | isolamento no re-stamp (consolidado com BAUER test1/test2 — 3 curvas no diferencial) + fingerprint único | |
| **G4** | censo | 162 → **165/205 (80 %)** no carimbo consolidado (T16 +1, K6 · BAUER test1 +1, K6 · test2 +1, retirada de exceção) · declaradas 15→13 · exceções 23→22 |
| **G5** | sincronização | retiradas com prova · triagem · docs vivos · aging · HTML |

## Estado

EXECUTADO 2026-08-20 (15:4x-16:2x, carimbo consolidado com BAUER): G1 ao digito (0,0226/0,0569/0,0249 — FECHA, margem sigma 0,4% declarada), G2 irmas LU bit-identicas, G3 isolamento exato fingerprint 4d1211958122, G4 censo 165 no carimbo · declaradas -1 (retirada K6, errata do mapa "meio-de-rampa" aplicada), G5 sincronizado.
