# Nenhum piso ATIVO repousa em chave cega — e a raiz das 6 retratações fica nomeada

**2026-08-15 (manhã)** · só-leitura · **nada retratado** · store `85e8104420b0`, censo
**141/205**. Resultado **NULO**, e é o resultado certo.

---

## 1. A pergunta, vinda da rodada anterior

O achado do `ECCLES` (2 exceções sobre piso já invalidado) apareceu **porque 2 das 22 provas
eram parseáveis**. A pergunta óbvia em seguida: **quantos outros pisos ativos repousam numa
chave que não separa as condições da fonte?**

## 2. ⚠️ A RAIZ das 6 retratações, nomeada

Nos seis casos, o "piso" media **dispersão entre condições que o artigo VARRE**, não
repetibilidade. E o motivo estrutural é sempre o mesmo:

> **a variável varrida não entra na config — ela vive só no NOME da curva.**

* `ECCLES_2010` — a carga axial (0 a 3,5 kN) não é campo de config. As **10** curvas caem
  numa **única** chave `(δ, F)`. A P-15 invalidou o piso por isso.
* `SUN_2025_CRIMP` — graxa × crimp não são campos. As 4 transversais caem numa chave só.
* `ICMEZ_2025` — o `grip_mm` **é** campo, e por isso este foi corrigido *na raiz* (G+H).

⇒ não é azar seis vezes: é propriedade estrutural, e é mensurável.

## 3. Medido: 13 fontes com a config "cega" — e **nenhuma** com risco vivo

Contando curvas por chave de família `(fonte, δ, F)`:

| fonte | curvas → chaves | piso ativo? | exceções que dependem |
|---|---|---|---:|
| `ECCLES_2010` | 10 → **1** | **None** | 6 |
| `JCSR_2023` | 5 → 1 | **None** | 1 |
| `LI_2022_MARSTRUC` · `QIN_2024` · `SUN_2025_CRIMP` | → 1 · 1 · 3 | **None** | 0 |
| `BAUER_2024` | 9 → 2 | 0,0933/0,2854/0,0900 | **6** |
| `LIU_2016` · `LIU_2022_RETIGHT` · `LI_2022_TRIBOINT` · `SUN_2025_REASSY` · `ZHANG_2018` · `ZHANG_2019` · `CACCESE_2009` | várias | ativo | **0** |

**Só o `BAUER_2024`** tinha piso ativo **e** exceções dependentes — o único candidato a risco
vivo.

## 4. ✅ E o `BAUER` é **falso alarme** — as suas "poucas chaves" são réplicas de verdade

A nota de aparato resolve em uma linha:

> `bauer2024_M8_fig6_rep1..rep6` (6) — M8, **20 kN**, **constant ~70 µm**
> `bauer2024_M12_fig8_test1..test3` (3) — M12×1.5, **50 kN**, spectrum 80/150 µm

São **duas condições, cada uma repetida**. Poucas chaves de config é o comportamento
**correto**: não há o que separar. O piso do BAUER é legítimo, e as 6 exceções que repousam
nele também.

⇒ **nenhum piso ativo hoje repousa em chave cega.** As fontes onde a cegueira é real
(`ECCLES`, `SUN_CRIMP`, `JCSR`, `LI_MARSTRUC`, `QIN`) **já têm piso `None`** — foram tratadas
pelas retratações anteriores.

## 5. ⚠️ A minha métrica precisou do segundo teste — 3ª vez nesta sessão

*"Poucas chaves de config"* é **flag**, não veredito: ela confunde **"a chave não vê
diferença"** com **"não há diferença"**. O discriminante é barato — a **nota de aparato** ou
o **nome da curva** (`rep1..rep6` diz réplica; `no_axial` × `axial_3p5kN` diz varredura).

É o **terceiro** caso do mesmo padrão nesta sessão:

1. a tupla de condição que ignorava graxa/crimp (marcou fatorial como réplica);
2. o veredito por diferença-de-conjuntos (um outlier fez o conjunto diferir);
3. esta.

**Sonda que não separa ausência de sinal de ausência de instrumento produz número plausível
e errado** — e nas três o conserto custou uma leitura.

## 6. O que fica como ferramenta

A contagem `curvas → chaves de família` é um **rastreio** útil: fonte com razão baixa merece
a pergunta *"isto é réplica ou varredura?"*, respondida pela nota de aparato. Vale rodá-la
sempre que uma **fonte nova** entrar ou uma família for criada — é onde as 6 retratações
teriam sido evitadas antes de virarem assinatura.

## Reprodutibilidade

`audit_excecoes2.py` no scratchpad + as contagens inline. Só-leitura, ~1 min.
