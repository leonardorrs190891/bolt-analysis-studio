# LIU_2025 N₉₅ — instrumento construído, candidato A falsificado, forma B especificada

**2026-07-31 (noite)** · Bloco 1 do `plano_tripe_restante.md`, sob o prereg
`2026-07-31-liu2025-n95-forma-prereg.md` (gates imutáveis; G1 executado e
FALHOU pelo ramo declarado). Só-leitura + sondas com override de processo —
**nenhuma adoção, config canônico intacto**, fingerprint `3d432a65c7e8`.

## 1. O instrumento (a descoberta do dia)

O N₉₅ (ciclos até F/F₀=0,95) modelo-vs-dado, com o dado lido da **Fig. 4
D-N do próprio paper** (âncora independente das curvas da fila):

| amplitude | dado | modelo | razão |
|---:|---:|---:|---:|
| 0,25 | 16.157 | 108 | 150× cedo |
| 0,30 | 13.516 | 108 | 125× cedo |
| 0,40 | 9.099 | 108 | 84× cedo |
| 0,50 | 2.745 | 108 | 25× cedo |
| 0,60 | 460 | 108 | 4,3× cedo |
| 0,80 | 19 | 108 | 5,9× **tarde** |

**O modelo tem N₉₅ CONSTANTE onde o dado varre 850×.** O defeito não é
"adiantado": é d(N₉₅)/d(amp) ≈ 0 — relógio de estágio I cego à amplitude.
Decomposição em 0,25 mm: 11 % de perda já em N=2.000, **59 % embedding +
41 % creep**. É a assinatura quantitativa do P5 ("dispara 10–100× cedo"),
agora com forma funcional: o dado exige **expoente efetivo ~11** de
N₉₅ sobre amplitude (850× de span sobre razão 3,2×).

## 2. Candidato A (campos existentes) — FALSIFICADO no G1

Rota testada: bedding vibração-dirigido slip-gated (`emb_load_frac` +
`emb_slip_gate`, o padrão da adoção LU) + `emb_depth`↓ + onset de creep
`t_0`. Medido (grades + bissecção na ponta rápida, JSON
`liu2025_n95_g1_grid.json`):

- A supressão FUNCIONA em direção: com o reservatório fracional no lugar
  do de profundidade, o N₉₅ de 0,25 mm vai de 108 → ∞ (nunca cruza) — o
  relógio deixou de ser cego.
- A ponta rápida fecha: elf 1,0–1,5 dá N₉₅(0,8) = 25–17 vs alvo 19 ✓.
- **Mas as duas pontas não fecham JUNTAS**: melhor varredura = **1/6**
  dentro de 3× (gate exigia ≥4/6). Com elf=1,0: 0,4 mm dispara a 159
  (57× cedo — o gate não corta em amplitude média) enquanto 0,25/0,30
  nunca cruzam (creep+wear com t_0 não produzem os 5 % em 16 k).
- Causa estrutural, não de grade: o gate `(slip/(slip+δt))^q` tem
  expoente efetivo ~2–4 sobre amplitude; chegar a ~11 exigiria
  `emb_load_frac` > 1,5 ("mais de 150 % do F₀ consumível por bedding") —
  tortura de parâmetro, vetada pela disciplina de parcimônia.
- Armadilha reencontrada (2ª vez hoje): `emb_um` é chave de cfg, NÃO campo
  do engine — a 1ª grade rodou com o embedding intacto e Δ≈0. O campo é
  `emb_depth` (metros). Conferir SEMPRE contra
  `JointMaterial.__dataclass_fields__` antes de ler uma grade.

## 3. Ramo B — o que a forma de engine precisa ser (espec. p/ PR-3)

O comportamento medido é de **transição de regime** (parcial→gross slip
em torno de 0,5–0,6 mm para este rig): abaixo dela os relógios de
estágio I (bedding E creep) quase param; acima, correm 5× mais rápido que
hoje. A forma candidata: **gate de regime de slip nos relógios de
estágio I** — o análogo do Cattaneo-Mindlin que JÁ existe para
wear/loosening (onde é inerte porque aqueles canais carregam ~0 aqui),
aplicado a `EmbeddingLoss`/`CreepLoss` com sharpness alto ou bifurcação.
Requisitos medidos que a spec deve satisfazer: (i) N₉₅ span 850× nas 6
amplitudes; (ii) não tocar as fontes onde embedding/creep fecham hoje
(gate default-inerte, opt-in per-rig); (iii) compatível com E2/fadiga do
LIU_2025 (o colapso tardio já está certo). **Isto é PR-3 — autorização do
professor** (o PR-3 devolvido sem uso no arco LU cobre exatamente a
classe "forma nova de engine").

## 4. Estado da fonte após o dia

Inalterado por este bloco (nenhuma adoção): LIU_2025 7 com estatuto + 4
fila. O ganho é o INSTRUMENTO (N₉₅ vs D-N, reutilizável em qualquer
fonte com D-N publicada) e a falsificação limpa do candidato barato antes
de gastar uma forma de engine nele.
