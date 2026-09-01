# A rota "modelar a forma de onda half-sine" do `LU_2024` está **FALSIFICADA**

**2026-08-14** · só-leitura · **nada adotado** · store `55273eab12b0`, censo **146/205** ·
módulos da sonda **limpos** no HEAD `74e1500` (conferido antes de medir — hazard de 08-14).

## De onde veio a hipótese

A retratação LU-PROTOCOLO estabeleceu, pelo texto do paper, que as corridas longas
(`fig14_*_long`) são a **§3.1.3 — half-sine de máquina a 1 Hz** e as `fig18`/`fig20` são o
**§3.2 manual**, que *"elimina os efeitos da half-sine"* (p. 15). As rotas de reabertura
registradas eram duas, ambas externas ao modelo: **réplicas no mesmo protocolo** (dado novo)
ou **µ/OEM do §3.1.3**.

Havia uma terceira, interna, que ninguém tinha testado: **half-sine é carregamento
unidirecional**, e o ciclo transversal do engine é **totalmente revertido** (±δ) ⇒ o modelo
aplicaria ~**2×** o curso real. Se for isso, escalar δ para **0,5×** deveria consertar as
três curvas do protocolo.

## A sonda (controle antes do resultado)

Embrulhei `runner._loading_for` para escalar `delta_mm` **só** nas curvas-alvo.
**Controle obrigatório em 1,00×: 5 de 5 casos reproduzem o store ao dígito** (as 3 alvo mais
2 de fora). Instrumento válido.

| curva | 1,00× | 0,70× | **0,50×** | 0,35× | 0,25× |
|---|---:|---:|---:|---:|---:|
| `amp0p25_long` | 0,1017 | 0,1017 | **0,1017** | 0,1017 | 0,1017 |
| `amp0p5_long` | 0,1257 | 0,2282 | **0,3170** | 0,3170 | 0,3170 |
| `amp1p0_long` | 0,4802 | 0,3676 | **0,2801** | 0,2967 | 0,3055 |

## ⚠️ O resultado sedutor, e por que ele NÃO vale

A `amp1p0_long` — **a pior curva da biblioteca** — melhora **42 % no MAE** (0,4802 → 0,2801)
e **46 % no res.máx** (0,8553 → 0,4617), com **ótimo interior exatamente em 0,50×**, que é o
fator que a hipótese prediz *a priori*. É o tipo de resultado que se quer aceitar.

**Não vale, e o motivo é a classe mecânica.** Instrumentando `resolve_transverse_slip`:

| curva | classe | slip/δ mediano |
|---|---|---:|
| `amp0p25_long` | **STICK** (100 %) | 0,000 |
| `amp0p5_long` | **PARCIAL** | 0,437 |
| `amp1p0_long` | **PARCIAL** | 0,719 |

* A **inércia exata** da `amp0p25` está **explicada e prevista**: em STICK nenhuma alavanca de
  slip alcança — é a regra de classe da campanha funcionando, não anomalia.
* Mas `amp0p5` e `amp1p0` são **da mesma classe (PARCIAL)** e respondem em **direções
  opostas**: uma piora monotonicamente, a outra melhora 42 %.

⇒ **um único fato físico — "o curso real é metade" — não pode estar certo numa curva e errado
na irmã de mesma classe, no mesmo protocolo, no mesmo rig.** A hipótese está **falsificada
como mudança de protocolo**, que é a única forma em que ela seria legítima.

O ganho da `amp1p0` fica sem explicação física e **não deve ser adotado**: ganho que a irmã
de mesma classe não compartilha é a assinatura de **ajustar uma curva**, e é exatamente o que
a parcimônia desta campanha recusa. (Leitura alternativa possível: a `amp0p5` satura em
stick abaixo de 0,7× — o `0,3170` repetido em 0,50/0,35/0,25 é o patamar de stick —, então
o δ menor a mata em vez de corrigi-la. Isso explicaria a piora **sem** salvar a hipótese: se
o mesmo fator leva uma curva a stick e melhora a outra, ele não descreve o aparato.)

## O que isto fecha

**A terceira rota de reabertura do `LU_2024` está fechada por medição** — restam as duas
registradas na retratação, ambas dependentes de **dado novo** ou de **caracterização do
§3.1.3**, nenhuma acessível a esta sessão.

Valor prático: ninguém precisa gastar um prereg nisto. O custo foi ~15 min de sonda, com
controle bit-idêntico e um discriminante (classe mecânica) que já existia.

## Reprodutibilidade

`halfsine_probe.py` no scratchpad: embrulha `runner._loading_for`, controle em 1,0× contra o
store, varredura de 4 fatores nas 3 curvas; classe por wrapper em
`dynamic_stiffness_analyzer.resolve_transverse_slip`. ~15 min, só-leitura.
