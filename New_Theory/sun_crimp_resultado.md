# SUN_2025_CRIMP — o dado é EXPONENCIAL PURO e o modelo só sabe desabar ou parar

**2026-08-06 (noite)** · campanha MARGENS fase A′, alvo "1 curva de fechar
100 %". Investigação só-leitura por subagente; store `5916d8be0510`. A conclusão
**inverte a premissa** que colocou esta fonte na fila.

## Veredicto: (b) — a digitalização está CERTA

Fig. 5 é raster nativo (1853×751 @300 dpi). Re-traço ponto-a-ponto contra o CSV
commitado, calibrado pelos ticks do próprio painel (1 px = 0,00163 em F/F₀):
**máx |Δ| = 0,0069 em F/F₀ na curva inteira** (média −0,03 kN). Âncoras
independentes conferem (platô crimp 2,90→2,11 kN bate o "≈2,8 kN" do texto; fim
do azul N≈664/0,415 kN). Separação das duas curvas no impresso: **34–240 px**,
ordens de grandeza acima da resolução ⇒ contaminação impossível.

**Não há colapso no dado em N=167. N=167 é onde o MODELO colapsa.**

## A causa: forma faltante, nomeada com número

* **Dado:** `ln(F/F₀)` vs N é **reta** — τ = 172,7 ciclos, **R² = 0,9961** nos 37
  pontos (1,0 → 0,028 = 3,6 e-folds). Taxa fracionária **constante**. Os autores
  dizem o mesmo, e atribuem a *"residual axial force"* (~2,8 kN) **só** à porca
  crimp.
* **Modelo:** log-taxa −0,0054 no início → **−0,0275 em N=130–141 (5× o dado)**
  → −0,0011 depois de N=167. Runaway no canal rotacional (68,8 % da perda) e
  **estacionamento no `loose_arrest_floor`**.
* Com floor = 0 (a física do paper para a porca padrão) o modelo **bifurca**:
  ganho ≤1,0 → final 0,65–0,70; ganho ≥1,5 → final **0,0000 exato**. Melhor de
  toda a varredura: 2,29×.

⇒ é o *"bifurcação arrest/zero, sem meio"* que o `CLAUDE.md` já registra — aqui
medido contra uma curva que vive **exatamente no meio**. **O engine não tem modo
de afrouxamento de taxa fracionária constante.** Forma, não constante.

## ⚠️ 6ª ocorrência da CHAVE CEGA — e a 1ª que CUSTA uma curva (executada)

`_pisos_medidos` chaveia por `(δ, F_amp, mode)`. No SUN **não existe par de
réplica válido**: toda família cruza uma variável varrida do artigo.

| família | n | o que de fato pareia | piso σ |
|---|---:|---|---:|
| δ=0,3 F=6000 | 4 | porca CRIMP × PADRÃO **e** COM × SEM graxa — **piso MAE 0,448** | 0,14077 |
| δ=0 F=7500 | 2 | crimp × padrão (axial 7,5 kN) | 0,03462 |
| δ=0 F=17500 | 2 | crimp × padrão (axial 17,5 kN) | 0,02340 |

Média por fonte ⇒ `limite_sres` = **0,06627 = 2,65× o global**. Um "piso" cujo
MAE é **0,448** não mede repetibilidade: mede a diferença entre os dois
tratamentos que o artigo compara.

**Custo medido, aceito e executado:** limite → 0,0250; a
`transverse_grease_crimp` **sai do tripé** (σ 0,0303 = 1,21×); fonte 7/8 → 6/8;
censo **139 → 138**. As 5 ocorrências anteriores foram inócuas; esta não é.
Executada assim mesmo — afrouxar a 3ª perna com um piso desses é o oposto do que
ela existe para fazer. Precedentes de perda por correção: retratação CACCESE e a
saída da `yang2021_r1` no D-U.

**⇒ a premissa da fase A′ estava invertida nesta fonte: consertar o piso CUSTA
uma curva, não ganha.**

## Duas armadilhas medidas (nenhuma adotada)

**1. `loose_arrest_floor = 0,20` "PASSA" o tripé (0,86×) fitando a JANELA.** Ele
estaciona o modelo em 3,0 kN enquanto o dado bruto desce a **0,42 kN** — os 8
pontos de N=405→664 (ratio 0,093→0,028) são invisíveis por causa do
`FLOOR_TRIM=0,10`. **Regra que isso gera:** piso lido para esta curva tem de ser
lido contra a **assíntota BRUTA (0,028)**, não contra o que a métrica enxerga.

**2. `arrest_approach_exp` fecharia** (exp ∈ [4,5; 6,5], 5 células contíguas;
melhor 5,5 → 0,0429/0,0819/0,0422, pior perna 0,86×) — **mas a irmã falsifica a
leitura de física compartilhada**: o mesmo expoente aplicado à `grease_crimp`
(mesmo rig, mesmo painel, mesma lubrificação) a destrói monotonicamente
(0,0221 → 0,0718 → 0,1542 → 0,1989). Seria `fitado-this-CURVA`, num parâmetro
de forma cujo único gate anterior **FALHOU** (prereg do grupo A, 2026-07-27),
para compensar um piso (0,06) que o artigo diz **não existir** nesta porca.
Não adotado.

## PROPOSTA (não executada — reclassificação exige assinatura)

**`SUN_2025_CRIMP` é falso positivo em `_FONTES_CLASSE_PARADA`.** A entrada veio
da razão de inclinação terminal (n=1, razão 25,1; reproduzida: 25,0). Mas a
inclinação terminal do modelo é ~0 **porque ele está ESTACIONADO no piso desde
N=167**, não porque falta acelerar — a métrica não distingue *"nunca acelerou"*
de *"já desabou"*. Corroboração independente já no repo:
`kernel_diagnostic_2026-07-27.md` mede esta curva em **r = −0,74 a −0,78**
contra a forma do grupo A — ela é o **espelho** da classe. E o remédio da classe
está falsificado nela em 4 doses (`crash_trigger_frac` 0,85/0,70/0,50/0,30 →
piora monotônica até 0,2408/0,5846/0,1882).

⇒ o charter manda: reclassificação de camada da triagem é **proposta**, nunca
edição sem assinatura. Fica aqui, com os números.

## Auditoria de input: limpa (e uma contradição do paper resolvida)

F₀ 15 kN ✓ · 12,5 Hz ✓ · sem `x_scale`/`x_offset` ✓ · sem trim. O paper se
contradiz no δ (§2.2 = 0,30 mm; §2.1 = 0,50 mm); o registry usa 0,30 e
**medir 0,50 piora 2,4×** (0,2412/0,5099/0,1544) e estraga a irmã ⇒ 0,30
confirmado. Token audit das 8: `_grease_standard` não casa `nogrease_standard`
— a armadilha de substring está corretamente fechada.
