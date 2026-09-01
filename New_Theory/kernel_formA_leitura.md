# Leitura de forma do kernel A (pré-FAIL2) — o grupo encolhe para 9, e o FAIL1 ganha explicação mecânica

**Data:** 2026-07-28 · **Diagnóstico, não fit** — nenhuma tentativa de prereg gasta
**Store:** `294808504d83` (re-verificação §4.43 do diagnóstico de 2026-07-27, que era sob `4f5bedfbace4`)
**Scripts:** `kernel_formA_leitura.py` (+ JSON) — pós-processamento puro

---

## 0. Três achados, um deles explica o FAIL1

1. **A assinatura sobrevive ao re-baseline, mas a coerência era inflada por média de
   fonte.** O perfil médio segue monótono neg→pos (−0,093 → +0,143) sob o fingerprint
   novo ✓. Mas a correlação **par-a-par por curva** dá mediana **0,67** e mínimo
   **−0,98** — os "0,90–1,00" do diagnóstico original eram entre perfis **médios por
   fonte**, e a média escondia o espalhamento interno.
2. **A lei de taxa, quantificada:** na janela pós-assentamento, o dado tem
   `p_mediano = −0,29` (taxa de perda **acelerando** suavemente com N) e o modelo
   `p_mediano = +0,44` (**desacelerando**). O gap de forma é de **estrutura temporal**:
   o modelo perde cedo e se cala; o dado carrega a perda para o fim. O nome da fila
   ("kernel desacelerante") descrevia o sintoma pelo avesso.
3. **A mesma assinatura é carregada por TRÊS canais diferentes** — e isto explica o
   FAIL1:

| subgrupo | canal dominante no fim (decomp) |
|---|---|
| Chu2026 ×6 | **wear 93–94 %** |
| Karlsen ×1, Yang2019 ×2 | **rotational 50–86 %** |
| Zhang2006 ×1 | **creep 100 %** |

> **Por que o FAIL1 falhou a transferência, lido do store:** o expoente na comporta de
> arresto age **só no canal rotacional**. Chu (wear) e Zhang (creep) nunca poderiam
> responder — o G3 (ajustar em CHU, prever os outros) estava estruturalmente perdido
> antes de rodar. Qualquer candidato **dentro de um mecanismo** repete essa morte.

## 1. Cortes de membresia — o grupo honesto é **9**, não 13

| corte | motivo medido |
|---|---|
| `yang2019 amp0p6_5Hz` + `varamp_small_to_large` | **metric-limited terminais** (varredura L25: ±3 % de N vale 0,21/0,26 em r no pico) |
| `chu2026 test1` (D0p3) | **outlier de nível**, não de forma: o modelo perde **9,6×** o que o dado perde — problema de sobre-perda em amplitude sub-limiar |
| `zhang2006 fig3_illus` | **procedência sintética declarada** na nota de aparato (*"treat those 4 cases as synthetic until re-derived"*) e ensaio que **para sem afrouxamento total** — não pode ancorar forma |

**Núcleo honesto: Chu2026 ×6 + Yang2019 ×2 + Karlsen ×1 = 9 curvas, 3 rigs.**

## 2. O que isto exige de um candidato a FAIL2

- **Agir na estrutura temporal COMPARTILHADA**, não dentro de um canal — a forma tem
  de mover `p_modelo` de +0,44 na direção de −0,3 nos três canais dominantes ao mesmo
  tempo, ou no driver comum a eles.
- **Excluídos pela leitura** (além do expoente de arresto, morto no FAIL1):
  amplificação por dano (`c_D`/`k_dmg_wear`) — acelera só wear+µ, repete a
  canal-especificidade; **rampa de fratura** — canal-agnóstica e é o accelerant certo
  em tese, mas **sem procedência de N_f aqui** (Zhang para sem soltar; nenhuma nota do
  Chu declara fratura), e a lição E2 é que relógio preditivo está falsificado.
- **A pergunta que falta responder antes de propor** (barata, uma sonda): no Chu
  disp-mode, a taxa de wear do modelo é ∝ `µF₀·slip` com `F₀` caindo e `slip`
  crescendo (`slip = δ − µF₀/k_tr`) — **por que a competição resolve para
  desaceleração?** Se for o `F₀` vencendo, o candidato natural é a dependência de
  pressão/força da taxa de perda slip-driven (um expoente **compartilhado** por wear e
  rotational, que são ambos ∝ µF₀·slip) — uma forma só, no driver comum dos dois
  canais que dominam 8 das 9 curvas. Zhang saiu do grupo, então "creep" deixa de ser
  restrição.

## 3. Estado da fila após esta leitura

- Kernel A: alvo real = **9 curvas / 3 rigs**; FAIL2 ainda **não proposto** — falta a
  sonda da competição `F₀×slip` (§2), que decide entre "expoente do driver comum" e
  "outra coisa".
- `chu test1` → junta-se ao problema de **sub-limiar/sobre-perda** (parente do
  YANG_2023_IJPEM, bifurcação de limiar).
- `zhang2006` → **re-derivar da endurance real** antes de qualquer uso em forma
  (a própria nota manda).

## 4. Reprodutibilidade

```bash
py -3.12 New_Theory/kernel_formA_leitura.py   # (1) assinatura (2) lei de taxa (3) decomp
```
Resultado bruto: `kernel_formA_leitura.json`. Convenções idênticas ao runner
(vetores da métrica do store; decomp lida da grade amostrada — caveat declarado).
