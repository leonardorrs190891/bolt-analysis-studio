# PR-3 — amplificador tardio AGNÓSTICO DE CANAL (`k_dmg_all`)

**2026-08-01** · autorização do professor: *"faça a opção mais robusta"*.
Gates escritos antes do código.

## Por que esta é a opção robusta

A classe exige agir sobre **o canal dominante de cada fonte** — e ele muda
(wear no CHU, rotacional no SUN, embedding+creep no YANG_2019, fadiga no
LIU_2025, creep no JCSR). Duas formas de atender:

| opção | como | por que NÃO / SIM |
|---|---|---|
| A — amplificar o canal escolhido por fonte | um `k` por canal, escolhido por quem calibra | ✗ **frágil**: exige atribuição *a posteriori* de "dominante" (a própria regra do repo diz que fatia no nominal **não** é cota de capacidade); multiplica parâmetros; escolha humana entra no fit |
| **B — amplificar o TOTAL da perda** | um fator sobre `dF_0_total`, governado por estado acumulado | ✓ **robusta**: nenhum canal precisa ser identificado — o fator multiplica o que os mecanismos produzirem, seja qual for; **1 número**; default inerte; funciona igual em fonte wear-pobre e wear-rica |

**B é escolhida.** É a mesma física do dano já validado
(`d_wear ·= 1+k_dmg_wear·D`), com o alvo corrigido: o dano degrada a
JUNTA, não só a face de apoio.

## A forma

```
dF_0_total ·= (1 + k_dmg_all · D)        # D = surface_damage já existente
```

- `k_dmg_all` novo em `JointMaterial`, **default 0.0 = OFF bit-idêntico**.
- Reusa `D` (estado já existente, alimentado por `c_D`/`W_ref`, com
  procedência) — **nenhum estado novo**.
- **`dF_0` sim, `dE` não** — o padrão exato do `k_dmg_wear` (CLAUDE.md):
  a energia dissipada segue sendo o trabalho real; a perda extra de
  pré-carga é contabilizada via `U_released`. Amplificar `dE` junto
  quebra conservação (~40 % de residual, medido em 2026-06).

## Gates (imutáveis)

- **G0 (inércia)**: `k_dmg_all=0` ⇒ trajetória **array-equal** à de hoje;
  suíte completa sem regressão.
- **G1 (conservação)**: com o amplificador ligado, `conservation_residual`
  na mesma ordem do que o engine já aceita (≤ ~1 J na escala das sondas) —
  se explodir, a rota de `U_released` está errada e PARA.
- **G2 (direção, 2 pontos)**: `k_dmg_all` ∈ {2, 8} tem de **baixar o fim**
  da curva em **≥4 das 5** fontes da classe (o `crash_trigger` fez 0/5 e o
  dano-no-wear 1/5 — a barra é ser agnóstico de canal).
- **G3 (classe)**: com **um** valor por fonte, soma dos MAE da fonte cai
  ≥15 % em **≥2 fontes independentes**.
- **G4 (nenhum caso pior)**: nenhuma curva da fonte piora >+0,01 em
  qualquer perna.
- **G5 (procedência)**: `k_dmg_all` por rig lido do dado (razão entre a
  inclinação terminal medida e a do modelo — o número que a classe já
  publica), não varrido às cegas.
- **G6 (sincronia)**: adoção ⇒ fingerprint muda ⇒ re-stamp uniforme +
  censo/_VIVAS/docs/páginas/testes no mesmo commit.
- **INCONCLUSIVO**: se G2 passar e G3 falhar, a forma age mas não é
  classe — documentar, deixar no engine inerte, não adotar.

## Previsão registrada

Como D cresce com a dissipação por slip, fontes de **creep puro**
(JCSR 82 % creep, sem slip transversal) podem ter **D ≈ 0** e o
amplificador nasce inerte lá — seria o limite honesto da forma, e
apareceria no G2 como "age em 4, não em 5". Registro isto agora para não
parecer descoberta depois.
