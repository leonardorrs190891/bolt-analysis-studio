# Execução do prereg `delta_free` — **G3 e G4 REPROVAM. O valor congelado estava FORA da janela.**

**Executado em 2026-07-30.** Prereg:
`docs/superpowers/specs/2026-07-30-yang2023ijpem-delta-free-prereg.md`.
Sonda: `New_Theory/yang2023_delta_free_exec.py`.
**Nada adotado.** Store e `adopted_configs.json` intocados (conferido).

| gate | resultado |
|---|---|
| **G2** alinhamento cinemático | **PASSA** — onset 150,0 / 180,0 µm exatos; slip(0,15)=slip(0,18)=0; slip(0,25)=70 µm |
| **G3** ramo sub-crítico | **REPROVA** — as duas saem do tripé |
| **G4** nada pior que +0,01 | **REPROVA** — 6 das 7 pioram |
| **G5** escopo | PASSA (bit-idêntico fora da fonte) |

O estrago no G3 é grande, não marginal:

| curva | MAE | res.máx | σ_res |
|---|---|---|---|
| 0,15 mm | 0,0093 → **0,0919** | 0,0241 → **0,3295** | 0,0103 → 0,1374 |
| 0,18 mm | 0,0076 → **0,1889** | 0,0156 → **0,8940** | 0,0087 → 0,3527 |

Mediana do res.máx das 7 acima do limiar: 0,3600 → 0,6200 (**+0,26**) ⇒ **F4**
também disparou.

---

## Por que reprovou — e o erro é MEU, na escolha do valor, não na rota

Medido na decomposição: em 0,18 mm o canal `rotational_loosening` foi de
**0,0000 → 0,8900 kN**. Com slip nulo isso seria impossível (o gate é
`g = slip/(slip+delta_t)`, que dá 0 em slip nulo) — logo o slip **não** ficou
nulo durante a corrida.

E aqui está o que eu não tinha medido: **o termo elástico DECAI**.
`F_slip/k_tr = µ·F₀/k_tr` cai junto com F₀ (medido: 84,0 → 78,4 µm em 20 mil
ciclos). Então o onset não é fixo — ele **desce** ao longo do ensaio.

A condição real para uma curva ficar sub-crítica não é "onset inicial ≥ δ", é

```
delta_free + F_slip(t)/k_tr  >  δ      PARA TODO t
```

e como o elástico é mínimo no fim, quem manda é o valor **final**:

| condição | conta | limite |
|---|---|---|
| 0,18 nunca escorrega | `delta_free > 180 − 78,4` | **> 101,6 µm** |
| 0,25 escorrega | `delta_free < 250 − 84,0` | **< 166,0 µm** |

**Janela admissível = (101,6 ; 166,0) µm**, largura 64 µm — **não é vazia**.

E o valor que eu congelei no G1 foi **95,968 µm**, que está **FORA** dela, na
borda inferior. Ele põe o onset inicial exatamente em 180,0 µm = δ(0,18) — e a
borda é **instável**, porque no ciclo seguinte o elástico já decaiu e o onset cai
abaixo de δ. Resultado: 0,18 destrava, entra em slip e faz runaway.

**A rota de procedência continua certa. O que errei foi escolher a BORDA de um
intervalo aberto**, com uma conta estática (`limiar − elástico_inicial`) numa
grandeza que decai. É o mesmo erro de família que já cometi duas vezes hoje: ler
um instantâneo como se fosse a trajetória.

## O que fica estabelecido de positivo

1. **O valor adotado (180 µm) está certo pelo motivo certo, não por acaso.**
   `delta_free ≥ δ_limiar` garante `δ − delta_free ≤ 0` e portanto **stick
   permanente**, independente de qualquer decaimento. É a escolha robusta para
   manter 0,18 quiescente — e é por isso que ele sobreviveu.
2. **Mas ele também trava o 0,25**, medido na trajetória inteira: com
   `delta_free = 180`, `δ − delta_free = 70 µm` e o elástico nunca cai abaixo de
   78,4 µm ⇒ slip **exatamente 0 em 20 mil ciclos**. Não é stick de ciclo 1 —
   é stick permanente, e o dado colapsa para 0,52. Confirmado o achado do prereg
   anterior, agora sobre a trajetória e não sobre um instantâneo.
3. **A janela (101,6 ; 166,0) µm existe** e separa os dois: qualquer valor no
   interior mantém 0,18 travado *para todo t* e destrava 0,25. O defeito é
   corrigível por input — o que faltava era a conta certa.
4. **O modelo é bimodal aqui:** stick permanente **ou** runaway a zero
   (0,30 mm vai a F₀=0 em ~1000 ciclos). O dado em 0,25 mm quer um decaimento
   *gradual* até 0,52 — nenhum dos dois modos. Isso é a bifurcação
   arrest/zero já registrada no CLAUDE.md (`self_locking_gate` com floor=0), e
   ela **limita o que um `delta_free` correto pode entregar**: destravar o 0,25
   provavelmente o joga no runaway, não no decaimento medido.

## Follow-up — precisa de prereg NOVO (o G1 deste congelou 95,968)

Valor determinado pela mesma disciplina, agora com a conta certa e **sem olhar
erro**: média geométrica da janela admissível,

```
delta_free(m8) = sqrt(101,6 × 166,0) = 129,86 µm
```

O G1 do prereg atual congelou 95,968 µm, então **não posso re-rodar com 129,86 e
chamar de aprovado** — seria exatamente o refit que os gates existem para
proibir. Um prereg novo, com o valor acima congelado e o m6 recalculado pela
mesma regra, é o caminho.

**Expectativa declarada, para não inflar o próximo prereg:** pelo ponto 4, o
0,25 mm deve sair do stick e provavelmente cair no *runaway*, o que melhora o
começo da curva e erra o fim. Se for isso, o `delta_free` correto é condição
**necessária e não suficiente**, e a forma que falta é a que interpola entre
arresto e zero — a mesma que o `loose_arrest_floor` endereça.

## Ganho desta execução

Zero curvas fechadas. Estabelecido: a janela admissível existe e tem 64 µm de
largura; o valor atual é robusto para o ramo sub-crítico e é o que trava o 0,25;
e o modelo é bimodal onde o dado é gradual. Custo: um prereg reprovado por um
erro meu de escolha de valor — que os gates pegaram na primeira passada, antes de
qualquer adoção.
