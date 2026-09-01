# Métrica por correspondência de nível — EXECUTADA e **REJEITADA**. A linha inteira fecha.

**Data:** 2026-07-28 · **Pré-registro:** `specs/2026-07-28-metrica-nivel-prereg.md`, gates **congelados em `3619af5`**
**Estado final:** implementação **REVERTIDA**; métrica canônica inalterada; store restaurado (203 casos, `4f5bedfbace4`)
**Antecessora:** `metrica_vida_results.md` (1ª tentativa, rejeitada por M2/M3)

---

## 0. Veredicto

| gate | resultado |
|---|---|
| N0 inércia total sem joelho | **OK — bit-a-bit** (181 curvas, 0 divergem) |
| N1 inércia no platô | **OK** (242 pontos pré-joelho, 0 violam) |
| **N2 discriminância** | **FALHA** — razão cliff/rampa **1,38×** (critério ≥ 2×) |
| N3 virada só no colapso | OK (vacuamente: 0 viradas) |
| N4 teto de 25 viradas | OK (**0** viradas) |
| N5 fingerprint | OK (`4f5bedfbace4`) |
| N6 não-unilateral | OK (14 curvas pioram) |

**Ramo pré-declarado:** *"**N2 ✗** ⇒ mesma morte da 1ª tentativa ⇒ **abandonar a
linha inteira** e registrar que correspondência por nível também não
discrimina."* Honrado.

**A meta iria de 148 para 139.** Zero viradas, **9 perdas**. A métrica não
resgatou nada e destruiu o que passava.

---

## 1. O que a matou de verdade — e não foi o gate

A previsão escrita no pré-registro (§4, N2) errou por uma ordem de grandeza:

| | previsto | medido |
|---|--:|--:|
| `Δ_col` do `fig2` fino | 1789 | **40** |
| joelho | N = 8000 | **N = 9749** |
| res.máx do cliff | 0,306 | **4,07** |
| res.máx da rampa | 0,110 | **2,95** |
| razão | 2,8× | **1,38×** |

O erro não foi de conta — foi de **premissa**. Eu supus o joelho em N=8000 (o
`trim_n_max` registrado). A regra, aplicada mecanicamente à curva **fina**,
colocou-o em 9749. Daí:

> **A regra de joelho não é invariante à amostragem.** Medido, na **mesma curva
> física** digitalizada de dois jeitos:
>
> | digitalização | pontos | joelho | `Δ_col` |
> |---|--:|--:|--:|
> | canônica | 15 | N = 8 800 | **1 100 ciclos** |
> | fina (re-digitalizada hoje) | 124 | N = 9 749 | **40 ciclos** |
>
> **27,5× de diferença em `Δ_col`.**

A regra opera sobre taxas **ponto-a-ponto**, então herda as escolhas de quem
digitalizou. Uma métrica normalizada por ela mede **como alguém amostrou a
figura**, não a junta. Isso a desqualifica **independentemente** dos gates —
e é um defeito de espécie diferente do da 1ª tentativa, não uma repetição dele.

*(Contribuiu para o valor extremo: o CSV fino foi reamostrado **uniforme em `r`**
— caveat já declarado no §5 do `liu2025_ramp_v2_results.md` —, o que concentra
35 pontos nos últimos ~15 ciclos. Mas isso é precisamente o ponto: uma escolha
legítima de reamostragem move o normalizador da métrica por 27×.)*

### 1.1 Consequência que vaza para fora desta proposta

O `trim_n_max` registrado usa **a mesma regra** (*"taxa local > 3× a mediana do
Estágio II, contígua até o fim"*, commit `b50550d`). Portanto: **os trims
vigentes também não são invariantes à amostragem** — eles são estáveis apenas
porque quem os aplica é uma pessoa exercendo julgamento, não a fórmula rodando.
Isso não invalida os trims (o julgamento humano ali é defensável e está
documentado caso a caso), mas **invalida a ideia de automatizá-los com esta
regra**, e deve ser dito na ratificação da §B.

---

## 2. Bloco B — a pergunta que motivava tudo: respondida, e é não

As 16 curvas trimadas, pontuadas na curva **inteira** sob a métrica de nível:

> **0 de 16 passam.** E várias pioram muito (`liu2025_M16_amp0p25`
> 0,0745/0,1672 → 0,7270/5,3056; `yang2021_amp0p5mm_ax8kN` 0,0649/0,1850 →
> 1,0860/4,8719).

⇒ **Remover os trims sob esta métrica não resgata nada.** A hipótese de trabalho
— *"a métrica em vida habilita a remoção dos trims"* — está **falsificada**.

---

## 3. O que os gates acertaram, de novo

- **N0/N1 passaram bit-a-bit** (181 curvas + 242 pontos de platô): a correção
  estrutural em relação à 1ª tentativa **funcionou**. A brecha do modelo que
  despenca e é perdoado está fechada — `jcsr2023_plain_outdoor`, o caso que a
  expôs, saiu **idêntico**.
- **N6 fez o serviço para o qual foi inventado.** Ele existia porque a 1ª
  tentativa só podia melhorar números. Aqui 14 curvas pioram — e a leitura
  declarada de antemão (separar piora **legítima** de **janela degenerada**) se
  provou necessária: 5 das 14 são degeneradas, incluindo
  `eccles2010_fig7d_axial_3p1kN_constant` com `Δ_col`=25 ciclos indo de
  0,0668/0,0891 para **3,7052/38,5223**.
- **O risco declarado antes de medir se materializou exatamente como escrito.**
  O §2.4 do pré-registro previu janelas degeneradas e disse que corrigi-las
  naquele momento seria mexer na forma depois de congelá-la. Foi o que
  aconteceu, e o registro prévio é o que permite lê-lo como propriedade da
  regra em vez de como acidente.

---

## 4. Estado final

**Revertido, sem resíduo:** `runner.py` de volta ao canônico (a implementação
**nunca** foi commitada); store restaurado — **0 divergências** nos campos
verticais nos 203 casos; fingerprint `4f5bedfbace4`; meta segue **147/202**.

**Preservado:** este documento, `metrica_nivel_gates.py` (o arnês; precisa do
patch revertido para rodar inteiro), `metrica_nivel_result.json`.

---

## 5. A linha está fechada. O que sobra.

Duas tentativas, dois pré-registros, duas mortes por gate — **de causas
diferentes**:

| | 1ª (ortogonal) | 2ª (nível) |
|---|---|---|
| morreu por | **M2** — o modelo escolhia a correspondência e um modelo que despenca era perdoado | **N2** — o normalizador `Δ_col` não é invariante à amostragem |
| efeito na meta | 147 → 153 (mas 4 de 6 viradas ilegítimas) | 148 → **139** (0 viradas, 9 perdas) |

O ramo pré-declarado manda **abandonar a linha inteira**, e é o que fica
registrado: **pontuar o colapso em vida não é redutível a uma métrica automática
sobre curvas digitalizadas esparsas.** As duas mortes convergem para a mesma
raiz — no trecho quase-vertical, **o dado publicado não carrega informação
suficiente** para distinguir formas nem para normalizar uma tolerância; o que
existe ali é a moldura da figura e as escolhas do digitalizador.

Isso **reforça** o que a §4.44a já dizia, agora com duas falsificações em vez de
um argumento: as curvas de colapso quase-vertical são **metric-limited** e
permanecem fora da meta por razão **metrológica**. O trim, aplicado por
julgamento humano e documentado caso a caso, segue sendo a saída honesta — e
agora se sabe que ele **não** é automatizável pela regra que o descreve.

**O que NÃO foi tentado e continua aberto** (nenhuma das duas tentativas o
toca): tratar essas curvas com **métrica de banda** — comparar o modelo contra
um envelope de incerteza do dado em vez de contra uma curva —, que é a resposta
estatisticamente correta ao scatter de 44 % e que o prereg v1 da rampa já havia
nomeado como *"fora de escopo, registrado aqui para não se perder"* (§5). É a
única rota restante que não foi falsificada, e exigiria mudar a métrica de
"distância a uma curva" para "pertinência a uma banda" — mudança maior que as
duas tentadas, e decisão do professor.
