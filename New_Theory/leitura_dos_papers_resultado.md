# "Leia os papers" — a leitura já estava feita, 2026-08-25

**Pedido do professor**, em resposta a eu ter dito que declarar a procedência das 147
entradas `per_case` exigia ler os papers.

**Era o diagnóstico errado, e o meu.** Medido: as 147 já têm procedência documentada — em
preregs, em documentos de resultado e na síntese `metodo_leitura_de_constantes.md`. O que
faltou foi **transcrever** para o campo `prov`, que é o único lugar que a máquina lê.

Fingerprint intocado (`db7de97e682a`): nada foi escrito no config.

---

## 1. A prova, num exemplo

Do PR-28 (`specs/2026-07-11-mem-iter4-preregistrations.md`, l. 1801, de **15/jul**):

> `mu_thread/mu_bearing` POR CASO = **Fig. 10 locknut digitalizada (input-de-paper)**:
> N=2:0,158, 4:0,186, 6:0,198, 8:0,245, 10:0,279.
> `loose_arrest_floor` POR CASO **lido do platô final da própria curva**.
> `emb_um` POR CASO **lido da queda em N=500** com subtração do front do modelo.

Os cinco números de μ estão no `adopted_configs.json` **sem `prov`**, e a frase que os
justifica tem seis semanas. Abrir o PDF do Sun para redescobrir isso seria refazer trabalho
feito — e a regra registrada neste repo é que **a porta mais barata é procurar o que já foi
medido**.

## 2. A decomposição, que muda o tamanho do problema

| classe | n | o que é |
|---|---:|---|
| **zero estrutural** | **45** | `s_crit_loose=0`, `emb_depth=0`, `C_creep=0`… — **não são constantes fitadas**, são canais **desligados**. A procedência é a decisão de desligar |
| **modo** | **18** | `loose_rate_mode="graded_scrit"` — string, escolha de **forma**, não valor |
| **valor** | **84** | os que pedem procedência de verdade |

⇒ **"147 constantes sem procedência" era leitura errada do próprio número.** 63 delas não
são constantes: 45 são canais em zero e 18 são seletores de forma. Isto muda a leitura do
DOF publicado — e é o segundo número deste projeto que eu havia publicado sem separar as
classes (o primeiro foram os *"40 grupos de uma curva só"*, que eram **10**).

## 3. A colheita: 147 de 147, zero pendente

`New_Theory/colheita_de_procedencia.py` → `procedencia_colhida.json` (74 pares
grupo×campo cobrindo as 147 entradas grupo×token×campo — `prov` é chaveado por campo).

**Cada entrada cita o documento; sem citação, não entra.** Fontes usadas:

| documento | o que ancora |
|---|---|
| PR-28 (15/jul) | μ do SUN por remontagem, `emb_um` por leitor canônico |
| P-13 prereg (20/ago) | `loose_F_exp`/`k_loose_graded` do YANG por LSQ ao F publicado, r² 0,9968–0,9999 |
| `rousseau_t10_ratchet_lido` | `free_spin_kin` = 1 − 920/3278 = 0,7195, do traço de rotação (r²=0,9997) |
| prereg zhang-fig3-runaway | `loose_runaway_frac`=0,25 **lido** (o paper define o fim do Estágio II em P=25 %) |
| prereg lu2024-amp1p5-aexp | `arrest_approach_exp`=1,864 **regredido** (r²=0,685), após o floor lido ser falsificado |
| prereg sun-ccreep-token | `C_creep`=9e-11 **estendido** do token da própria fonte — zero número novo |
| prereg lu2024-fig14-burst | o pacote `onset_burst_*`/`slip_onset_*`, fitado-declarado |
| `metodo_leitura_de_constantes` | a hierarquia de procedência e as 23 instâncias do arco 19–20/ago |
| `MODEL_LEGITIMACY` §4.7 | `k_wear_spec` por par tribológico; μ do DLC (0,126) medido na fonte |

**Distribuição da procedência colhida:** leitura/input-de-paper/regressão em **~24** pares,
zero estrutural em **25**, forma em **8**, fitado-declarado em **8**, e **9** referências
"idem" a uma entrada irmã que traz o texto completo.

⚠️ **Uma honestidade que a colheita força:** o μ=0,15 do `LIU_2020_WEAR` nos tokens `zinc` e
`af0.4` **não é leitura da fonte** — é o default 0,15 do bloco `shared`, herdado. Só o DLC
(0,126) é medido no paper. A procedência colhida **diz isso**, em vez de deixar os três
parecerem igualmente lidos.

## 4. ⚠️ Por que NÃO fundi ao `adopted_configs.json`

`engine_fingerprint()` hasheia `kb.adopted_config(s)` **inteiro** — `cfg`, `pack`, `prov` e
`verdict`. Acrescentar procedência **muda o fingerprint** e obriga a re-carimbar os **210**
registros do store. É operação de **adoção**, single-writer, e há sessão paralela ativa. O
`CLAUDE.md` já registra exatamente este caso:

> *"corrigir um RÓTULO de procedência dessincroniza hash↔store igual a uma mudança de `cfg`
> — toda edição de metadado do `adopted_configs.json` embarca no próximo re-stamp, nunca
> solta."*

⇒ **a colheita é o trabalho; a fusão é um passo separado**, que pede janela sem sessão
paralela e um re-carimbo de ~40 min. O artefato está pronto para ela.

## 5. O que isto destrava

A **tabela de constantes com procedência** — a que o plano de figuras (ITEM AC) identificou
como *"a que separa o artigo de um exercício de ajuste"* e que **não podia ser escrita por
inteiro**. Agora pode: 147 de 147, cada uma com a classe e o documento.

## Reprodutibilidade

```bash
py -3.12 New_Theory/colheita_de_procedencia.py   # imprime SEM procedência: 0
```

O script **não escreve** no config — só produz o mapa. A guarda
`tests/test_procedencia_colhida.py` reprova se aparecer entrada nova sem procedência
colhida, o que impede a dívida de voltar em silêncio.
