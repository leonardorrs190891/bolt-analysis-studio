# ⛔ ERRATA 2026-08-17 (11:0x) — os números DESTE documento são IRREPRODUZÍVEIS

> Ele publicou **"38 das 205 curvas · 216 pontos · 12 fontes"** como o que o
> `FLOOR_TRIM = 0,10` descarta, **sem dizer qual definição usou**. Tentei reproduzir hoje
> contra o store `7a60cacb72de` e **não consegui**:
>
> | definição | curvas | pontos | fontes |
> |---|---:|---:|---:|
> | **(A)** todo ponto cru com ratio normalizado < 0,10 | **41** | **670** | 13 |
> | **(B)** só os que caem **dentro** da janela pontuada | 1 | 7 | 1 |
> | ~~publicado abaixo~~ | ~~38~~ | ~~216~~ | ~~12~~ |
>
> A **(B)** é degenerada **por construção** — a janela da métrica termina no último ponto
> sobrevivente, então ponto abaixo do piso quase nunca fica dentro dela. A **(A)** é a
> leitura direta. O **216 não é nenhuma das duas**, e não sei qual terceira definição usei.
>
> ⚠️ **Isto é pior que número errado.** Número errado se corrige; número cuja definição não
> se reconstrói **não é verificável por ninguém, incluindo quem o escreveu**. A lição:
> **contagem publicada carrega a definição no próprio texto**, não na cabeça de quem mediu —
> a mesma disciplina que `_SEM_FORMA_MOTIVO` e `_PARES_REPLICA_DECLARADOS` aplicam ao
> estatuto, e que faltou aqui na aritmética.
>
> ✅ **A contagem que vale hoje é a da sessão paralela** (`c34ef88`), porque ela **declara a
> causa**: das **82** curvas com janela menor que a curva — **32** por piso · **12** por
> `trim_n_max` · **8** por ambos · **30** por **efeito de borda** (último ponto da CSV um fio
> além do `n_max`). ⇒ **40 por piso** (32+8) contra os meus **41** da definição (A):
> diferença de 1, dentro do que critério de borda explica.
>
> ✅ **VERIFICADA independentemente em 2026-08-17 (11:5x)** — apontar um número como canônico
> sem medi-lo seria o mesmo atalho que produziu esta errata:
>
> | | eu medi | eles publicaram |
> |---|---:|---:|
> | janela menor que a curva | **82** | **82** ✅ exato |
> | `trim_n_max` | **12** | **12** ✅ exato |
> | ambos | **8** | **8** ✅ exato |
> | piso | 33 | 32 |
> | borda | 29 | 30 |
>
> Os totais batem **ao dígito**; o split piso/borda difere em **1**, e é **fronteira de
> classificação**, não erro — curva que mergulha abaixo do piso por um fio **e** tem ponto de
> borda cai num lado ou no outro conforme a ordem dos testes. ⇒ **a contagem deles é sólida,
> e o ponteiro para ela está justificado por medição, não por deferência.**
>
> **Sobrevive deste documento:** a natureza do achado — o `FLOOR_TRIM` encurta a simulação
> **e** a janela, e a queda em relação ao censo de 2026-07-29 é **composicional** (saída da
> `UFU_LAB`, entrada das corridas longas do `LU_2024`). **Os três números do título, não.**

---

# ~~O censo do `FLOOR_TRIM` estava 63 % errado nos pontos~~ — e a causa é composicional

**2026-08-15** · só-leitura · **nada mudado na física** · store `85e8104420b0`, censo do tripé
**141/205** (intacto).

Instância de **§4.43**: número publicado que envelheceu em silêncio. O `CLAUDE.md` afirmava,
medido em **2026-07-29**, que a convenção `FLOOR_TRIM = 0,10` põe fora de escopo

> *43 das 203 curvas … 588 pontos, 13 fontes — `ECCLES_2010` 56 pts, `UFU_LAB` 449,
> `LU_2024` 24, `YANG_2021` 6/6 com mínimo 0,000*

Dezessete dias e **vários re-carimbos** depois, ninguém re-mediu.

---

## 1. O que se mede hoje

Replicando a convenção **exata** do runner (`runner.py:465-485`) —
`r_all = r_all / max(r_all[0], 1e-9)` e depois `keep = r_all >= 0,10`:

| | publicado (07-29) | **medido (08-15)** | Δ |
|---|---:|---:|---:|
| curvas afetadas | 43 de **203** | **38 de 205** | −5 |
| **pontos descartados** | **588** | **216** | **−63 %** |
| fontes envolvidas | 13 | **12** | −1 |

## 2. ⚠️ A queda **não** é do modelo — é da população

Os pontos caíram muito mais que as curvas (−63 % × −12 %), e isso sozinho já denuncia
mudança de **composição**, não de física. As duas causas somam quase exatamente a diferença:

| evento | data | efeito |
|---|---|---|
| **`UFU_LAB` sai do projeto** ("a UFU não faz parte mais desse projeto") | 08-01 | **−449 pontos** em 3 curvas |
| **`LU_2024` ganha as 3 corridas `fig14_*_long`** (P4 do plano LU) | 07-31 | LU vai de 24 → **92+** pontos |

⇒ 588 − 449 + ~68 ≈ 207, contra 216 medidos; o resíduo é re-digitalização (D-W, D-R, D-S, D-U).

**Nenhuma leitura de mérito do modelo muda.** Quem lesse "588 → 216" como o modelo passando a
cobrir o colapso final estaria lendo a saída da UFU como melhoria de física.

## 3. Distribuição de hoje

| fonte | curvas | | fonte | curvas |
|---|---:|---|---|---:|
| `YANG_2023_IJPEM` | 6 | | `KARLSEN_2022` | 3 |
| `LU_2024` | 6 | | `YANG_2019` | 2 |
| `BAUER_2024` | 5 | | `YANG_2021` | 2 |
| `ECCLES_2010` | 5 | | `LI_2022`·`LIU_2025`·`ROUSSEAU`·`ZHANG_2006` | 1 cada |
| `SUN_2025_CRIMP` | 5 | | | |

As mais afetadas: `lu2024_fig14_amp0p5_long` (**63 pts**, mín. 0,0047) e
`eccles2010_fig8b` (**27 pts**, mín. **0,0000**).

## 4. O que continua verdadeiro

As três consequências práticas do gotcha **não** dependem do número e seguem de pé:

1. *"o modelo não pega a queda no fim"* tem **duas camadas** — abaixo de 0,10 **nada** é
   pontuado, em curva nenhuma;
2. sonda de **fratura** precisa baixar o piso, senão a fratura é **inobservável** (foi o que
   quebrou o G1 do prereg `a4f00ad`);
3. ao baixar o piso, os números **deixam de ser comparáveis** ao publicado.

⇒ o que envelheceu foi a **magnitude**, não o mecanismo. Mas a magnitude é o que se cita.

## 5. ⚠️ Este número **não está sob guarda**

O `test_meta_numeros_nao_envelhecem` cobre o censo do **tripé** (14/14 desde ontem). Este é
outro censo, e recomputá-lo exige ler as **CSVs cruas do disco** (~1 min), não o store — caro
demais para a suíte. Fica como **candidato declarado**, não executado: mesma classe das
**células de custo** que a auditoria de cobertura já identificou como desprotegidas.

## Reprodutibilidade

Sonda inline no corpo do commit; usa `load_full_curve` + `rh.caso_comparavel` e replica a
normalização do runner (`r/r[0]` **antes** do corte — foi conferido em `runner.py:465-485`
justamente para não repetir o erro de unidade das CSVs em porcentagem).

⚠️ **Honestidade sobre a própria sonda:** ela **hardcoda `0,10`** em vez de importar
`runner.FLOOR_TRIM`. É réplica, não leitura — se o limiar mudar, este número envelhece **sem
aviso**, exatamente como o de 07-29. Quem re-medir, importe a constante.
