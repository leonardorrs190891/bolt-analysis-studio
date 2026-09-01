# Amplificador com INTERRUPTOR — E2 falha; a classe fecha com spec completa

**2026-08-01** · emenda do PR-3 (prereg
`2026-08-01-amplificador-subclasse-slip`). Terceira e última variante
testada hoje. **Nenhuma adoção**; censo `129/205`, fingerprint
`a410d6537c83`, suíte **881/1**.

## A síntese que a medição sugeriu (e por que não era palpite)

- `crash_trigger`: perfil temporal **certo** (interruptor nítido, ~0 cedo
  / ~1 tarde), sinal **errado** (≤1, só suprime).
- `k_dmg_all·D`: sinal **certo** (>1), perfil **errado** (gradual — G1
  falhou com +53 %/+119 %/+397 %).

⇒ amplificar **com o interruptor**: `dF_0 ·= (1 + k_late_amp·g_switch)`,
reusando `crash_trigger_frac/sharpness`. Um número novo, OFF exato.

## Meu erro de gate, achado pela álgebra antes do dado

O E1 que escrevi pinava `crash_trigger_frac=0,85` e exigia razão
tardio/inicial **>5**. Mas essa razão é fixada pelo próprio `frac`:

| `frac` | g inicial | g final | razão |
|---:|---:|---:|---:|
| 0,85 | 0,214 | 0,993 | **4,6** ⇒ gate impossível |
| 0,60 | 0,0165 | 0,934 | **56** ⇒ folgado |

**Escrevi um gate infeasible por construção** e a 1ª execução (k=6) só
mostrou o runaway que isso força. Corrigido para 0,60 **antes** de olhar
MAE. Lição: conferir a álgebra do gate ao escrevê-lo — dois limites mais
um parâmetro pinado podem se contradizer.

## E2 (o gate de classe) — FALHA

Interruptor em 0,60, `k` **lido** por fonte (`(razão−1)/g_final`):

| fonte | k | soma MAE | melhoram | pioram >0,01 |
|---|---:|---|---:|---:|
| CHU_2026 | 0,9 | 0,826 → 0,824 (**−0 %**) | 5 | 3 |
| YANG_2019 | 8,3 | 0,356 → 0,431 (**+21 %**) | 0 | 3 |
| SUN | 1,0 | 0,250 → 0,412 (**+65 %**) | 2 | 4 |

Zero fontes com −15 %; nenhuma sem piora. **E2 falha ⇒ sem adoção.**

O CHU é o caso instrutivo: **5 curvas melhoram e 3 pioram**, soma
empatada. O interruptor acerta a forma de algumas e estraga outras da
MESMA fonte com o MESMO `k` — é a assinatura de "não é constante
per-rig", o mesmo veredicto que a grade de 54 pontos deu lá.

## Fecho da classe — o que ficou provado hoje

A classe "aceleração tardia" (7 fontes, 21 curvas) tem agora **três
falsificações com mecanismo nomeado**:

1. **Gates Hill** (`slip_onset`, `conformation`, `slip_regime`,
   `self_locking`, `crash_trigger`): contradomínio (0,1] — **só atrasam**.
2. **Amplificador por acumulador** (`k_dmg_all·D`): sinal certo, **perfil
   gradual** ⇒ estraga início e meio para consertar o fim.
3. **Amplificador por interruptor** (`k_late_amp·g`): sinal e perfil
   certos, mas **o valor não é per-rig** — dentro da mesma fonte umas
   curvas melhoram e outras pioram.

**Especificação final para o PR-3 do professor** (o que uma forma teria de
ter, tudo medido): amplificar (>1) · perfil tardio (interruptor, não
acumulador) · e **um relógio que não seja nem `D` nem `F₀`** — porque `D`
é gradual demais e `F₀` realimenta o que está sendo amplificado
(bifurcação medida: k≥3 leva a zero em 30 ciclos). O candidato natural é
um relógio **por curva** (fração de vida), que é *input de paper*, não
constante de rig — a mesma rota que resolveu o estágio 3 do LIU_2025
(`N_f` como input, §4.53).

As duas capacidades ficam no engine, **default-inertes e testadas**
(9 invariantes), disponíveis se o professor autorizar a rota do relógio.
