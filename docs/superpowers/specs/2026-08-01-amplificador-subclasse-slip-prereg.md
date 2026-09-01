# Prereg — `k_dmg_all` na SUB-CLASSE dirigida por slip (escopo mecanicista)

**2026-08-01** · re-escopo do PR-3 após o G2 falhar 3/5. Gates antes de
qualquer novo número.

## Por que este re-escopo NÃO é gate-shopping

O critério de escopo é **mecanicista, verificável antes de medir o ganho,
e escrito no prereg anterior**: `D` só cresce com **dissipação por slip**.
Logo a forma é estruturalmente inerte onde a perda não é dirigida por
slip. Isso é decidível olhando o ENSAIO, não o resultado:

| fonte | δ imposto | perda dirigida por slip? | escopo |
|---|---:|---|---|
| JCSR_2023 | **0,0 mm** | não (creep + corrosão) | **FORA** — por definição do ensaio |
| LIU_2025 | 0,3 mm | não nesta amplitude (slip incubado por `slip_onset_W=250 kJ`, adotado) | **FORA** — por cfg adotado, não por resultado |
| YANG_2019 | 0,4 mm | sim | DENTRO |
| CHU_2026 | 0,4 mm | sim | DENTRO |
| SUN_2025_CRIMP | 0,3 mm | sim | DENTRO |

As duas exclusões saem de **δ=0** e de um **parâmetro adotado antes**
deste trabalho — nenhuma delas olha o MAE.

## Gates (imutáveis)

- **G1 (classe, bloqueante)**: com **UM** `k_dmg_all` por fonte, a soma
  dos MAE da fonte cai **≥15 %** em **≥2 das 3** fontes do escopo.
- **G2 (nenhum caso pior, bloqueante)**: nenhuma curva da fonte piora
  **>+0,01** em qualquer perna — incluindo as que já passam. É a barra
  dura: CHU tem 9 curvas, YANG_2019 tem 5, SUN tem 8.
- **G3 (procedência)**: o `k` por fonte é **lido**, não varrido — da razão
  entre a inclinação terminal do dado e a do modelo (o número que a
  classe já publica), arredondado a 1 casa. Varredura só para confirmar
  que o valor lido é o melhor da vizinhança, não para escolhê-lo.
- **G4 (sincronia)**: adoção ⇒ fingerprint muda ⇒ re-stamp uniforme +
  `exemplo_m12_sintetico` direto + censo/_VIVAS/docs/páginas/testes no
  mesmo commit.
- **INCONCLUSIVO**: se o `k` lido melhorar a fonte mas exigir valores
  diferentes por curva DENTRO dela, é o veredicto do CHU de novo —
  documentar e parar.

## RESULTADO — G1 e G2 falham nas TRÊS, e o padrão é o achado

| fonte | k lido | soma MAE | pioras >0,01 |
|---|---:|---|---:|
| CHU_2026 | 1,2 | 0,826 → 1,260 (**+53 %**) | 7 de 9 |
| YANG_2019 | 8,2 | 0,356 → 0,779 (**+119 %**) | 5 de 5 |
| SUN | 50,7 | 0,250 → 1,240 (**+397 %**) | 4 de 8 |

Zero fontes melhoram (G1 exigia ≥2). **Sem adoção.**

**Diagnóstico**: `D` cresce de forma **gradual** (0 → 0,9 ao longo do
ensaio), então `(1+k·D)` amplifica **a curva inteira**. Para consertar a
inclinação final é preciso `k` grande — e aí o início e o meio, que já
estavam certos, são destruídos. Não é magnitude errada: é **perfil
temporal errado**.

## EMENDA (declarada ANTES de medir): o perfil que falta já existe

Cruzando os dois resultados de hoje:

- `crash_trigger` tem o **perfil certo** (interruptor Hill nítido em
  `F_0/F_0_init`, ~0 cedo e ~1 tarde) e o **sinal errado** (≤1, suprime);
- `k_dmg_all·D` tem o **sinal certo** (>1, amplifica) e o **perfil errado**
  (gradual desde o início).

⇒ **A síntese não é palpite, é a interseção de duas medições**: amplificar
com o interruptor no lugar do acumulador —

```
dF_0_total ·= (1 + k_late_amp · g_switch)
g_switch = ft/(ft + (F_0/F_0_init)^k)      # o MESMO g do crash_trigger
```

Reusa `crash_trigger_frac`/`crash_trigger_sharpness` (já existentes, com
significado físico de limiar de perda de auto-travamento) e acrescenta
**um** número. `k_late_amp=0` ⇒ OFF exato.

### Gates da emenda

- **E0 (inércia)**: `k_late_amp=0` ⇒ array-equal.
- **E1 (perfil)**: com o interruptor em `crash_trigger_frac=0,85`, a
  amplificação nos primeiros 50 % dos ciclos tem de ser <10 % e nos
  últimos 10 % >50 % — é a definição operacional de "tardio".
- **E2 (classe)**: soma dos MAE cai ≥15 % em ≥2 das 3 fontes do escopo,
  **sem** nenhuma curva piorando >+0,01.
- Falhou ⇒ a classe fecha com spec precisa e **nenhuma forma adotada**.

### ERRATA do E1 — o valor que EU fixei era algebricamente inviável

Medido: com `crash_trigger_frac=0,85` o E1 **não pode** passar, e isso é
álgebra, não dado. O interruptor vale `g = ft/(ft+r^k)`; a razão entre a
amplificação tardia e a inicial é fixada por `frac`:

| `frac` | g inicial (r=1) | g final (r≈0,45) | razão |
|---:|---:|---:|---:|
| 0,85 | 0,214 | 0,993 | **4,6** |
| 0,60 | 0,0165 | 0,934 | **56** |

O E1 exige (>50 % tarde) com (<10 % cedo) ⇒ razão **>5**. Com 0,85 o teto
é 4,6 — **eu fixei um número que tornava o gate impossível**, e a 1ª
execução (k=6) só mostrou o runaway que isso força. Corrigido para
`crash_trigger_frac=0,60` (razão 56, folgada), **antes** de olhar
qualquer MAE. O k por fonte segue LIDO: `k = (razão_terminal − 1)/g_final`.

⚠️ Registro do erro: um gate com dois limites e um parâmetro pinado pode
ser **infeasible por construção** — conferir a álgebra do gate ao
escrevê-lo, não depois.

## Previsão registrada

O CHU deve ser o melhor caso (wear domina, D chega a 0,61) e o SUN o pior
(D = 0,019 — quase nada para amplificar). Se o G1 passar, será por
CHU + YANG_2019. **Risco declarado**: no CHU, `k` grande derruba o fim
para 0,115 contra 0,142 medido — pode fechar o fim e **estragar o meio**,
que é o que o G2 pega.
