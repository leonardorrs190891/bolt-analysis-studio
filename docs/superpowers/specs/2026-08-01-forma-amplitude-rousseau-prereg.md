# Prereg — forma de RESPOSTA À AMPLITUDE ancorada no ROUSSEAU (dado consistente)

**2026-08-01** · o déficit que o LIU_2025 não conseguiu atacar (dado
internamente inconsistente) tem agora âncora limpa: **mesmo rig, mesmo
paper, duas amplitudes 4× separadas, medidas no mesmo dia**.

## O defeito, medido (fingerprint `576605bcf96d`)

Aço t10, cfg re-fitado a 0,05 mm (`c_bend`=3,0):

| condição | dado (fim) | modelo (fim) | MAE |
|---|---:|---:|---:|
| 0,05 mm (Fig. 5, **fitada**) | 0,137 | 0,301 | 0,107 |
| 0,20 mm (Fig. 6, **held-out**) | 0,164 | 0,313 | 0,133 |

O dado quase **não muda** com 4× de amplitude (0,137 → 0,164) e o modelo
também não (0,301 → 0,313) — mas **ambos erram na mesma direção**: o
modelo retém ~2× o medido nas DUAS. ⇒ ⚠️ **Leitura corrigida ao tabular:
aqui NÃO há déficit de INCLINAÇÃO em amplitude** (o dado do aço é quase
insensível entre 0,05 e 0,2 mm, e o modelo acompanha). O que existe é um
**déficit de NÍVEL comum às duas** — outra classe de defeito.

## Consequência para o plano (declarada ANTES de qualquer fit)

A hipótese que motivou este prereg (*"a resposta à amplitude é fraca
demais"*) **não é sustentada pelo par do Rousseau**: seria preciso ver o
dado variar muito com a amplitude e o modelo não acompanhar. Não é o
caso. Portanto:

- **NÃO abrir forma de amplitude com esta âncora.** Seria fitar uma
  inclinação que o dado não pede.
- O alvo real que o par revela é **nível de perda no aço** (modelo retém
  o dobro), com a MESMA constante nas duas amplitudes ⇒ candidato a
  constante per-rig, não a forma nova.

## Gate único (G1), e o que ele decide

Varrer as constantes de nível já existentes do grupo aço (`emb_depth`,
`loose_arrest_floor`, `mu_bearing/mu_thread`) e perguntar: **existe UM
valor que aproxime as duas amplitudes ao mesmo tempo** (soma dos MAE das
4 curvas do aço cai ≥20 %, nenhuma piora >+0,01)?

- **Passa** ⇒ é constante per-rig faltante: adotar pelo procedimento
  normal (1 número, procedência declarada, held-out reportado).
- **Falha** ⇒ o déficit de nível do aço é estrutural com as constantes
  atuais; documentar e **parar** (não inventar forma).

Ramo INCONCLUSIVO: se a varredura melhorar a Fig. 6 piorando a Fig. 5 (ou
vice-versa), o defeito É dependente de amplitude e o prereg de forma
volta à mesa — com esta medição como evidência.

---

## EXECUÇÃO (mesma sessão) — G1 PASSOU, nenhuma forma aberta

Decomposição primeiro (regra do repo: alavanca multiplicativa é limitada
pela fatia do canal): **afrouxamento rotacional carrega 67–79 %** nas duas
amplitudes.

| alavanca | soma MAE (4 curvas do aço) | pioras >0,01 |
|---|---:|---|
| base | 0,300 | — |
| `tr_loose_gain` 3 / 4 / 6 | 0,671 / 1,055 / 1,348 | 2 / 3 / 3 |
| `mu_bearing=mu_thread`=0,10 | 0,559 | 3 |
| **`loose_arrest_floor`=0** | **0,233 (−22 %)** | **nenhuma** |

Fronteira monótona (0,00→0,233 · 0,02→0,250 · 0,05→0,276 · 0,10→0,315 ·
0,15→0,351): não há mínimo interior — **não é knob ajustado, é um valor
de contorno**. O `0,08` vigente vinha do **pack**, não de leitura do rig;
a substituição tem **procedência de APARATO** (roletes INA-HYDREL FE
declaradamente para remover o atrito parasita ⇒ sem auto-travamento).

**Veredicto**: G1 PASSA ⇒ constante per-rig faltante, adotada pelo
procedimento normal. **A forma de amplitude NÃO foi aberta** — e a
evidência que a desaconselha (dado 0,137→0,164 contra modelo 0,301→0,313)
fica registrada aqui para não ser re-proposta sem dado novo.
