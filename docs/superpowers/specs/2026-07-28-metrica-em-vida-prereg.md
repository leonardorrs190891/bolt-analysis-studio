# Pré-registro — MÉTRICA EM VIDA no trecho vertical (mudança de métrica canônica)

**Data:** 2026-07-28 · **Autorização:** professor, "autorizado item 1 — métrica em vida no trecho vertical"
**Fingerprint vigente:** `4f5bedfbace4` (203 casos) · **Escopo:** campanha inteira, não uma fonte
**Status:** PROPOSTO — gates IMUTÁVEIS depois de assinados (§4.43)

> ## ⚠ O risco desta mudança, dito antes de medi-la
>
> Uma métrica nova que reclassifica falhas como passes é o caso de manual de
> **mover a trave**. E esta mudança é **unilateral por construção**: o resíduo
> novo é `≤` o vertical em **todo** ponto (§2). Logo, "melhorou" não é evidência
> de nada — a única pergunta legítima é **ONDE** ela melhora, e se aquele lugar
> é um lugar onde a métrica antiga estava, comprovadamente, medindo ruído.
> Os gates abaixo são todos sobre isso.

---

## 1. O que motiva (medido, não suposto)

`New_Theory/liu2025_ramp_v2_results.md` §6, na única curva da biblioteca cujo
colapso foi recuperado por re-digitalização fina (`fig2_single`, 134 pts):

- a forma acerta **6 de 7 cruzamentos em vida** (erro de **30 ciclos** entre
  `r`=0,60 e 0,50, numa curva de 9 789);
- e o tripé **vertical** falha assim mesmo (res.máx **0,337**);
- porque no rabo o dado cai de **0,20 a 0,104 em 5 ciclos**, de modo que
  `res.máx < 0,10` exige acertar a fratura em **±0,05 % da vida** — numa fonte
  com **44 % de scatter de espécime** e digitalização que resolve ±20 ciclos.

⇒ Não é falta de dado (foi recuperado) nem de física (a forma acerta): é a
métrica exigindo, num degrau vertical, precisão de cronômetro que o fenômeno não
tem. Classe **METRIC-LIMITED** (`MODEL_LEGITIMACY.md` §4.44a).

---

## 2. A forma proposta — uma fórmula, sem chave de regime

Para cada ponto do dado `i = (N_i, r_i)`, com a curva do modelo **densa e já
alinhada** (a mesma que a métrica canônica usa hoje):

```
d_i      = min sobre a curva do modelo de  sqrt( ((r_m − r_i)/σ_r)²
                                              + ((N_m − N_i)/σ_N(i))² )
resíduo_i = d_i · σ_r          [em unidades de r, para o limiar 0,10 seguir valendo]
sinal_i   = sinal( r_modelo(N_i) − r_i )        [convenção vertical, preserva σ_res]
```

com **`σ_r = 0,02`** e **`σ_N(i) = 0,03 · N_i`** — os erros de digitalização
**declarados** nas notas de aparato (`liu2025_scirep_M16.md`: *"±0.02 em F/F0 e
±3% no posicionamento de ciclo"*), adotados como **default de campanha**.
Classe de procedência: **input-de-paper**. Refinamento por fonte = follow-up
declarado, não parte desta adoção.

**Por que não tem limiar de regime.** Onde a curva é plana, o ponto mais próximo
do modelo está **na vertical** e a fórmula devolve **`|Δr_i|` exatamente** — a
métrica de hoje, bit-a-bit. Onde é quase-vertical, a fuga horizontal domina e o
resíduo vira `|ΔN|·σ_r/σ_N`, ou seja, **pontuação em vida**. A transição é
contínua e ditada pela inclinação local **do dado**, não por escolha de quem mede.

**Propriedade que cria o risco (declarada):** o candidato vertical sempre entra na
minimização, logo `resíduo_i ≤ |Δr_i|` **sempre**. A métrica só pode melhorar
números. Daí os gates.

**O que NÃO muda:** alinhamento (`align`), `FLOOR_TRIM`, `trim_n_max`, a janela de
métrica, a física, e o `engine_fingerprint()` (que hasheia o bloco `shared` +
configs adotadas — nada disso é tocado).

---

## 3. Implementação declarada

Campos **novos** em `CaseResult`, computados **sempre**, ao lado dos atuais:
`mae_life`, `maxerr_life`, `maxerr_life_at`, `resid_std_life`, `metric_sigma`.
Os campos verticais **permanecem** no store. Motivo: o delta tem de ficar
**visível e auditável** por curva, como a coluna "campanha" do report mestre
torna visível o gap de adoção. Nenhum número histórico é sobrescrito.

---

## 4. GATES (imutáveis depois de assinados)

**M0 — identidade onde a fuga horizontal é desprezível.** Em todo ponto com
`|dr/dN|·σ_N ≤ 0,1·σ_r`, exigir `|resíduo_life − |Δr|| ≤ 1e-6`. Falhou ⇒ bug de
implementação, PARA.

**M1 — curva plana não se mexe.** Para toda curva cujo `max_i(|dr/dN|_i·σ_N(i))`
seja `< 0,2·σ_r`: `|Δ MAE| ≤ 0,001` **e** `|Δ res.máx| ≤ 0,001`.

**M2 — discriminância preservada** (o gate que impede a métrica de virar brecha).
No núcleo `LIU_2025` + `fig2_single` fino, sob a métrica **nova**: a **rampa**
passa **e** as duas alternativas — **sem forma** e **cliff** — **continuam
falhando**. Se o cliff passar, a métrica deixou de distinguir formas ⇒ PARA.

**M3 — toda virada tem de ser atribuível a trecho íngreme.** Para cada curva que
vire falha→passe, o ponto que era o **máximo-residual sob a métrica antiga** tem
de estar em trecho com `|dr/dN|·σ_N > σ_r`. Uma única virada por folga em trecho
**raso** ⇒ PARA (é brecha, não correção).

**M4 — teto declarado de viradas.** Se **mais de 25** das 55 curvas hoje fora do
tripé virarem, **PARAR e reportar antes de qualquer adoção**: uma métrica que
resgata metade do que falta é suspeita **por construção**, não por resultado.
(Não é rejeição automática — é ponto de parada obrigatório.)

**M5 — fingerprint inalterado.** `engine_fingerprint()` continua `4f5bedfbace4`.
Mudou ⇒ algo indevido foi tocado, PARA.

**M6 — nenhuma curva PIORA.** Impossível por construção (§2); medir assim mesmo.
Qualquer piora ⇒ bug.

### 4.1 Interpretação pré-declarada

| resultado | leitura |
|---|---|
| M0–M3, M5, M6 ✓ e M4 ✓ (≤ 25 viradas) | métrica adotável; a meta passa a ser reportada nos dois eixos, com o delta por curva |
| M0–M3 ✓ mas **M4 ✗** (> 25) | **PARAR.** Reportar as viradas com o perfil de resíduo de cada uma; adoção volta a ser decisão do professor com o número na mão |
| **M2 ✗** | a métrica não distingue mais formas ⇒ **morre**, independentemente do resto |
| **M3 ✗** | há brecha em trecho raso ⇒ **morre** ou volta à prancheta |
| **M0 ✗** ou **M5 ✗** ou **M6 ✗** | bug de implementação; consertar e re-rodar, sem reinterpretar gate |

---

## 5. O que NÃO está sendo proposto

- **Não** substituir os campos verticais no store (ficam, para auditoria).
- **Não** mexer em `align`, `FLOOR_TRIM`, `trim_n_max` nem na física.
- **Não** revogar trim algum: a ratificação do §B segue de pé, e o efeito desta
  mudança sobre ela é medição posterior, não consequência automática.
- **Não** refinar `σ_r`/`σ_N` por fonte nesta rodada (follow-up declarado).
- **Não** adotar a forma da rampa do Liu 2025 — segue em falha parcial (G1 12/15).

---

## 6. Reprodutibilidade

```bash
py -3.12 New_Theory/metrica_vida_gates.py     # M0-M6 sobre os 203 casos
py -3.12 New_Theory/parallel_batch.py --workers 6 --store   # re-simula c/ campos novos
```
