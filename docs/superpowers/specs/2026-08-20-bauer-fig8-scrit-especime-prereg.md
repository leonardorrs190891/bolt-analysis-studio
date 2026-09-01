# PREREG — BAUER fig8: o LIMIAR do espectro ligado, s_crit POR ESPÉCIME (test1+test2; test3 recusado por navalha)

**2026-08-20 (15:2x-15:4x)** · **gates congelados neste commit** · mandato das
15:19 (*"continue"*) — a 2ª evidência da classe de aceleração tardia, atacada
com o instrumental do dia.

## 1. A física — que é a da PRÓPRIA nota de aparato

A fig8 roda **espectro variável** (18 ciclos a 80 µm + 2 a 155 µm — JÁ
adotado no grupo) e a nota explica o 3-stage: *"collapse as falling F_V drops
the critical amplitude below the spectrum base"*. Isso é o kernel
`graded_scrit` COM limiar — mas o grupo rodava **`s_crit_loose = 0`**: sem o
limiar, a transição de fração do espectro (2/20 → 20/20 ciclos ativos) não
existe e a aceleração não emerge. INSTRUMENTADO: o slip da base cresce
0 → 25 µm ao longo do ensaio (o [K(s)] a solta) e o disparo acontece quando
ele cruza o s_crit — a mecânica exata da nota.

⚠️ Falsificações no caminho (registradas): a forma `loose_runaway_*` de hoje
com frac=0,75 lido do joelho **PIORA MUITO** (0,30–0,53 de MAE — o boost é
bifurcação; o bauer é transição GRADUAL de fração) — a 2ª evidência do
runaway-de-porca-solta **não é esta fonte**; e o s_crit ÚNICO de grupo
destrói as irmãs (G2 6/6 reprovado) — o joelho varia POR ESPÉCIME, como a
própria fonte documenta (*"knee position varies per test, F_V ≈ 35–40 kN"*;
fig6: 5 réplicas dispersam 0,93–1,08 ⇒ piso σ da fonte 0,0900).

## 2. O pacote — per_case por espécime (tokens `test1`/`test2`)

| curva | célula (s_crit · k) | base → resultado | região |
|---|---|---|---|
| `test1` (DECLARADA metric-limited) | **15 µm · 0,070** | 0,0745/0,3965/0,0928 → **0,0305/0,0719/0,0282 — FECHA** | **7/9 células** na grade fina; centralidade 4/4 vizinhos; pior perna 0,72× |
| `test2` (EXCEÇÃO assinada) | **30 µm · 0,060** | 0,0290/0,1795/0,0461 → **0,0149/0,0419/0,0187 — FECHA** | **4/4 vizinhos** fecham; pior perna 0,47× |
| `test3` (EXCEÇÃO assinada) | **RECUSADO** | melhor célula isolada (14 µm · 0,050 → 0,0157/0,0342/0,0131) tem **0/4 vizinhos** fechando — fio de navalha MEDIDO; as 3 células que fecham são diagonais (degenerescência s_crit↔k) | fica exceção como está; grupo intocado ⇒ bit-idêntico |

Contagem: 2 fitados por curva ×2 (estatuto IJPEM — a forma-mãe é a física da
nota; o joelho F_V 35–40 kN dá a REGIÃO, não o valor). O limite σ da fonte é
**0,0900** (piso de réplica fig6 — `rh.limite_sres`, o helper canônico; a
sonda inicial errou usando 0,025 fixo e está registrado).

## 3. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | test1 ao dígito | 0,0305/0,0719/0,0282 pelo canônico — FECHA |
| **G2** | test2 ao dígito | 0,0149/0,0419/0,0187 pelo canônico — FECHA |
| **G3** | test3 + fig6 ×5 + resto da fonte | bit-idênticos (tokens disjuntos; grupo intocado) |
| **G4** | isolamento | Δ=0 exato fora do BAUER_2024 no re-stamp; fingerprint único nos 210 |
| **G5** | censo | 162 → **164/205** · declaradas 15 → 14 (test1, K6) · exceções 23 → 22 (test2, retirada por mérito) |
| **G6** | sincronização | retiradas com prova preservada · triagem · docs vivos · aging · HTML |

## 4. Predições registradas

1. G1/G2 ao dígito. 2. O test1 é a 2ª metric-limited a cair pela releitura
do "colapso" (a 0_45 foi a 1ª — lá era passo de amostragem; aqui é transição
de fração do espectro que o limiar cruza). 3. A classe "aceleração tardia"
PERDE um membro para INPUT+kernel (não forma nova): das 3 (bauer test1,
fig14_amp0p5/1p0_long), sobra o par fig14 (scatter colossal). 4. test3 fica
— e a recusa por navalha é a prova de que o gate anti-navalha faz trabalho.



## §6 ADENDO pós-execução (22:4x) — o texto integral da p.8 lido

1. ⚠️ **Correção de input PENDENTE**: o paper diz `sa,E,peak = 150 µm`; o
   `delta_spectrum` adotado carrega **155 µm** (erro de 3 %). Corrigir exige
   re-gates das 3 curvas (2 recém-fechadas) — vai à fila como correção de
   input, não se executa às 22h em cima de fechamentos do dia.
2. **"For both linear sectors, the gradients of all tests are still
   similar"** — os AUTORES afirmam gradientes similares entre os testes.
   Isso REFORÇA os fitados test1/test2 (k 0,070/0,060, próximos) e explica o
   test3 como o espécime anômalo (a diagonal dele pedia k 0,033–0,050).
3. **ΔFV,init**: as curvas calculadas do autor partem de pré-cargas iniciais
   DIFERENTES (perda de montagem por plastificação + spring-back da torção).
   O nosso dado normalizado absorve isso no 1º ponto, mas o F₀ FÍSICO do
   espécime (que entra em µF₀/thresholds) pode diferir do nominal 50 kN —
   rota possível para a navalha do test3 (F₀ por espécime), sem observável
   direto no dado normalizado. Fica nomeada.
4. A fronteira POR PRÉ-CARGA é publicada: s_crit(50 kN)=99 µm,
   s_crit(35 kN)=76 µm — material para conversão futura da fronteira do
   autor à coordenada de slip do engine.

## Estado

EXECUTADO 2026-08-20 (15:4x-16:2x, carimbo consolidado com T16): G1 test1 ao digito (0,0305/0,0719/0,0282 — FECHA), G2 test2 ao digito (0,0149/0,0419/0,0187 — FECHA), G3 test3+fig6 bit-identicos, G4 isolamento exato (3 curvas no diferencial) fingerprint 4d1211958122, G5 censo 165 no carimbo (162+3) · declaradas -1 · excecoes -1, G6 sincronizado (catraca 21->20, guarda de piso respondida com numero, pin T16 3a era).
