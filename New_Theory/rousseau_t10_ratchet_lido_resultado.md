# `rousseau2025_steel_t10` — o traço de ROTAÇÃO publicado dá TODAS as constantes: 4,0× → 1,30× (passo 1) → **FECHA O TRIPÉ** (passo 2, gate regredido à taxa)

**2026-08-19 (noite)** · preregs `2026-08-19-rousseau-t10-ratchet-lido` (passo
1, melhoria) e `2026-08-19-rousseau-t10-taxa-regredida` (passo 2, fecho) —
gates congelados antes de cada um · mandatos: *"siga agora para
…steel_t10.html"* (18:5x) e *"trabalhe mais até atingir o tripé"* (19:13) ·
**resultado final: 0,0158/0,0324/0,0098 — TRIPÉ com folga ≥60 % nas 3 pernas**
(ver §7).

## 1. O que destravou a curva "transfer-limited"

O veredicto de 2026-08-15 (nenhuma constante compartilhada serve às 4 abertas)
está certo e **fica de pé** — mas media a pergunta errada. A fonte publica **a
rotação relativa parafuso-porca** (Figs. 4/5, eixo secundário) junto da
pré-carga, e isso muda o estatuto das constantes: em vez de compartilhar ou
fitar, **cada curva carrega as próprias leituras**.

Digitalizado hoje (da extração vetorial que já existia; traços de rotação nunca
tinham sido digitalizados — a nota de aparato os registrava como "available in
the PDF"):

| observável | valor | validação cruzada |
|---|---|---|
| θ_fim t10 | **10,92°** | 10,97° na leitura manual do §4.27 (−0,5 %) |
| θ_fim t12 | 4,36° | 4,23° idem |
| dF/dθ aço | **919,7 N/deg (r²=0,9997!)** | t12: 893,6 (3 % ⇒ lei da JUNTA) |
| dF/dθ HDPE | ~~117,9/117,0~~ **138 / 207 N/deg** | ERRATA §8 — varia com espessura |

CSVs novos na biblioteca: `rousseau2025_steel_t{10,12}_rotation_deg.csv`.

## 2. As DUAS capacidades que a leitura exigiu (TDD, default-inertes)

1. **`free_spin_kin`** (§4.56): o engine drena `k_b·lead` = **3278 N/deg** por
   rotação relativa — assume o laço rígido fora do parafuso. O rig mede
   **920**. A fração não-drenante é lida: `fsk = 1 − 920/3278 = 0,7195`.
   Física: rigidez de dreno = série do laço (parafuso + membro + compliances de
   interface); o HDPE muito mais mole confirma a estrutura QUALITATIVAMENTE
   (números corrigidos na ERRATA §8: 138/207 N/deg, variam com a espessura).
2. **`loose_amp_exp` no graded_scrit**: a docstring prometia e o ramo não lia
   (item R do lado do código; medido inerte). Implementado; `exp=1`
   bit-idêntico.

## 3. O pacote per_case — zero fit à métrica; as 3 pernas são PREDIÇÃO

| campo | valor | leitura |
|---|---|---|
| kernel | graded_scrit, s_crit=0 | forma existente; rotação arranca em N~16 |
| `free_spin_kin` | 0,7195 | dF/dθ ÷ k_b·lead |
| `loose_amp_exp` | 0,0 | θ(N) pós-onset LINEAR (r²=0,983) ⇒ taxa constante |
| `k_loose_graded` | 0,01394 | slope 0,0736°/ciclo ÷ 5,28 |
| `slip_onset_W` | 3,5465 J | W_acc no fim da folga de 1° (N=25; intercepto da reta F(θ) = 11,1 kN > F₀ ⇒ 1º grau não drena) |
| `emb_depth` | 0,0 | ponto PUBLICADO (20, 1,0000): zero queda em 20 ciclos |
| `C_creep` | 0,0 | mesma leitura de limite (≤0,5 % em 20 ciclos) |

**Resultado (canônico, ao dígito da sandbox):**

| perna | antes | depois | limite |
|---|---:|---:|---|
| MAE | 0,1548 (3,10×) | **0,0289** (0,58×) ✅ | 0,05 |
| res.máx | 0,2702 (2,70×) | **0,0668** (0,67×) ✅ | 0,10 |
| σ_res | 0,0994 (3,98×) | **0,0324** (1,30×) ❌ | 0,025 |

**Validação independente: θ_fim do modelo = 10,42° vs 10,92° medido (−4,6 %)** —
e o k NÃO foi fixado por θ_fim (veio da taxa). As **7 irmãs bit-idênticas**
(G2 ✓), incluindo a `steel_t10_amp0p2`, blindada pela entrada-vazia do matcher
(o token `steel_t10` é substring dela; teste-guarda `test_rousseau_t10_token`
fixa a ordem do dict).

## 4. O que fica declarado — o resíduo tem nome e número

- **A derivada do F publicado é um SINO**: sobe até 0,0099/ciclo em N=100 e cai
  a 0,0029 em N=170. O Hill⁴+taxa-constante dá subida mais abrupta e sem
  descida ⇒ a onda residual ±0,06 que segura o σ em 1,30×.
- **O dreno local CAI no fim**: 919,7 → ~500 N/deg entre θ=8° e 10,4° (contato
  de flanco parcial em F baixo). O `fsk` constante é a aproximação de 1ª ordem.
- **Floor lido 0,1086 RECUSADO**: o dado publicado o atravessa (último ponto
  0,0951) — regra da barreira artificial (§7 do doc ICMEZ). O floor 0,0 de
  APARATO do grupo fica.
- Re-leituras alternativas (meia-altura da derivada, k do pico, floor+aexp)
  foram **medidas e pioram** (0,065–0,184) — o pacote é o ótimo da estrutura
  disponível, e o que falta é FORMA (sino/dreno-variável), não constante.

## 5. Rota aberta para as irmãs (prereg próprio, não este)

As 2 abertas com traço θ (hdpe_t10/t12) têm a rota — com os números CORRETOS
da ERRATA §8 (re-extração do PDF por ticks): θ_fim = **21,27 / 12,65°**, dF/dθ
= **138 / 207 N/deg** (por CURVA no HDPE, não por junta). A pendência da
âncora-zero foi RESOLVIDA pela calibração absoluta (zeros 0,10/0,00/0,04°).

**Sonda preliminar na t12 (medida, SEM adoção):** o pacote ingênuo (fsk=0,9259
de dF/dθ + k do slope θ) dá 0,0566→**0,0328/0,0655/0,0362** (σ 1,45×) — e
zerar emb/creep PIORA 3× (0,1076): **a t12 PRECISA dos canais paralelos**
(baseline: emb 290 + creep 229 + wear 245 N), diferente da steel_t10 (dado
plano ⇒ paralelos ≈ 0). Isso expõe o refinamento necessário da leitura: com
θ ∝ N, a regressão F-vs-θ atribui à rotação o que os canais paralelos perdem
⇒ **o fsk deve ser lido da PARTIÇÃO** `dreno_rot = (ΔF_total − paralelos)/θ`
(≈147 N/deg ⇒ fsk≈0,948 na t12, usando o orçamento do grupo como partição
declarada). E o θ do modelo fica 39 % abaixo do lido (7,76 vs 12,65) — corte a
diagnosticar antes do prereg. A hdpe_t10 tem dado RUIDOSO (taxa local do CSV
até negativa — a Fb fina oscila no impresso): parte do σ dela (2,76×) pode ser
ruído do dado; medir o piso antes de atacar. A `steel_t10_amp0p2` não tem
traço θ publicado (Fig. 6) — sem rota de leitura hoje.

## 6. Reprodutibilidade

Sondas em `C:/Users/leo_r/.claude/jobs/3d12ac81/tmp/` (`sonda_rousseau_theta`,
`digitalizar_rotacoes`, `leitura_*`, `pacote_completo_t10`, `lsq_hill_taxa`);
engine `free_spin_kin` + exp-no-graded no commit da capacidade; testes
`test_free_spin_kin.py` (7) e `test_rousseau_t10_token.py` (4).

## 7. ✅ PASSO 2 no mesmo mandato: o gate REGREDIDO à taxa observada FECHA

O §4 nomeou o resíduo (sino da taxa) e o LSQ provou que ele não fecha sem a
descida: **Hill sozinho à taxa local dá r²=0,092**. A descida existe no engine
— o arrest gate — e a regressão COMPLETA
`taxa(N) = A·Hill(N; N50, s)·(1−floor/r(N))^aexp` com r(N) do DADO dá
**r²=0,891**:

| parâmetro (engine) | valor | origem |
|---|---|---|
| `k_loose_graded` | 0,05109 | A=0,02420 frac/ciclo da regressão |
| `slip_onset_W` | 12,7064 J | N50=89,5 (×0,142 J/ciclo) |
| `slip_onset_sharpness` | 1,89 | s da regressão |
| `loose_arrest_floor` | 0,0295 | **não-barreira** (≤0,0951 do último ponto publicado) |
| `arrest_approach_exp` | 8,0 | degenerescência (floor,aexp) declarada — só o produto 0,236 identifica; célula aexp=8 pelo precedente SUN, escolhida SEM a métrica |

Estatuto: **fitado-por-regressão a OBSERVÁVEL** (a taxa do F publicado) — as
3 pernas continuam predição. Resultado canônico:

| perna | passo 1 | **passo 2** | limite |
|---|---:|---:|---|
| MAE | 0,0289 | **0,0158** (0,32×) ✅ | 0,05 |
| res.máx | 0,0668 | **0,0324** (0,32×) ✅ | 0,10 |
| σ_res | 0,0324 | **0,0098** (0,39×) ✅ | 0,025 |

Resíduos ±0,02 na curva inteira; θ_fim 9,64° vs 10,92° (−12 %: o arrest corta
a rotação terminal e o ramo graded não tem free-spin PÓS-arresto — declarado).
**Vizinhança 8/8 fecha** (±10–20 % em k, W, floor, s) — região, não navalha.
Trajetória do dia da curva: pior perna **4,0× → 1,30× → 0,39×**, em dois
passos gateados — a MESMA estrutura do dia (SUN standard e LU T10).

## 8. ⚠️ ERRATA da mesma noite: a extração vetorial da fig4 estava CORROMPIDA

Ao preparar a rota das HDPE, a validação visual contra o impresso REPROVOU os
números da fig4 desta manhã: a rot t12 dava 23,2° na conta contra ~12,5° no
impresso, e a pré-carga t12 da polilinha terminava em 0,56 contra 0,346 do CSV
canônico. A extração vetorial da Rodada 4 (`rousseau2025_fig4_fig5_vector.json`)
é VÁLIDA na fig5 (3 âncoras externas independentes) e TRUNCADA/PARCIAL na fig4.

Re-extração DIRETO do PDF: o tracejado é atributo de estilo (`dashes`) do path
— separa rotação de pré-carga sem heurística — e a calibração é ABSOLUTA pelos
ticks de texto (0° @ y=209,75; 3,66 pt/deg; 0,455 pt/ciclo). Resultado
validado contra o impresso: **θ_fim HDPE = 21,27 / 12,65 / 2,16°**
(t10/t12/t14; zeros confirmados 0,10/0,00/0,04°). Com os θ corretos, dF/dθ do
HDPE = **138 / 207 N/deg** — VARIA com a espessura; o "117,9/117,0 idênticos"
publicado mais cedo era coincidência de DOIS artefatos da mesma extração.

**Nada da adoção da `steel_t10` muda** (a fig5 é a base e está validada).
Corrigidos por errata: docstring do engine, §4.56, VarSpec, prov da adoção,
CLAUDE.md e este doc. **Lição de método:** concordância entre duas curvas do
MESMO instrumento não valida o instrumento — só âncora EXTERNA (ticks, leitura
manual independente, CSV validado) valida. A minha "validação interna
t10↔t12 a 0,8 %" era exatamente essa armadilha.
