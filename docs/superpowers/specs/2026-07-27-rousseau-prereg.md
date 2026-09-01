# PRÉ-REGISTRO — Rousseau 2025 (M12, varredura de espessura de membro)

> **IMUTÁVEL a partir de agora.** Gates escritos ANTES de qualquer fit. Alterar
> qualquer critério depois de ver resultado invalida o prereg — abra outro.
> Convenção da campanha: máximo **2 preregs por candidato**; a segunda falha é
> falsificação documentada (FAIL2), não terceira tentativa.
>
> Escrito 2026-07-27, sobre o store certificado no S3 (fingerprint
> `4f5bedfbace4`, 203/203, zero erros).

---

## 0. Estado medido — a partida

| caso | MAE | res.máx | onde ocorre | final previsto | final medido |
|---|--:|--:|--:|--:|--:|
| **steel_t10** | 0.087 | **0.188** | N=170 = **100%** da curva | 0.325 | **0.137** |
| steel_t12 | 0.046 | 0.074 ✔ | 50% | 0.655 | 0.624 |
| steel_t14 | 0.020 | 0.034 ✔ | 33% | 0.904 | 0.903 |
| **hdpe_t10** | 0.058 | **0.153** | 36% | 0.200 | 0.212 |
| **hdpe_t12** | 0.064 | **0.138** | 62% | 0.301 | 0.321 |
| hdpe_t14 | 0.044 | 0.077 ✔ | 30% | 0.882 | 0.875 |

Curvas curtas: 170–400 ciclos. Fonte inteira = 6 casos, 3 fora do tripé.

## 1. Correção de narrativa — o que já está construído

**O roadmap item 10 do CLAUDE.md e a nota §4.20 do MODEL_LEGITIMACY estão
DESATUALIZADOS** e não podem servir de base para este trabalho. Medido hoje:

- §4.20 diz que o *stroke-split* "segue não-construída" e que
  `GA_member`→`k_member_shear` é "INERTE no pack CM". **Falso hoje:** o PR-14
  adotou `GA_member=20000` para o grupo HDPE, e o termo está **vivo** —
  `k_member_shear` = 2.00e6 / 1.67e6 / 1.43e6 N/m para t10/t12/t14, entrando em
  série com `k_tr` em `k_tr_transverse` (analyzer L1012). O slip resolvido cai
  monotonicamente com a espessura: **0.232 → 0.144 → 0.049 mm**. É exatamente o
  comportamento que a forma deveria produzir, e os três finais HDPE acertam.
- O roadmap cita "MAE 0,228→0,373→0,380" e sobre-predição crescente com a
  espessura. **Falso hoje:** os MAE são 0.058/0.064/0.044 (HDPE) e
  0.087/0.046/0.020 (aço), e o erro **cai** com a espessura, não cresce.

**Lição aplicada (F4 PARE):** uma falsificação não re-baselinada contra o
canônico vigente induz ao candidato errado. Foi o que matou o `flank_s_crit`.
Por isso o G0 abaixo vem antes de tudo.

## 2. As duas trilhas — e por que NÃO são um fenômeno só

O diagnóstico de posição do resíduo separa os 3 violadores em dois problemas
distintos. **Uma única forma não fecha os três**, e um prereg que prometa isso
está errado desde o enunciado.

**Trilha A — steel_t10: arresto terminal.** O resíduo máximo está no **último
ponto** da curva. O modelo afrouxa, mas **para cedo demais**: retém 0.325
enquanto o dado chega a 0.137. Não é falta de slip — o t10 é o aço com MAIS
slip resolvido (0.231 mm, contra 0.000 no t14, que trava por completo e acerta
por isso). É a **perda por slip que satura** antes da hora.
  - *H-A1:* `loose_arrest_floor` alto demais para este par. O grupo aço herda o
    0.08 do PACK, enquanto o HDPE tem 0.2 adotado. Predição distintiva: baixar
    o piso move o **fim** da curva sem mexer no começo.
  - *H-A2:* o `self_locking_gate` (S-curve em `1−F_min/F₀`) fecha cedo a
    F₀=10.25 kN. Predição distintiva: o efeito escala com F₀, logo t12 (que
    passa) também se move — e aí a hipótese cobra preço em não-regressão.
  - *H-A3:* take-up elástico superestimado no aço fino, isto é, o mapeamento
    `grip→L_eff→k_b`/`c_bend` não escala. Predição distintiva: muda o slip, logo
    move a curva **inteira**, não só o fim.

**Trilha B — hdpe_t10/t12: forma no meio da curva.** Os finais acertam
(0.200/0.212 e 0.301/0.321); o resíduo máximo está a 36% e 62% de N. É
**tempo de joelho**, não nível.
  - *H-B1:* transição de assentamento cedo/tarde (`emb_depth` adotado 5e-7 m).
  - *H-B2:* o gate de regime de slip (CM) atravessa o limiar no ciclo errado.
  - *H-B3:* irredutível — as amplitudes são **por espécime** (paper Tabela 2:
    0.5/0.49/0.38 mm) e o t14 usa 0.38: a fonte pode não sustentar uma forma
    única. Se for isto, o desfecho é exceção com prova, não forma nova.

## 3. Diagnóstico OBRIGATÓRIO antes de qualquer fit

Lição da campanha: diagnosticar ponto-a-ponto **antes** de fitar. Nenhum fit
pode começar sem os quatro itens abaixo registrados.

- **D1** — Curva de resíduo assinado (modelo − dado) vs N para os 3 violadores.
  Identificar se o resíduo é monotônico (nível) ou tem troca de sinal (forma).
- **D2** — Decomposição por mecanismo no ponto do `maxerr_at` de cada um: qual
  canal domina a perda ali.
- **D3** — Sonda de direção com **2 pontos** antes de qualquer bisseção, para
  cada lever candidato (regra dura: a campanha errou o sentido da monotonicidade
  duas vezes por pular isto).
- **D4** — Ler o paper para as três hipóteses B: as amplitudes por espécime e o
  protocolo de assentamento estão declarados? Isto decide H-B3 por **leitura**,
  não por fit.

## 4. GATES — imutáveis

**G0 — Re-baseline da falsificação (bloqueante).** Antes de propor qualquer
mecanismo, reescrever o item 10 do roadmap e a §4.20 com os números medidos
hoje. *Passa* quando o texto do repositório descrever o estado real. Enquanto
não passar, nenhum outro gate pode ser avaliado.

**G1 — Inércia por construção (não-negociável).** Qualquer campo novo nasce
default-inerte: com ele no valor OFF, os **202 casos comparáveis** saem
**bit-idênticos** ao store `4f5bedfbace4`. Zero diferença, não "diferença
pequena". Switch de forma é `fittable=False` no registry.

**G2 — Alvo.** Os 3 violadores entram no tripé (MAE ≤ 0.10 **E** res.máx ≤ 0.10).
*Crédito parcial aceito:* **≥2 dos 3**, desde que o terceiro melhore ≥30% no
res.máx. Menos que isso = FAIL.

**G3 — Não-regressão.** (a) Os 3 casos Rousseau que hoje passam continuam no
tripé; (b) nenhum caso da biblioteca piora mais de **+0.01** em MAE ou res.máx;
(c) a mediana global dos 202 não piora.

**G4 — Procedência.** Toda constante nova declara classe: medida | âncora de
literatura | handbook/tabela | fitada-this-rig. Fitada-this-rig entra na
contagem de DOF e no `prov` do config adotado. **Proibido** promover constante
sem procedência escrita.

**G5 — Transferência (o gate que vale cientificamente).** A forma é ajustada num
**subconjunto** e prevê o resto **sem re-fit**: ajustar em `{t10, t14}` e prever
`t12` zero-refit, nas duas famílias. *Passa* se o t12 previsto ficar dentro de
+0.02 do res.máx que teria com fit próprio. **Este gate existe porque o Rousseau
é a única varredura controlada de rigidez de membro da biblioteca** — fechar as
curvas sem passar aqui não prova nada sobre transferência de forma, e a tese do
projeto é justamente essa.

**G6 — O resíduo cai onde ele estava.** Para cada violador, o res.máx **na
posição do `maxerr_at` original** tem de cair. Proíbe a solução que só desloca o
pico para outro N e melhora a métrica sem acertar a física.

**G7 — Verificação adversarial.** Antes de adotar, ≥3 votos independentes
tentando **refutar** o "passou", com instrução explícita de assumir refutado em
caso de dúvida. Maioria refutando = não adota.

## 5. Parada

- Trilha A e Trilha B são preregs **separados** para efeito de FAIL2: cada uma
  tem direito a 2 tentativas.
- **FAIL2 em A** → o arresto terminal do aço vira falsificação documentada e
  `steel_t10` entra na lista de exceções com a prova quantitativa.
- **FAIL2 em B** → confirma H-B3; os dois HDPE viram exceção por amplitude
  por-espécime, com a Tabela 2 do paper como prova.
- Em qualquer FAIL, **o statu quo é byte-idêntico** — nada de "adotar o menos
  pior".

## 6. NÃO autorizado por este prereg

- Ligar as capacidades da F4 que seguem não-demonstradas (`flank_s_crit`,
  `flank_transverse_on`) — exigem palavra explícita do professor.
- Qualquer lever que só mova **nível**: hoje está medido que `MAE ⊆ maxerr`
  (zero curvas violam só o MAE), logo nível não fecha curva nenhuma.
- Absorvedor cego (piso/ganho livre) sem física nomeada — precedente do PR-10,
  em que o floor 0.30 melhorava a mediana e foi recusado.
- Fitar scatter entre espécimes.
- Tocar em qualquer fonte fora de ROUSSEAU_2025 / ROUSSEAU_HDPE.
