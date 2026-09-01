# Re-fit do HDPE do ROUSSEAU — adotado por PROCEDÊNCIA, com o gate de ganho falhado

**2026-08-02** · decisão D-D (por delegação) + prereg
`2026-08-02-rousseau-hdpe-refit`. `GA_member` **20 000 → 22 000**;
fingerprint `a410d6537c83` → **`63722b266dc0`**.

## Por que re-fitar

A `hdpe_t10` mudou de **dado** (re-digitalizada pelo centro da banda,
validada contra a Fig. 7 do próprio paper). O `GA_member=20000` foi
ajustado contra a versão errada ⇒ perdeu procedência. Mesma regra do
erratum do drive do aço: **quando o dado muda, o fit contra o dado velho
não vale mais**.

## ⚠️ A sonda que teria mentido (3ª vez no mesmo dia)

A primeira sonda de `GA_member` deu **Δ = 0,0000 exato** nas duas
direções — leitura óbvia: "alavanca morta". **Era chave de cfg, não campo
do engine**: o runner traduz `GA_member` em `k_member_shear = GA/t`, e o
override morria no filtro de `JointMaterial`. Sondando o campo real, a
resposta é forte. Terceira ocorrência hoje da mesma classe
(`emb_um`→`emb_depth`, canal de flanco sem companheiro, agora esta).

## O resultado, e o regime que fixa o valor

| GA | soma MAE (3 HDPE) | t14 | pioras >0,01 |
|---:|---|---|---|
| 8 000 | 0,6512 | 0,0441 | — |
| 20 000 (antigo) | 0,2092 | 0,0441 | — |
| **22 000** | **0,1887 (−10 %)** | **0,0440** | **nenhuma** |
| 24 000 | 0,1884 | 0,0559 | t14 |
| 30 000 | 0,2210 | 0,1048 | t14 |

**22 000 é o maior valor que mantém a t14 em stick** — a t14 tem MAE
idêntico (0,0441) para qualquer GA ≤ 22 000 e quebra acima. O limite não
é escolha de quem calibra: **é o regime**.

## Gates

| gate | resultado |
|---|---|
| **G1 (ganho ≥15 %)** | ❌ **−10 %** — declarado |
| G2 (nenhuma pior) | ✅ nenhuma das 3 |
| G2b (aço isolado) | ✅ **bit-idêntico** nas 3 |
| **G3 (held-out no tripé)** | ✅ e **melhora**: 0,0267 → **0,0260** |
| G4 (procedência) | ✅ valor lido do regime de stick, não varrido |

**Adotado por procedência, não por ganho** — mesma forma da adoção do
`c_bend` do aço ontem: o gate falhado fica escrito no `prov`/`verdict` do
cfg, não numa nota de rodapé.

## O que isto NÃO é

Não é um ganho de meta: −10 % na soma de três MAEs não tira nenhuma curva
da fila (t10 segue ~2,5×, t12 ~2,2×). O valor do trabalho é outro: **o
número do canônico voltou a ter procedência**, e a evidência preditiva
mais forte da campanha (o held-out da Fig. 6) **melhorou em vez de ser
sacrificada** — que era o risco declarado no prereg.
