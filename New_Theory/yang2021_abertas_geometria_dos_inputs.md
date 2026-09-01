# YANG_2021 `amp1p0` e `amp0p5` (alvos 3–4) — a geometria dos inputs FECHA a rota determinística, e o caminho revelou dois defeitos de registro

**2026-08-19** · store `7a60cacb72de`, censo 144/205 · sondas **só-leitura**,
instrumentos validados · **nada adotado** · sequência de ataque
(`PROMPT_ATACAR_AS_ABERTAS.md`), alvos 3 e 4 fechados juntos — o argumento é o
mesmo e é de estrutura, não de varredura.

## 1. O que fiz de diferente

A forma nomeada (`yang2021_stick_sustentado_resultado.md`) diagnosticou a fonte
(8/8 em stick; `gth` varrido: net zero). O que faltava: o diagnóstico **por
curva** da `amp1p0` — a única com carga axial nominal de 2 kN — e a pergunta
sobre o canal que ninguém sondou.

**Achado 1 — o canal tardio da `amp1p0` é o `gth`, não o rotacional clássico.**
O shell diz "rotational_loosening 87 % do incremento tardio", e sondei as
alavancas desse nome: `eta_loose`, `k_j_init`(+`kj_mode`), `phi_load_dep`,
`I_theta`, `tr_loose_gain`, `loose_arrest_*` — **Δ = 0 exato em todas, com os
companheiros ligados**. Lendo o ramo no engine: em disp-mode + stick, o
`RotationalLoosening.rate()` retorna pelo caminho **gth** (ratchet de stick)
antes de qualquer um desses parâmetros ser lido. O rótulo da decomposição é do
*mecanismo*, não da lei ativa. ⇒ gotcha novo da família "Δ=0 exige conferir o
RAMO, não só os companheiros".

## 2. O fechamento — geometria dos inputs, mais forte que qualquer varredura

Resíduo tardio (último terço, `pred − dado`) contra o único input que varia:

| δ (mm) | resíduo tardio | estatuto |
|---:|---:|---|
| 0,5 | **+0,070** | aberta |
| 0,6 (r1) | **+0,045** | aberta |
| 0,6 (r2) | **−0,052** | tripé |
| 0,6 (r3) | **−0,027** | tripé |
| 0,7 | −0,007 | tripé |
| 0,8 | +0,103 | exceção |
| 0,8 (fig2) | +0,104 | exceção |
| 1,0 | **+0,063** | aberta |

Dois fatos estruturais, nenhum contornável por forma:

1. **O sinal alterna três vezes** ao longo do eixo de amplitude
   (+ · ± · − · + · +), e as abertas (0,5 e 1,0) **cercam** as protegidas
   (0,6–0,7). Qualquer lei monótona de amplitude que dê mais taxa às pontas dá
   também ao meio — e o meio já tem resíduo negativo. Foi exatamente o que a
   varredura do `gth_k` mediu como *net zero*; aqui está o porquê.
2. **Réplicas nominais idênticas têm sinais opostos** (r1 +0,045 × r2 −0,052 ×
   r3 −0,027, mesma condição 0,6 mm/8 kN). Nenhuma função determinística dos
   inputs — amplitude, carga, pressão, o que for — pode separar curvas cujos
   inputs são **iguais**. É o teto da dispersão de espécime, o mesmo dos alvos
   1 e 2 (LU r1: vidas 12400/14649/16251; LIU fig2: vidas 9870/14400).

⇒ `amp1p0` (1,28×) e `amp0p5` (1,55×) ficam **abertas e sem rota
determinística**, com a prova mais curta da campanha: o alvo muda de sinal
dentro da mesma célula de inputs.

## 3. Achado 2 — o input axial do paper NÃO entra no modelo, e o registro mente a proveniência

No caminho, a tabela expôs: `F_amp_N = 5640` nas **oito** curvas, proveniência
*"literature (Pai&Hess 2002)"* — enquanto a Tabela 1 do paper (transcrita na
própria nota de aparato E no loop do registry, onde o `axkn` existe e vai só
para a *string* da nota) dá a carga axial **por ensaio**: 2,0 / 6,0 / 8,0 /
11,2 kN, senoidal, **90° defasada** do transversal.

**Medido com instrumento validado** (gancho em `settling_amplitude_factor`
confirmando o valor recebido): trocar 5640 → 2000 dá **Δ = 0 bit-a-bit**. O
porquê está no engine: `F_ax = |F_amp·cos(θ)|` e o caso é montado com
**θ = 90°** ⇒ F_ax = 0 ⇒ o fator retorna 1,0 por guard. O F_amp é
**estruturalmente inerte** em toda fonte transversal-pura — o valor errado não
distorce nada *hoje*.

Consequências, separadas com cuidado:

- **Correção de registro (documental, Δ=0):** a proveniência "Pai&Hess" está
  errada para esta fonte — o paper publica o valor. Corrigir é higiene, não
  mérito; entra na fila de dado, não muda métrica nenhuma.
- **Forma faltante honesta (não é rota para as abertas):** a excitação
  **composta** do rig (transversal + axial 90° defasada) não é representável na
  config — a componente axial cíclica não alcança nenhum canal. É limitação
  declarável do modelo para esta fonte. ⚠️ **E ela NÃO destravaria as
  abertas**: com o axial dentro, r1/r2/r3 continuam na mesma célula
  (0,6 mm/8 kN) com sinais opostos — o §2.2 sobrevive intacto.

## 4. Estado das curvas

| curva | pior perna | veredito |
|---|---:|---|
| `amp1p0mm_ax2kN` | 1,28× (σ; mx 1,07× também) | sem rota determinística (§2); canal tardio = gth, já net-zero |
| `amp0p5mm_ax8kN` | 1,55× (σ) | idem — mesma prova, mesmo cerco |

As duas seguem em `classe_parada`, agora com o **porquê estrutural** medido em
vez de herdado da classe.

## 5. Reprodutibilidade

Sondas de sessão: alavancas rotacionais com companheiros
(`kj_mode`+`k_j_init`, `loose_torsion_mode`+`eta_loose`, ...), leitura do ramo
gth no engine, mapa resíduo-tardio × inputs do store, gancho em
`settling_amplitude_factor` com validação do valor recebido. Nada escrito.
