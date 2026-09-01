# A bifurcação medida no fio da navalha — 0,01 mm no limiar move o final do modelo de **0,94 para 0,00**

**2026-08-07** · só-leitura · **nada adotado** · reforça **P-13** com a **terceira**
fonte independente.

## O caminho, e a hipótese que eu tinha

Diagnosticando as 4 indecidíveis do `YANG_2023_IJPEM`, a decomposição mostrou uma
**transição de regime nítida** em δ = 0,25 mm:

| curva | δ (mm) | MAE | viés | \|v\|/MAE | decomposição no fim |
|---|---:|---:|---:|---:|---|
| `0_15_below_threshold` | 0,15 | **0,0093** | +0,008 | 0,90 | embedding 68 % · creep 32 % |
| `0_18_below_threshold` | 0,18 | **0,0076** | +0,004 | 0,47 | creep 54 % · embedding 46 % |
| **`0_25`** | 0,25 | **0,1664** | **+0,1664** | **1,00** | creep 54 % · embedding 46 % |
| `0_30` | 0,30 | 0,1200 | +0,047 | 0,39 | **rotacional 95 %** |
| `0_35` … `0_65` | 0,35–0,65 | 0,082–0,179 | ± | 0,22–1,00 | **rotacional 96–99 %** |

As duas de baixo do limiar acertam com MAE **0,008**. A `0_25`, no **mesmo
regime**, erra **0,1664** com viés positivo **puro**.

Os próprios `case_id` dizem onde está o limiar do paper: `0_15_mm_below_threshold`
e `0_18_mm_below_threshold` são rotulados assim **pela fonte**. Logo o limiar
real está entre 0,18 e 0,25; o do modelo (`delta_free` = **0,18 mm** no grupo M8)
deixa a `0_25` com só **0,07 mm** de slip efetivo.

**Hipótese:** baixar `delta_free` dá slip à `0_25` e fecha a curva.

## ⛔ FALSIFICADA — e produziu a melhor evidência da campanha

| `delta_free` | rotacional | **final do modelo** | viés | MAE |
|---:|---:|---:|---:|---:|
| 0,200 | 0,0 % | 0,9456 | +0,1664 | 0,1664 |
| 0,180 (nominal) | 0,0 % | 0,9456 | +0,1664 | 0,1664 |
| **0,170** | **0,4 %** | **0,9448** | **+0,1663** | 0,1663 |
| **0,160** | **93,0 %** | **0,0000** | **−0,0510** | 0,1444 |
| 0,155 | 93,6 % | 0,0000 | −0,1502 | 0,1904 |
| 0,140 | 94,7 % | 0,0000 | −0,3025 | 0,3025 |
| 0,120 | 95,4 % | 0,0000 | −0,4474 | 0,4474 |

**O dado termina em 0,5200.**

Entre `delta_free` = 0,170 e 0,160 — **um centésimo de milímetro** — o canal
rotacional salta de **0,4 % para 93,0 %** e o final do modelo cai de **0,9448
para 0,0000 exato**. O dado está **quase exatamente no meio** dos dois atratores.

⇒ **não existe parametrização que ponha o modelo em 0,52.** O canal é binário:
ou quase não engata, ou desaba a zero. O melhor MAE de toda a varredura é
**0,1444** (2,9× o limite), e ele ocorre no primeiro ponto **depois** do salto —
não por acerto, mas porque ali o erro de sinal trocado é menor em módulo.

## Por que esta é a evidência mais forte da P-13

As três fontes que exibem a forma faltante, agora com o discriminante de cada:

| fonte | evidência | rig |
|---|---|---|
| `SUN_2025_CRIMP` | `ln(F/F₀)` vs N **reta**: τ=172,7, **R²=0,9961** em 37 pts | M12, crimp/padrão |
| `ROUSSEAU_2025` HDPE | nenhum `loose_arrest_floor` em [0; 0,40] fecha; **pernas com ótimos em valores diferentes** | M12 8.8, membro HDPE |
| **`YANG_2023_IJPEM`** | **0,01 mm de limiar move o final de 0,94 a 0,00**, com o dado no meio | M8, δ 0,15–0,65 mm |

Três rigs, três materiais/tamanhos, três escalas de amplitude. E a IJPEM entrega
o que as outras duas não tinham: **a demonstração de que o salto é
descontínuo**, não apenas mal calibrado — dois valores adjacentes do mesmo
parâmetro dão finais separados por 0,94.

## O padrão que se repete nas três falsificações desta manhã

Em ROUSSEAU e IJPEM eu propus consertos que **pareciam** de calibração
(procedência de aparato num caso, limiar mal posto no outro), e os dois
falsificaram **na direção oposta à prevista**. A explicação é a mesma:

> a constante que eu queria mover está **compensando** a forma que falta.
> Removê-la ou ajustá-la não melhora — **expõe o buraco**.

O `loose_arrest_floor = 0,2` do HDPE e o `delta_free = 0,18` do M8 não são
física medida: são **as bordas do intervalo onde o modelo binário passa mais
perto** de curvas que vivem no meio.

## O que fica

* **P-13 reforçada** de 2 para **3 fontes**, com o discriminante mais nítido
  vindo da nova.
* **As 4 indecidíveis do IJPEM não têm rota de calibração.** A `0_25` é
  inalcançável por `delta_free`; as `0_30`/`0_35`/`0_50` estão no regime
  rotacional, onde a mesma bifurcação atua.
* **Nenhuma ação executável sem a forma nova** — que é P-13, decisão do
  professor.

⚠️ **Não medido:** que uma taxa fracionária constante feche estas curvas. O que
está medido é que o **modelo binário não pode**, e que o dado exige o
intermediário.

## Reprodutibilidade

As duas varreduras estão no scratchpad e são recomputáveis do store em minutos
(6 curvas M8 × 6 valores de `delta_free`; depois 8 valores finos na `0_25`).
