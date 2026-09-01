# ADOÇÃO D-Z — re-fit da FORMA do creep no JCSR: as 2 curvas fecham, e os 3 controles ficam **bit-idênticos**

**2026-08-09** · pedido direto do professor (*"solve the two cases … `jcsr2023_galv_seawater`;
`jcsr2023_plain_seawater`"*) · prereg `docs/superpowers/specs/2026-08-09-jcsr-forma-creep-prereg.md`
(gates congelados **antes** de medir).

## O que isto é — dito sem enfeite

**Não é física nova.** É **re-fit, numa grade mais fina, de duas constantes que o próprio
`adopted_configs.json` já declarava como `fitado-this-rig`**:

| constante | `prov` registrada antes desta adoção |
|---|---|
| `creep_alpha_sat` | *"fitado-this-rig (grade)"* |
| `creep_t_c` | *"seed = onset c da Eq.(2) do paper (input-de-paper) × ajuste fino 1,5–2× (fitado-this-rig)"* |

O kernel saturante já estava adotado (D-H) e o `C_creep` — o **nível**, que carrega o proxy
ambiental — **não foi tocado**. Mudou só a **forma**.

## Por que a forma, e não uma constante

O shell `ataque_curva.py` mediu nas duas, contra os limites vivos:

| | `galv_seawater` | `plain_seawater` |
|---|---:|---:|
| MAE | 0,0390 (**0,78×**) | 0,0289 (**0,58×**) |
| res.máx | 0,0966 (0,97×) | 0,0784 (0,78×) |
| **σ_res** | **0,0468 (1,87×)** | **0,0371 (1,48×)** |
| **viés** | **+0,0000** | +0,0047 |
| resíduo por terço | −0,044 / +0,007 / +0,043 | −0,027 / +0,021 / +0,025 |
| erro se forma nos ciclos | 7–10 | 10–15 |
| creep — perda absoluta total | **0,646** | **0,490** |

A `galv` tem viés **exatamente zero** e resíduo que **troca de sinal** ao longo do ensaio: o
nível está perfeito e só a forma está errada — a assinatura mais limpa de *"forma, não
constante"*. E as alavancas livres confirmaram: `C_creep` em 0,5–2,0× **piora em todas as
doses** (σ 1,74× a 4,46×), ou seja o nível já está no ótimo.

## Os valores adotados

| curva | antes (α, t_c) | **depois** | σ_res |
|---|---|---|---|
| `galv_seawater` | 3,0 · 1 373 760 | **3,0 · 1 717 200** (×1,25) | 0,0468 → **0,0154** |
| `plain_seawater` | 3,0 · 2 531 520 | **5,0 · 2 303 683** (×0,91) | 0,0371 → **0,0234** |

Ambos são **região**, não fio de navalha: **6 células** fecham na `galv` (α 2,5–4,0 × t_c
1,15–1,25×) e **5** na `plain` (α 5,0–6,0 × 0,88–0,91×). Grade de 2 constantes × 2 curvas,
sem tocar em mais nada.

## Gates — medidos

| # | gate | resultado |
|---|---|---|
| **J1** | as 2 alvo fecham o tripé | ✅ `galv` 0,0348/0,0526/**0,0154** · `plain` 0,0187/0,0480/**0,0234** (limite σ 0,0250) |
| **J2** | 3 controles não pioram (ΔMAE ≤ +0,01) | ✅ **ΔMAE = +0,0000 nos três — bit-idênticos** |
| **J3** | isolamento fora do `JCSR_2023` | ✅ Δ = **0,000000000** em 5 curvas de fontes distintas |
| **J4** | censo 139 → 141 | (abaixo) |
| **J5** | suíte completa | (abaixo) |

⚠️ **O J2 é o gate que importava, e ele veio no melhor formato possível.** A `plain_indoor` é
quase perfeita (0,0009/0,0021/0,0010) e era o canário: se um re-fit de forma a degradasse, o
ganho nas outras duas teria sido sobreajuste. Ela não mudou **nem no último dígito** — porque
as constantes vivem em `per_case`, e `per_case` casa por token do `case_id`. O resultado
bit-idêntico é a evidência de que o re-fit **não vazou** para as vizinhas.

## Erro meu no caminho, e como foi pego

O primeiro teste de transferência do kernel produziu **catástrofe** (σ de 1,87× para 9,45×; a
`plain_indoor` destruída). Catástrofe em curva que estava boa é assinatura de **teste
inválido**, e era — dois erros compostos:

1. **Nomes de campo errados**: usei `creep_sat_tc`/`creep_sat_alpha`; os reais são
   **`creep_t_c`**/**`creep_alpha_sat`**. O filtro de `JointMaterial` descarta chave
   desconhecida **em silêncio** ⇒ os dois overrides nunca chegaram ao engine.
2. **`t_0` errado** no fator de renormalização (`t_0_creep` não existe; o campo é `t_0`) ⇒ o
   default 1,0 entrou com `t_end` = 6,9×10⁶ s e o fator deu **48×**.

⇒ meu "teste do kernel saturante" fez **uma única coisa**: multiplicar `C_creep` por 48.

**Consequência de método, já instalada:** o `ataque_curva.py` guardava contra **inércia**
(`= nominal (INERTE)`) mas não contra **explosão**. Agora tem a guarda
`EXPLODIU (%.0fx o MAE)` — mudança catastrófica em curva saudável passou a ser sinalizada
como teste suspeito, não como resultado.

## O que fica registrado como limitação

O `α` da `plain` sobe de 3,0 para **5,0** — mudança grande numa constante de forma. O que a
sustenta: (a) a constante é `fitado-this-rig` **por registro anterior**, não procedência
travada; (b) há **região** de 5 células, não ponto; (c) o J2/J3 barram qualquer custo em outra
curva, e o custo medido foi **zero**.

O que isto **não** é: não é evidência de que o kernel saturante ganhou poder explicativo novo.
É a mesma forma, com as constantes onde deveriam estar desde o D-H.

## Reprodutibilidade

```bash
py -3.12 New_Theory/ataque_curva.py jcsr2023_galv_seawater
py -3.12 New_Theory/ataque_curva.py jcsr2023_plain_seawater
py -3.12 New_Theory/parallel_batch.py --workers 6 --store
```
