# `k_emb_renew` por protocolo — NÃO ADOTA, e a predição que eu registrei FALHOU

**2026-08-04** · prereg
`2026-08-04-liu2022-emb-renew-por-protocolo-prereg.md` (decisão D-F, por
delegação). Fingerprint intacto: `63722b266dc0`. Executor:
`New_Theory/liu2022_emb_renew_exec.py` · dados:
`liu2022_emb_renew_exec.json`.

## Veredicto: NÃO ADOTA — por DOIS motivos independentes

O ramo declarado que se aplica é **"NÃO ADOTA (t4 bloqueia)"**. Mas a
medição entregou um segundo motivo, mais fundo, que não estava previsto:
**a correção de nível troca erro entre estágios em vez de consertar
física.**

## A varredura, gate por gate

| X | G2 controle | G4 t1/t2 fecham | G1 held-out sai | G1b soma MAE fig7a | G3 pior no t4 (mae/mx/σ) |
|---:|---|---:|---|---:|---|
| 0,9 | ✅ | 0/2 | nenhuma | **+0,0005** | +0,0048 / +0,0056 / +0,0012 ✅ |
| **0,8** | ✅ | **2/2** | nenhuma | **+0,0010** | +0,0096 / **+0,0113** / +0,0024 ❌ |
| 0,7 | ✅ | 2/2 | nenhuma | +0,0015 | +0,0144 / +0,0169 / +0,0037 ❌ |
| 0,6 | ✅ | 2/2 | nenhuma | +0,0022 | +0,0193 / +0,0225 / +0,0051 ❌ |
| 0,5 | ✅ | 2/2 | nenhuma | +0,0030 | +0,0241 / +0,0281 / +0,0065 ❌ |
| 0,3 | ✅ | 2/2 | nenhuma | +0,0044 | +0,0337 / +0,0394 / +0,0096 ❌ |

**Não existe dose que feche t1/t2 mantendo o t4 dentro de +0,010.** A janela
é estreita e mensurável: em X=0,8 o t4 estoura por **+0,0013** numa perna
(res.máx), e em X=0,9 o t4 passa mas t1/t2 não fecham.

## Motivo 1 — a predição G1b falhou, e isso é diagnóstico

Registrei no prereg: *"se o mecanismo for real, a fig7a deve **melhorar**
(...) Se der ausência-de-piora-sem-melhora, dizer isso e não vender como
confirmação."*

**A fig7a piorou em TODAS as seis doses** (+0,0005 a +0,0044 na soma dos 4
MAE). Nenhuma curva dela sai do tripé — o G1 duro passa —, mas a predição
positiva **falhou**.

E o motivo não é ruído: **a fig7a também tem tendência no dado**
(1,43× · 2,05× por reaperto). Baixar o nível ajuda o t1 (dado perde 2,78 %,
modelo 5,76 %) e **atrapalha o t3** (dado 8,14 %, modelo 5,56 % — o modelo
já perde de menos lá). Os dois efeitos se cancelam com saldo negativo.

⇒ **A correção de nível redistribui o erro entre estágios.** Ela fecha t1/t2
na fig8 porque lá a mistura de estágios favorece, não porque a física esteja
melhor. Este argumento é **independente do t4** e sozinho justifica a
recusa.

## Motivo 2 — o t4 é fratura, e não vou declará-lo para desbloquear

O prereg previu isto por escrito, antes de medir: *"Não vou declarar o `t4`
fora do censo para desbloquear este gate (...) Declarar por conveniência
inverteria a ordem da prova."* Mantido. O estatuto do t4 fica como decisão
**separada**, com prereg próprio, e tem duas rotas honestas:

* **por mérito** — ligar o canal de fadiga com `N_f ≈ 1500` **lido da nota
  de aparato** (precedente exato: adoção E2 do LIU_2025, `N_f` como
  input-de-paper por curva, gates 7/7). O cfg do grupo hoje **não tem**
  `fatigue_enabled`, então o mergulho é inproduzível por construção.
* **por escopo** — declarar, com a procedência tripla que já existe
  (registry, nota de aparato, `CLAUDE.md`).

## O que passou, e vale registrar

* **G2 (isolamento): perfeito nas 6 doses.** As 12 curvas de
  `fig5`/`fig6a`/`fig6b` ficaram bit-idênticas — a chave nova
  `LIU_2022_RETIGHT_direct` **não vazou de grupo**, e o prefixo mais longo
  venceu `LIU_2022_RET` sem empate, como o prereg previa.
* **G1 (held-out duro): passou.** Nenhuma das 4 curvas do fig7a sai do
  tripé em nenhuma dose. A claim "é o protocolo" não foi **refutada** — ela
  só não foi **confirmada**.
* Instrumento validado: baseline re-simulado bate com o store a 1e-9 nas 21.

## Consequência para a fila

As três curvas do `LIU_2022_RETIGHT` na fila form-limited **continuam nela**.
O defeito está nomeado com precisão e tem três falsificações independentes:

1. **família de constantes** — 10 parametrizações, tendência 10× fraca
   demais (prereg D-E, G1);
2. **relógio por contagem de reapertos** — contradição intra-fonte, o dado
   varre 0,75× a 2,05× entre as 4 cadeias do mesmo rig (medição direta: uma
   forma não produz direções opostas);
3. **substituto de nível** — fecha por redistribuição, e a predição
   registrada no held-out falhou (prereg D-F, G1b).

Isso satisfaz o requisito (a) da regra de parada (≥2 instrumentos
independentes) e o (b) para **2 dos 3** membros por pré-registro — o terceiro
morreu por contradição direta no dado, que é mais forte que prereg, mas
**não** foi pré-registrado, e o registro tem de dizer isso.
