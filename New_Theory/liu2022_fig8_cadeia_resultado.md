# Cadeia de reapertos do fig8 — a TENDÊNCIA é falsificada, e o t4 é fratura

**2026-08-04** · prereg `2026-08-04-liu2022-fig8-cadeia-prereg.md` (decisão
D-E, por delegação). Fingerprint `63722b266dc0`. **NADA FOI ADOTADO sob este
prereg.** Sonda: `New_Theory/liu2022_fig8_cadeia_probe.py`.

## Veredicto: FALSIFICADO (a tendência), com número

**G1 falha em 10 de 10 parametrizações.** Nenhuma dose de nenhum dos 5
candidatos (`k_wear_spec`, `emb_depth`, `k_emb_renew`, `c_D`, `k_dmg_wear`)
produz a queda monotônica de retenção que o dado tem.

E a falha é **quantificada**, não binária. A única direção que produz alguma
tendência decrescente em t1→t3 é `k_wear_spec` **para baixo**: vão de
**0,0054** onde o dado tem **0,057** — a tendência do modelo é **10× fraca
demais**. As outras quatro alavancas produzem tendência **crescente**
(direção oposta à do dado).

## O relógio "contagem de reapertos" morre por contradição INTRA-FONTE

A forma que o defeito parecia pedir é uma taxa que cresça com o número de
reapertos. Medido nas **4 cadeias da mesma fonte** (mesmo rig, mesmo M12),
razão de perda por reaperto, só entre estágios de janela igual (5000 ciclos):

| cadeia | protocolo | razão por reaperto (dado) | modelo |
|---|---|---|---|
| `fig8_multi` | dry, multi | **1,78× · 1,99×** | 1,02× · 0,99× |
| `fig7a_oil_direct` | oil, direto | **1,43× · 2,05×** | 0,95× · 1,01× |
| `fig6a_dry_release` | dry, release | 1,09× · 1,17× | 1,09× · 1,01× |
| `fig6b_oil_release` | oil, release | **0,75× · 0,93×** | 0,89× · 0,99× |

O dado varre de **0,75× a 2,05×** — duas cadeias **desaceleram** e duas
**dobram**. Um relógio por contagem de reapertos produz UMA direção; para
cobrir as quatro ele teria de ser **fitado por figura**, o que é ajuste com
nome de mecanismo. Mesma classe de morte da hipótese *front-loaded* do
LU_2024 (falsificada intra-fonte com 2 parametrizações).

## O que a contradição REVELA — e não é ruído

O agrupamento não é por lubrificação: é por **protocolo**. As duas cadeias
que **não liberam** o parafuso (direto/multi) dobram; as duas que
**liberam** (release), não. A nota de aparato dá o enquadramento do próprio
paper: *(i) direto ao torque* restaura só **88–90 %** de F0; *(ii) soltar
30°–60° e reapertar* restaura **~100 %** (método recomendado). E a mesma
nota já registrava a pergunta em aberto: *"retightening curves show whether
δ_emb should reset on retighten"*.

Perda no **1º reaperto**, por protocolo:

| | release | direto/multi | razão |
|---|---:|---:|---:|
| dry | 6,86 % | **2,22 %** | 3,1× menos |
| oil | 4,85 % | **2,78 %** | 1,7× menos |

⇒ **reaperto sem liberar perde MENOS**, nas duas lubrificações. O modelo usa
`k_emb_renew=1,0` (renovação TOTAL do assentamento) para todas as quatro
cadeias. Hipótese que isto abre, com procedência de protocolo e não de
figura: **sem liberar, a interface não re-assenta, logo δ_emb não renova.**
Segue para prereg próprio (D-F) — **não** é adotada aqui, porque este prereg
media a TENDÊNCIA e a tendência falhou.

## O t4 não é afrouxamento — é FRATURA, e já estava documentado

Os "9,96×" que apareceram na 1ª leitura são o **mergulho da fratura por
fadiga**. Procedência anterior a esta sessão, em três lugares:

* `validation_cases.py`: *"4th retightening — ends in FATIGUE FRACTURE at
  ~1500 cyc (trim)"*;
* nota de aparato: *"ends at the fracture dive (~78 % at 1,500 cycles), not
  a loosening endpoint"*;
* `CLAUDE.md`, gotchas: `liu2022_fig8_t4` nomeado entre as caudas de
  fratura **out-of-model**.

O cfg do grupo **não tem canal de fadiga** (`fatigue_enabled` ausente) ⇒ o
mergulho é inproduzível por construção. Isto é **escopo**, não forma. Duas
rotas, decididas por medição no D-F: declarar por escopo, ou ligar fadiga
com `N_f≈1500` **lido da nota** (precedente exato: adoção E2 do LIU_2025,
`N_f` como input-de-paper por curva, gates 7/7).

## Erro de instrumento que EU cometi e corrigi no meio

A 1ª normalização que usei para comparar estágios foi **janela comum em
N=1500**, para remover o confundimento de exposição (o t4 tem 1500 ciclos,
os irmãos 5000). Ela deu `1,00 · 0,95 · 1,72 · 9,96×` e a forma pareceu um
**limiar**. Estava errada: amostrar em N=1500 cai **dentro do transiente de
assentamento**, onde a razão mede a forma da curva, não a perda do estágio.
t1/t2/t3 **já compartilham** a mesma janela de 5000 ciclos, então a
comparação certa é a perda total de cada um: **2,22 % → 3,96 % → 7,91 %**,
razões **1,78× e 2,00×** — dobramento limpo. Tentando remover um
confundimento eu havia introduzido outro.

## Gates, um a um

| gate | resultado |
|---|---|
| **G0** (direção, 2 pontos) | ✅ 5 candidatos × 2 doses; **nenhum inerte**; instrumento validado (baseline re-simulado bate com o store a 1e-9) |
| **G1** (tendência decrescente, vão ≥0,08) | ❌ **0 de 10**; melhor caso 0,0054 = **10× fraco** |
| G2 (nenhum pior) | n/a — sem adoção |
| G3 (isolamento) | n/a — sem adoção |
| **G4** (≥2 das 3 entram) | ⚠️ **passaria** com `k_wear_spec` 3e-15→1,5e-15 (fecham 4/5) — **recusado**: ver abaixo |
| G5 (procedência) | ❌ para o G4: `k_wear_scale_tr=0,06` é o MESMO nas 4 cadeias (mesmo rig, mesmo parafuso). Baixá-lo só na fig8 significaria *"o coeficiente de desgaste depende de qual figura do paper o ensaio aparece"* |
| G6 (sincronia) | n/a |

**Ramo aplicado: FALSIFICADO + NÃO ADOTA (ajuste sem mecanismo).** O ramo
estava escrito no prereg antes de qualquer medição, exatamente porque este é
o caso: **+2 curvas no censo por um número sem procedência** é a compra que
parece progresso. O ganho existe e está medido; a recusa é deliberada.
