# PREREG — `yang2019_M10_amp0p4_5Hz`: o pacote gth LIDO + trim@9000 (transição de regime out-of-model, 16º trim do §B)

**2026-08-20 (10:2x)** · **gates congelados neste commit** · mandato explícito
das 10:17: *"ataque mais …yang2019_M10_amp0p4_5Hz.html para ficar no tripé"*,
sob a delegação de decisões de 08:14.

## 1. O pacote (per_case `amp0p4`; leituras do próprio dado)

| campo | valor | leitura |
|---|---|---|
| `emb_depth` / `C_creep` | 0 / 0 | platô PUBLICADO de 4000 ciclos (1,000–1,004) |
| `gth_k` | 7,19e-5 | LSQ da INTEGRAL F(N) (r²=0,969) |
| `gth_A0` | 2009 | onset do platô (N≈4690 × rq) |
| `gth_accel_p` | 2,87 | aceleração da taxa (11,6× para Neff 3,8×) |
| `slip_onset_W` | 0 | o 40.000 J do GRUPO é observável das irmãs de SLIP; nesta curva de stick o W nunca acumula e o gate Hill zera o canal PARA SEMPRE (causa-raiz medida hoje) — a incubação DESTA curva é o `gth_A0` lido |
| **`trim_n_max`** | **9000** (cfg do grupo, formato {token: N}) | ver §2 |

## 2. O trim, e por que ele é a classe do §B e não um atalho

A cauda pós-9000 é o INÍCIO do colapso por **transição de regime stick→slip**
— a classe exata dos 15 trims existentes ("finais com fratura/colapso →
out-of-model → trim", li2022ti/yang2021/liu2022). O dia gastou **6 estruturas
falsificadas com números** tentando capturá-la:

1. damage knockdown total (D=1 ⇒ µ=0 desliga os drives — F volta a 1,000);
2. graded pós-ruptura (o [K(s)] re-trava; slip re-fecha);
3. µ_s/µ_k latch (avalanche: o feedback µ↓→slip↑→dreno colapsa em ~1000
   ciclos onde o real leva 2000+);
4. damage-com-teto em W_ref grande (D não cresce: W intermitente ~7,5e-5 J/c);
5. damage-com-teto em W_ref pequeno (detona cedo);
6. damage-com-teto na escala MEDIDA do W (0,11→3,5 J na transição): ainda
   avalanche — **conclusão estrutural: o W pós-abertura explode com o
   feedback, logo qualquer acoplamento W→µ é efetivamente um degrau**. A
   gradualidade real (população de asperezas rompendo) exigiria um relógio
   próprio sem observável independente = fit puro (item D).

O modelo segue o dado a **±0,014 até N=9000** (90 % da janela; o joelho da
transição do modelo emerge em F=0,916 — o mesmo do dado). O trim declara o
que o engine declaradamente não tem, com a física nomeada e os observáveis
para o desenho futuro (o joelho e a taxa da avalanche).

## 3. Sandbox — FECHA

**0,0966/0,1411/0,0761 → 0,0087/0,0240/0,0101** (0,17×/0,24×/0,40×).

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha ao dígito | 0,0087/0,0240/0,0101 pelo canônico |
| **G2** | as 6 irmãs YANG_2019 bit-idênticas | (o slip_onset_W=0 é per_case; o trim é por token) |
| **G3** | isolamento no diferencial do carimbo | |
| **G4** | fingerprint único nos 210 | |
| **G5** | censo 158 → **159/205 (78 %)** · abertas 6 → 5 | |
| **G6** | o trim entra como o **16º do §B** (lista de exceções da F5 — decisão DELEGADA, registrada para sua ratificação) + report/censo/docs/aging | |

## Estado

EXECUTADO 2026-08-20 (10:2x-10:4x): G1/G2 na hora; carimbo único.
