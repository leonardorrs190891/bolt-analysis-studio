# JCSR `galv` e `plain` atacadas — e a forma que eu ia propor **já está lá**

**2026-08-09** · shell `New_Theory/ataque_curva.py` (novo, reutilizável) ·
**nada adotado**.

## O diagnóstico das duas, pelo shell

| | `galv_seawater` | `plain_seawater` |
|---|---:|---:|
| MAE | 0,0390 (**0,78×**) | 0,0289 (**0,58×**) |
| res.máx | 0,0966 (**0,97×**) | 0,0784 (**0,78×**) |
| **σ_res** | **0,0468 (1,87×)** | **0,0371 (1,48×)** |
| **viés** | **+0,0000** | +0,0047 |
| resíduo por terço | −0,044 / +0,007 / +0,043 | −0,027 / +0,021 / +0,025 |
| erro se forma nos ciclos | **7–10** (u=0,09) | **10–15** (u=0,12) |
| creep — perda **absoluta** total | **0,646** | **0,490** |
| creep no incremento **tardio** | **0,000** | 0,0006 |

**As duas são sub-classe A**, só o σ viola, e a `galv` tem viés **exatamente
zero**: o nível está perfeito e **só a forma** está errada — a assinatura mais
pura possível de *"forma, não constante"*.

E o creep faz **toda** a perda, **cedo**: o incremento do terço final vale
**0,010** e o creep contribui com **zero** dele.

## Alavancas: nenhuma livre fecha

`C_creep` em 0,5–2,0× piora em todas as doses (σ 1,74× a 4,46×) — a constante
está no ótimo. `creep_conform_exp` é **inerte em 0** e péssimo acima. Os canais
de wear, rotacional e arresto têm **capacidade ~0** e o shell os pula.

**Veredito do shell: candidata a FORMA, não a constante.**

## ⛔ A forma que eu ia propor JÁ ESTÁ ADOTADA — e a curvatura persiste

O padrão (creep dominante, modelo rápido demais cedo) apontava para o **kernel
de creep saturante** do **D-H**, cuja adoção registra explicitamente que a
reprovação anterior *"mediu 18 curvas TRANSVERSAIS onde creep não domina; esta é
a população oposta"*. O JCSR é população de creep dominante.

**Mas ele já está lá**, com constantes ajustadas por curva:

| curva | `creep_mode` | `creep_t_c` | `creep_alpha_sat` |
|---|---|---:|---:|
| `galv_seawater` | **saturating** | 1 373 760 | 3,0 |
| `plain_seawater` | **saturating** | 2 531 520 | 3,0 |
| `outdoor` | saturating | 12 830 400 | 5,0 |
| `stainless_seawater` | saturating | 4 268 160 | 5,0 |
| `indoor` | log (`t_0`) | — | — |

⇒ **a curvatura do JCSR sobrevive ao kernel saturante já ajustado.** Isso é
resultado: elimina o candidato mais óbvio para a sub-classe A e mostra que o
defeito é de outra natureza.

## ⚠️ Dois erros meus no caminho, compostos — e como foram pegos

O teste de transferência produziu resultados **catastróficos** (σ de 1,87× para
**9,45×**; a `plain_indoor`, que era quase perfeita — 0,0009/0,0021/0,0010 —,
destruída). Catástrofe é assinatura de **teste inválido**, e era:

1. **Nomes de campo errados.** Usei `creep_sat_tc` / `creep_sat_alpha`; os reais
   são **`creep_t_c`** / **`creep_alpha_sat`**. O filtro de `JointMaterial`
   descarta chave desconhecida **em silêncio**, então esses dois overrides
   **nunca chegaram ao engine**.
2. **`t_0` errado no fator de renormalização.** Usei `ov.get('t_0_creep', 1.0)` —
   o campo se chama **`t_0`** —, então o default 1,0 entrou com `t_end` = 6,9×10⁶ s
   e o fator deu **48×** em vez dos ~21 do D-H.

⇒ meu "teste do kernel saturante" fez **uma única coisa**: multiplicar `C_creep`
por 48. Tudo o mais foi no-op.

**Lição para o shell:** ele guarda contra **inércia** (`= nominal`) mas não
contra **explosão**. Mudança catastrófica em curva que estava boa é o outro
sintoma de teste inválido, e merece guarda própria.

## O que fica

* **shell novo e reutilizável**: `py -3.12 New_Theory/ataque_curva.py <case_id>` —
  diagnóstico, onde o erro se forma, **capacidade absoluta** por canal,
  procedência de cada alavanca (TRAVADA/livre) e sonda de 2 pontos com veredito;
* as duas curvas do JCSR são **form-limited**, com o kernel de creep já no seu
  melhor;
* o candidato óbvio da sub-classe A (**kernel saturante**) está **eliminado**
  para esta fonte — ele já está aplicado.

## Reprodutibilidade

```bash
py -3.12 New_Theory/ataque_curva.py jcsr2023_galv_seawater
py -3.12 New_Theory/ataque_curva.py jcsr2023_plain_seawater
```
