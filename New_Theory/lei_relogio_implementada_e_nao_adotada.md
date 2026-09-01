# A lei `N_emb ∝ 1/δ` está **implementada e correta** — e **não foi adotada**. O motivo é o que ela revelou.

**2026-08-14** · engine: forma nova **default-inerte** · **nada adotado** ·
store `c37618c5cc96`, censo **141/205** · assinatura de forma em bloco do professor
(*"continue, assine tudo, e faça o loop sem parar"*).

Sequela direta de `lei_relogio_embedding_por_deslocamento.md` (derivação + predição
zero-refit 4/4) e da adoção `CHU_2026_D1p0` (`3b07011`).

---

## 1. O que foi construído

Campo novo em `JointMaterial`, no padrão default-inerte da campanha:

```
emb_clock_delta_ref : float = 0.0      # 0 = OFF exato
# quando > 0:  N_emb_eff = N_emb * (emb_clock_delta_ref / |delta_amp|)
```

Lido em `EmbeddingLoss.rate()`. Invariantes em `tests/test_emb_clock_delta.py` (4).

### ✅ Gate de PARIDADE — 8 de 8 idênticas ao 12º dígito

A validação anterior injetava o `N_emb` **calculado à mão** por curva. O engine agora
faz a divisão internamente. **Não são a mesma afirmação**, e a diferença já custou um
dia nesta campanha (`emb_um` vs `emb_depth`, filtrado em silêncio).

| curva | δ | à mão (`N_emb` explícito) | engine (a lei) | igual? |
|---|---:|---|---|---|
| `test2` | 0,4 | 0,1193/0,3881/0,1508 | 0,1193/0,3881/0,1508 | **sim** |
| `test7` | 0,4 | 0,1432/0,2931/0,1417 | idem | **sim** |
| `test8` | 0,4 | 0,1595/0,2509/0,1692 | idem | **sim** |
| `test9` | 0,5 | 0,0393/0,0682/0,0145 | idem | **sim** |
| `test3` | 0,5 | 0,2027/0,2872/0,0761 | idem | **sim** |
| `test4` | 0,7 | 0,0792/0,2915/0,0911 | idem | **sim** |
| `test5` | 1,0 | 0,0208/0,0395/0,0183 | idem | **sim** |
| `test6_repeat` | 1,0 | 0,0279/0,0422/0,0122 | idem | **sim** |

**0 divergências.** A implementação é a lei validada.

### ✅ A lei GENERALIZA a adoção vigente, não a substitui

Em δ = 1,0 mm a lei devolve `400·(1,0/1,0)` = **400** ⇒ `test5` e `test6_repeat` dão
**Δ = +0,0000 exato**. A adoção `CHU_2026_D1p0` é o **caso particular** da lei no ponto
de referência. Isso é o formato mais forte possível de compatibilidade: não é "quase
igual", é a mesma conta.

---

## 2. ⛔ Por que NÃO foi adotada

Aplicando **uma** entrada de fonte (`emb_depth`=3,0e-5 · `N_emb`=400 · `δ_ref`=1,0 mm)
às 8 curvas não-`test1`:

| curva | δ | nominal | com a lei | Δσ |
|---|---:|---|---|---:|
| `test9` | 0,5 | 0,0449/0,1173/0,0547 | **0,0393/0,0682/0,0145** | −0,0402 ⇒ **ENTRA** |
| `test2` | 0,4 | 0,1543/0,4639/0,1897 | 0,1193/0,3881/0,1508 | −0,0388 |
| `test4` | 0,7 | 0,1043/0,2708/0,1255 | 0,0792/0,2915/0,0911 | −0,0344 |
| `test7` | 0,4 | 0,1504/0,2485/0,1671 | 0,1432/0,2931/0,1417 | −0,0255 |
| `test8` | 0,4 | 0,1640/0,3456/0,1924 | 0,1595/0,2509/0,1692 | −0,0233 |
| `test5`/`test6` | 1,0 | — | — | **+0,0000 exato** |
| **`test3`** | **0,5** | 0,1381/0,1741/0,0369 | 0,2027/0,2872/0,0761 | **+0,0392 PIORA** |

**+1 no censo, 0 saem** — mas a `test3` piora **4× acima** da tolerância de +0,01 que
matou candidatos no D-AB. **Sob a disciplina vigente, a adoção reprova.** O gate
congelado manda, mesmo quando o saldo é positivo.

---

## 3. ⚠️ O achado que vale mais que o +1: o par de rugosidade do artigo

A nota de aparato (Tabela 1) **inverteu a minha leitura**: `Ra 0,4 µm` é a **linha de
base** (Tests 1–8) e `Ra 1,6 µm` é a variante **RUGOSA**, só o Test 9. Eu havia lido
`Ra1p6um` no nome do arquivo como espécime polido.

E `test3` × `test9` são **o par de rugosidade do próprio paper**: δ = 0,5 mm e
F₀ = 49 kN **idênticos**, só o acabamento difere (Fig. 3b). Como `emb_depth` é, por
construção, função da **classe de rugosidade** (tabela VDI 2230 f_Z), aplicar 30 µm às
duas aplica um nível fora de classe em uma delas.

### Decomposição: o dano na `test3` é do NÍVEL, não do relógio

| o que se injeta | `test3` | Δσ |
|---|---|---:|
| nominal | 0,1381/0,1741/0,0369 | — |
| **só** o relógio (`N_emb`=800) | 0,1072/0,1602/0,0430 | +0,0061 |
| **só** o nível (`emb_depth`=30 µm) | 0,2807/0,3152/0,0587 | +0,0218 |
| os dois (o grupo) | 0,2027/0,2872/0,0761 | +0,0392 |

⇒ **a lei é quase inocente** — sozinha ela até **melhora o MAE** (0,1381 → 0,1072). Quem
machuca é o nível fora de classe.

---

## 4. ⚠️ AUTO-AUDITORIA: a adoção de 3 horas atrás sobrevive, mas fica exposta

Se a lisa (Ra 0,4) quer embedding pequeno, então `test5`/`test6` — que são **a mesma
classe Ra 0,4** — não deveriam precisar de 30 µm. Medi contra mim mesmo.

**Bandas de `emb_depth` que servem, mesma rugosidade Ra 0,4:**

| curva | δ | banda medida |
|---|---:|---|
| `test1` | 0,3 | 1,6 µm (adotado, PR-38) |
| `test3` | 0,5 | melhor ≈ 1,6–2 µm — **e não fecha em nível nenhum** (MAE 0,0612 > 0,05; σ 0,0297 contra 0,0296, a **0,3 %**) |
| `test5` | 1,0 | **[25, ~50] µm** (fecha em 25/30/40; falha em 20 e em 60) |

**Os 30 µm SÃO necessários em δ = 1,0 mm.** Com a lei ligada e nível pequeno,
`test5`/`test6` **saem** do tripé (0,0943/0,1728/0,0584 e 0,0678/0,1268/0,0389 em
1,6 µm). E **nenhum nível único serve à família**: em 1,6 · 2,0 · 3,0 · 5,0 µm o
placar é **0 de 7** nas quatro varreduras.

### O que isso significa, dito sem alívio

O `emb_depth` desta fonte está absorvendo uma **dependência do ALVO com o
deslocamento** — não do relógio. O engine tem dependência de amplitude no alvo do
embedding (**ρ-unificação**, `emb_amp_exp`/`rho_ref_emb`, §4.18), mas o driver dela é
**razão de força**, e o CHU roda `F_amp` **constante em 19 600 N** nas cinco amplitudes
⇒ ρ é o mesmo nas cinco e a forma **não distingue** as condições. É a mesma lacuna que
motivou a lei do relógio, **um andar acima**.

### ✅ E a lei de potência óbvia para o alvo já está FALSIFICADA pelos 3 pontos

| trecho | razão de δ | razão de `emb` | expoente implícito |
|---|---:|---:|---:|
| 0,3 → 0,5 | 1,67 | ~1,1 | **0,19** |
| 0,5 → 1,0 | 2,0 | ≥ 12,5 | **≥ 3,6** |

**~19× de desacordo entre os expoentes.** Uma potência única em δ **não descreve** o
alvo exigido. ⚠️ Ressalva honesta: nível e forma são acoplados (lição D-Z), então estas
bandas são condicionais ao relógio da lei; o que a medição sustenta com firmeza é o
**salto de ≥12×** dentro da mesma classe de rugosidade — e *esse* número não tem
leitura benigna. Quando uma constante precisa mudar 12× dentro da sua própria classe
física, ela deixou de ser a constante que o nome diz.

---

## 4b. A variante "só o relógio, sem o nível" também foi medida — e ganha zero

O grupo de fonte podia levar **só** a lei (`N_emb`=400 · `δ_ref`=1,0 mm), deixando o
`emb_depth` no default e preservando o `CHU_2026_D1p0` para δ=1,0 mm. Isso resolveria
o problema do nível fora de classe. Os números já estavam medidos na decomposição:

| curva | só o relógio (`N_emb`=800, `emb` default) | veredito |
|---|---|---|
| `test3` | 0,1072/0,1602/0,0430 | **Δσ +0,0061** — dentro da tolerância de +0,01 ✅ |
| `test9` | 0,0451/0,0746/**0,0404** | melhora (−0,0143) mas **não fecha** (σ > 0,0296) |

⇒ **a variante limpa passa o gate e ganha 0 curvas; a variante que ganha 1 reprova o
gate.** As duas maneiras de escopar o grupo estão medidas, e nenhuma é adotável. Não é
que faltou tentar a versão elegante — ela foi tentada e o ganho é nulo, porque o que
traz a `test9` para dentro é o **nível**, não o relógio.

## 5. Por que não estreitei o grupo para pegar o +1

O conjunto que ganharia é {`test5`, `test6`, `test9`} = {δ=1,0 · Ra 0,4} ∪ {δ=0,5 ·
Ra 1,6}. **Nenhuma regra do artigo escolhe esse conjunto** — ele é definido pelo
resultado, não pela física. Montar a chave depois de ver o placar é **mover a trave**,
e é exatamente o que os gates congelados existem para impedir. O precedente é o D-AC,
onde a regra de escolha veio da Fig. 6 do paper e **derrotou** a alavanca de melhor σ
na curva-alvo.

## 6. Estado final

| item | estado |
|---|---|
| forma no engine | ✅ implementada, **default-inerte**, paridade 8/8 |
| testes | ✅ 4 invariantes, incl. **proibição de expoente ajustável** |
| adoção | ⛔ **não ocorre** — reprova o gate de não-piora |
| fingerprint | **inalterado** (`c37618c5cc96`) — nada de config mudou |
| censo | **141/205**, inalterado |

Precedente de formato: §4.52 (adoção per-rig LIU_2025 revertida pelo gate cego) —
*"rollback limpo; **a capacidade fica**"*.

## 7. O que fica na mesa, nomeado com precisão

**Dependência do alvo de embedding com o deslocamento imposto**, em rig de δ imposto
com `F_amp` fixo — irmã da ρ-unificação, um andar acima da lei do relógio. Com a
ressalva medida de que **não é potência simples**: qualquer candidato tem de explicar
por que o alvo é ~plano de δ=0,3 a 0,5 e depois salta ≥12× até δ=1,0. A hipótese que
isso sugere — **transição de regime** (parcial → gross slip) em vez de lei contínua —
é testável com a classificação mecânica por `resolve_transverse_slip`, e **não** foi
medida aqui.

## Reprodutibilidade

`chu_lei_engine.py` (paridade + fonte), `chu_decomp3.py` (decomposição nível×relógio +
varredura), `chu_autoaudit.py` (bandas por curva) no scratchpad. Só-leitura, controle
bit-idêntico, ~25 min.
