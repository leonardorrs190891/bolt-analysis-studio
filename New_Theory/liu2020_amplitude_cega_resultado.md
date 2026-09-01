# LIU_2020_WEAR — a âncora da derivada de amplitude, e o modelo é CEGO a ela

**2026-08-06 (noite)** · campanha MARGENS, fase A′ (fechamento de fontes),
alvo nº 2. Sonda só-leitura sobre o store `5916d8be0510` (139/205). Nada
escrito no store/config/CSV.

## Por que esta fonte importa mais do que "1 curva fora" sugere

A nota do registry diz, literalmente, que a Fig. 9 é a **"curva-chave p/
d(afrouxamento)/d(amplitude) (super-linear medido, ~A_F^1.5)"**. A varredura
0,1/0,2/0,3/0,4 mm a P₀=18 kN fixo foi digitalizada **para ancorar a derivada
de amplitude** do modelo.

## A medição

| amp (mm) | perda DADO | perda MODELO | razão | viés | MAE |
|---:|---:|---:|---:|---:|---:|
| 0,1 | 0,0120 | **0,0350** | 2,917 | −0,0155 | 0,0157 |
| 0,2 | 0,0367 | **0,0350** | 0,954 | +0,0002 | 0,0050 |
| 0,3 | 0,0665 | **0,0350** | 0,526 | +0,0193 | 0,0193 |
| 0,4 | 0,1689 | **0,0350** | 0,207 | +0,0729 | **0,0729** |

**A perda do modelo é 0,0350 nas quatro — idêntica a 4 decimais.**
Espalhamento: dado **14,07×**, modelo **1,00×**. Ajuste `perda ∝ amp^b`:
**b(dado) = 1,819** (o paper diz ~1,5) contra **b(modelo) = −0,000**.

⇒ **4ª ocorrência de "sub-resposta à variável varrida"** — e a mais extrema,
empatada com a frequência do LI_2022 (que dava 0,03 % de espalhamento). Junta-se
a: frequência (LI_2022), espessura (ROUSSEAU), torque (LU_2024).

## A causa: não é dado, é o CONFIG ADOTADO

Decomposição da AF0,4: **embedding = 100,0 %**; creep, wear, fretting de flanco,
afrouxamento rotacional e fadiga **exatamente 0**. O config adotado desliga
todos os canais sensíveis à amplitude:

```
k_wear_spec = 0.0   E   K_archard = 0.0      (wear morto pelas DUAS vias)
C_creep     = 0.0
emb_depth   = 1.12e-6                        (único canal vivo)
```

E o `EmbeddingLoss` é *state-based* na profundidade restante: satura em
`emb_depth` **independentemente da amplitude** ⇒ perda idêntica por construção.

⚠️ **As 3 curvas que passam, passam pelo motivo ERRADO.** A perda real em
0,1–0,3 mm calha de ficar perto de 0,035; o modelo acerta o número sem ter o
mecanismo. Uma fonte "8/9" que na verdade não responde à variável que ela
existe para medir.

## Rota óbvia FALSIFICADA por medição (sonda de 2 pontos, como manda o charter)

Religar wear pela via canônica não recupera a lei — **satura o modelo**:

| `k_wear_spec` | perda do modelo (0,1→0,4 mm) | espalhamento | MAE |
|---|---|---:|---|
| 0 (config atual) | 0,0350 · 0,0350 · 0,0350 · 0,0350 | **1,00×** | 0,005–0,073 |
| **5e-14** (valor do bloco `shared`) | 0,816 · 0,965 · 0,993 · 0,999 | **1,22×** | 0,208–0,305 |
| 2e-13 | 0,999 · 1,000 · 1,000 · 1,000 | **1,00×** | 0,371–0,458 |

Com o coeficiente da biblioteca a junta perde TUDO em 18 000 ciclos nas quatro
amplitudes ⇒ o espalhamento não volta, porque tudo satura no teto. **Nenhum
valor de prateleira serve**: seria preciso um `k_wear_spec` ajustado a esta
fonte, e aí a pergunta passa a ser se o expoente resultante bate 1,82 — o que é
**fit com gates**, trabalho de fase B, não de faxina.

## Consequência para a campanha

1. **LIU_2020 sai da fase A′** (fechamento barato): não há conserto de dado; o
   caminho é fit gateado.
2. **Lição de leitura, para o placar por fonte:** "poucas curvas fora" pode
   esconder fonte que passa por coincidência. O diagnóstico honesto de uma
   fonte quase-fechada exige olhar se o modelo **responde à variável varrida**,
   não só o placar. Vale re-olhar as outras fontes de varredura com o mesmo
   teste (custa 4 leituras do store).
3. **Integridade de âncora**: enquanto o canal estiver morto, esta fonte **não
   pode** ancorar d(afrouxamento)/d(amplitude) — mesmo estatuto que o eixo N do
   YANG_2023_IJPEM ganhou no tick 4.
4. **O teste virou INSTRUMENTO, e achou uma SEGUNDA fonte cega.** A 1ª
   varredura de controle usou a chave mecânica e só enxergou o LIU_2020 — a
   mesma cegueira que escondeu o caso. Reescrito para agrupar **pela variável
   de fato varrida** (`delta_mm`/`F_amp_N` do `config_used`) dentro da mesma
   janela (`n_max`), virou `New_Theory/resposta_variavel_varrida.py`
   (só-leitura, segundos). Resultado nas 8 varreduras que qualificam:

   | fonte | var | níveis | dado | modelo | veredito |
   |---|---|---:|---:|---:|---|
   | LIU_2016 | F_amp | 5 | 1,68× | 1,88× | responde |
   | LIU_2017_AXIAL | F_amp | 5 | 3,33× | 1,72× | responde (parcial) |
   | **LIU_2020_WEAR** | **delta** | 4 | **14,07×** | **1,00×** | **CEGO (0 %)** |
   | LIU_2020_WEAR | F_amp | 4 | 1,96× | 2,00× | responde |
   | LIU_2022_RETIGHT | F_amp | 4 | 1,92× | 1,76× | responde |
   | LU_2024 | delta | 3 | 3,82× | 3,37× | responde |
   | LU_2024 | F_amp | 4 | 1,47× | 1,84× | responde |
   | **YANG_2023_IJPEM** | **delta** | 3 | **6,86×** | **1,07×** | **CEGO (1 %)** |

   **Duas leituras que isto entrega:** (i) o instrumento se valida sozinho — 6
   das 8 mostram o modelo espalhando como o dado, então "1,00×" não é artefato
   de método; (ii) o **LIU_2020 responde a F_amp (2,00× contra 1,96×) e não a
   delta** — a cegueira é do canal de DESLOCAMENTO, não da fonte inteira, o que
   estreita o candidato de conserto.

   **A 2ª cega é o YANG_2023_IJPEM** (0,15/0,18/0,25 mm, todas na janela de
   2000 ciclos): dado 6,86×, modelo **1,07×**. Isto **sharpen** o diagnóstico do
   tick 4 do ledger (bimodalidade stick/runaway com rotas esgotadas): o modelo
   não tem resposta graduada à amplitude **nem abaixo do limiar**, onde não há
   bifurcação para culpar. Não reabre a fonte (as rotas seguem esgotadas e o
   eixo N está rebaixado), mas nomeia melhor o defeito.

   ⚠️ **Ausência de linha NÃO é atestado**: fonte com <3 níveis na mesma janela
   não é coberta. As sub-respostas ao **torque** (LU_2024) e à **espessura**
   (ROUSSEAU) foram achadas por outros caminhos e não aparecem aqui — e note
   que o LU_2024 aparece como "responde" em delta/F_amp, o que é verdade e não
   contradiz a cegueira dele ao torque.
5. Candidato para a **fila do professor**: re-ativar o canal de amplitude no
   LIU_2020 com `k_wear_spec` per-fonte é adoção de constante com fit —
   precisa de prereg, held-out e procedência (o par tribológico é **zinco**,
   distinto dos pares já ancorados).
