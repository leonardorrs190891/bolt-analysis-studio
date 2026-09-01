# Prereg — `fret_freq_exp` como lei de frequência do LI_2022, **pós-D-Q**

**2026-08-05** · decisão **D-T** (por delegação, MANDATO PERMANENTE) · gates
escritos **antes de qualquer execução**. Fingerprint de partida `b70276f2fa43`
(pós-D-Q e D-S). Motivação: `New_Theory/li2022_lei_frequencia_resultado.md`.

## Por que este teste existe

A fila form-limited é **1 curva** (`li2022ti_axialmin_10Hz`). A regra de parada
(`regra_de_parada_proposta.md`) exige que **todo** membro da classe seja
falsificado por **predição pré-registrada** antes de a classe ser encerrada. Hoje:

* **re-pesagem entre canais existentes** — FALSIFICADA por álgebra (teto do
  kernel log = 1,0753 mesmo a 100 % de fatia, contra alvo 2,009);
* **`fret_freq_exp`** — apenas **recusado por custo** numa medição anterior
  (`li2022ti_fret_freq_resultado.md`), sob config **pré-D-Q**. Não é falsificação.
* **kernel de creep** — fora de escopo desta sessão: raio de explosão sobre toda
  a população dominada por creep, decisão do professor.

Este prereg fecha o segundo item. **Não é proposta de adoção** — é o teste que
mata ou promove o candidato. Se ele passar, a adoção é outro prereg.

## O que muda, e por que o número não é escolhido por mim

`flank_wear_from_slip` tem expoente de frequência **explícito**. Da decomposição
pós-D-Q, o flanco carrega **9,3 %** da perda a 10 Hz. Para uma fatia `s` entregar
razão `r_alvo` com expoente `e`:

```
s·(f_hi/f_lo)^e + (1−s) = r_alvo
⇒ e = ln[(r_alvo − 1)/s + 1] / ln(f_hi/f_lo) = ln(11,80)/ln(2) = 3,57
```

O valor testado é **`fret_freq_exp = 3,57`** — **derivado da conta**, não varrido.
Isto é deliberado: uma varredura acharia o melhor placar; a conta pergunta se o
valor que a *física da atribuição* exige funciona.

## Predição registrada, ANTES de medir

1. **A razão de frequência do MODELO vai subir muito, mas ficará ABAIXO de
   2,009** — porque o expoente foi calculado sobre a fatia do flanco *no
   nominal*, e a decomposição é atribuição *a posteriori* de UMA parametrização,
   não cota de capacidade (regra medida em 2026-07-29 no `chu…test8`: uma
   alavanca que troca a LEI pode mover 13× a própria fatia). O sinal do erro é o
   que estou prevendo, não o valor. **Palpite: razão entre 1,5 e 2,5.**
2. **A `axial_10Hz_full` (curva longa, 330k ciclos) PIORA** — é a que a medição
   pré-D-Q reportou como destruída, e agora ela é a curva que o D-Q acabou de
   colocar no tripé com σ 0,0214.
3. **A `axialmin_20Hz` melhora** (precisa de menos perda; o expoente tira).

Se (1) sair >2,5 ou <1,2, minha leitura da atribuição está errada e o resultado é
**INCONCLUSIVO**, não falsificação.

## Gates (IMUTÁVEIS)

- **G0 (instrumento):** `fret_freq_exp` tem de CHEGAR ao engine (override
  presente em `_effective_overrides`) **e** o canal de flanco estar ligado
  (`flank_wear_on=1`). Sem isso, Δ=0 em bloco se lê como "inerte" quando é
  "nunca aplicado" — armadilha medida em 2026-08-01.
- **G1 (o gate que decide — a curva-alvo fecha?):** a `axialmin_10Hz` entra no
  tripé (MAE ≤ 0,05 **e** res.máx ≤ 0,10 **e** σ ≤ 0,025).
- **G2 (nenhuma aprovada sai):** as 3 curvas do LI_2022 que hoje passam
  (`axial_10Hz_full`, `axialmin_15Hz`, `axialmin_20Hz`) **continuam** no tripé.
- **G3 (nenhum caso pior +0,010):** nas 4 curvas da fonte.
- **G4 (isolamento):** `fret_freq_exp` é aplicado **só** ao LI_2022_TRIBOINT
  nesta medição; o LIU_2016 fica intocado e isso é **verificado**, não assumido.
- **G5 (a razão de frequência):** medir e registrar
  `perda_modelo(10 Hz)/perda_modelo(20 Hz)` contra o alvo **2,009**.

### Ramos

- **PROMOVIDO** — G1 e G2 passam ⇒ o candidato vive e merece prereg de adoção
  (que terá de tratar transferência: o `LIU_2016` também tem canal de flanco, e
  soltar `fret_freq_exp` só numa fonte é fudge por fonte).
- **FALSIFICADO** — G1 falha **ou** G2 falha. Registrar com número. Isto **fecha
  o requisito (b)** da regra de parada para este membro.
- **INCONCLUSIVO** — G0 falha, ou a predição (1) erra a faixa por muito: o teste
  não testou.

## O que este prereg NÃO faz

Não adota nada. Não toca `adopted_configs.json`, store, CSV ou reports. A rota é
**override** e a comparação é contra o store vigente, com o **mesmo `n_max`** nas
duas pontas (gotcha do `n_cap`: sonda capada contra store integral é
maçã-com-laranja).
