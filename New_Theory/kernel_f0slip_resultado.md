# Sonda F₀×slip — o "expoente compartilhado" está MORTO na leitura, e o grupo A se dissolve

**Data:** 2026-07-28 · **Custo:** zero preregs (leitura) · **Store:** `294808504d83`
**Script:** `kernel_f0slip_sonda.py` (engine intacto, mecanismos default, 5 curvas instrumentadas)

---

## 0. Veredicto em uma linha

O candidato a FAIL2 "expoente `a` no driver comum `µF₀ᵃ·slip`" exigiria
**a = 2,17 / −1,20 / 4,45 / −0,96 / −216** nas cinco curvas instrumentadas —
**incoerente até dentro do próprio Chu** (2,17 vs −1,20 vs 4,45). Não existe
expoente compartilhado. O FAIL2 **não deve ser gasto nesta forma**.

## 1. O que a instrumentação mostrou (fatos novos de mecânica)

| curva | s_F₀ | s_slip | taxa wear | taxa rot | alvo (dado) |
|---|---:|---:|---:|---:|---:|
| chu test7 (0,4 mm/61 kN) | −0,38 | **+0,002** | −0,58 | +0,10 | −0,83 |
| chu test3 (0,5 mm/49 kN) | −0,35 | **+0,001** | −0,52 | +0,13 | **+0,42** |
| chu test4 (0,7 mm/49 kN) | −0,57 | **+0,001** | −0,69 | +0,22 | **−2,53** |
| karlsen (M30) | −0,39 | +0,32 | +0,10 | +0,51 | +0,68 |
| yang amp0p4 (M10) | −0,01 | **+1,09** | +8,2 | +7,9 | +3,80 |

1. **O Chu está em gross-slip profundo: o slip é CONSTANTE** (s_slip ≈ 0,001–0,002).
   Em 0,4–0,7 mm, `δ ≫ µF₀/k_tr`, então `slip ≈ δ − δ_free` e a desaceleração do
   wear do modelo vem **inteira** da queda de F₀ (taxa ~ F₀¹·slip⁰). A narrativa
   "F₀ cai × slip cresce competem" não se aplica ao Chu — só a Karlsen (+0,32) e
   Yang (+1,09), que estão na transição partial→gross.
2. **E o próprio DADO do Chu não compartilha lei de taxa**: test3 **acelera**
   (−0,42 → alvo +0,42), test7 desacelera (−0,83), test4 desacelera **forte**
   (−2,53) — amplitudes diferentes, cinéticas diferentes, **no mesmo rig**.
3. Yang amp0p4 é outro regime (taxas +8 no fim — beira de runaway/limiar), não a
   mesma física dos Chu.

## 2. A consequência honesta — o "grupo A" não sobrevive à leitura por curva

A cadeia do dia inteiro, em três degraus, cada um mais fino que o anterior:

| degrau | o que dizia | o que a medição fina mostrou |
|---|---|---|
| fila (2026-07-15) | "UMA forma fecha 26 curvas de 4 fontes" | eram 3 problemas (diagnóstico 27/07) |
| diagnóstico 27/07 | "grupo A coerente: 13 curvas, r = 0,90–1,00" | r era entre **médias por fonte**; por curva, mediana 0,67 (leitura de hoje) |
| leitura de hoje | "9 curvas, gap de estrutura temporal comum" | **nem a lei de taxa do dado é comum** — dentro do Chu, p_dado vai de −0,75 a +2,52 |

⇒ **A família "kernel desacelerante" era um artefato de agregação em três níveis.**
O que resta de real: (i) a assinatura *média* monótona neg→pos existe, mas é a média
de comportamentos heterogêneos; (ii) os fatos de mecânica do §1 (slip constante no
Chu; wear ∝ F₀ puro; regimes distintos por rig).

## 3. O que isto salva e o que isto pede

- **Salva o FAIL2**: duas formas candidatas morreram em leitura (arresto-expoente no
  FAIL1 real; driver-expoente aqui, de graça). A hipótese restante não é "uma forma
  para o grupo" — é **estudo por fonte**, começando pelo Chu (6 curvas, 1 rig,
  wear-dominado, slip constante), no molde do estudo Liu de hoje: reler o artigo,
  entender o que o F/F₀ do Ti faz que um wear ∝ F₀ linear não faz (as três cinéticas
  do §1.2 sugerem **regime dependente de amplitude dentro da própria fonte**).
- **Pede uma decisão de fila**: rebaixar o item "kernel desacelerante" de "1 prereg
  para 25→13→9 curvas" para "estudo Chu2026 (6) + diagnósticos separados
  (Karlsen 1, Yang 2)". O FAIL2 da hipótese-kernel fica **não gasto e reservado**.

## 4. Reprodutibilidade

```bash
py -3.12 New_Theory/kernel_f0slip_sonda.py   # ~1 min; engine intacto
```
Resultado bruto: `kernel_f0slip_result.json`. Janela pós-assentamento (>20 % N),
slopes em log-log; slip lido de `resolve_transverse_slip` (a função do engine).
