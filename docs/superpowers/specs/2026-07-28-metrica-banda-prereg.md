# Pré-registro — MÉTRICA DE BANDA (3ª e última tentativa da linha)

**Data:** 2026-07-28 · **Autorização:** professor, *"pré-registre a métrica de banda"*
**Antecessoras, ambas REJEITADAS:** `2026-07-28-metrica-em-vida-prereg.md` (§4.45) · `2026-07-28-metrica-nivel-prereg.md` (§4.46)
**Fingerprint vigente:** `4f5bedfbace4` (203 casos) · **Status:** PROPOSTO — gates IMUTÁVEIS depois de assinados

> **Regra da §4.45 aplicada, agora com conta NUMÉRICA.** Cada gate abaixo carrega
> o valor **medido** que a forma proposta produz no caso de referência. Na 2ª
> tentativa eu fiz a conta *de cabeça* e ela errou por uma ordem de grandeza
> (previ `Δ_col`=1789, era 40), o que desperdiçou um ciclo inteiro. Aqui a conta
> foi **rodada**. **Custo declarado:** isto é divulgação parcial e reduz a
> cegueira; foi feita **só** no caso de referência (`fig2_single`, nas duas
> digitalizações) e em **duas** curvas planas, e todos os números estão escritos
> abaixo para que a perda de cegueira seja auditável.

---

## 1. O que as duas mortes anteriores obrigam

| morte | causa | o que esta forma faz |
|---|---|---|
| §4.45 (ortogonal) | o **modelo escolhia** a correspondência (`min()`), então um modelo que despenca varria o valor do dado e era perdoado | avaliação **em `N_i` fixo**, sem `min()`, sem voto do modelo |
| §4.46 (nível) | o normalizador `Δ_col` vinha de **taxas ponto-a-ponto** ⇒ não invariante à amostragem (1100 vs 40 ciclos na mesma curva) | **sem regra de joelho**: a largura da janela é `3 %` de **um número por curva** (`N_fim`), e a banda usa o dado **interpolado**, não os pontos amostrados |

---

## 2. A forma

```
h_N(curva) = FRAC_N * N_fim              FRAC_N = 0.03
banda_i    = [ min , max ] do DADO INTERPOLADO em [N_i - h_N , N_i + h_N]
             (grade de 64 pontos, clampada ao domínio do dado)
resid_i    = 0                                    se banda_lo <= r_mod(N_i) <= banda_hi
             dist. à borda mais próxima           caso contrário
sinal_i    = +1 acima da banda, -1 abaixo
```

`FRAC_N = 0,03` é o **erro de posicionamento de ciclo declarado** nas notas de
aparato (`liu2025_scirep_M16.md`: *"±3 % in cycle placement"*), adotado como
default de campanha. Classe: **input-de-paper**. Refino por fonte = follow-up.

**Três escolhas de projeto, com o motivo medido:**

1. **SEM dilatação vertical (`±σ_r`).** Incluí-la afrouxaria o tripé em 0,02 em
   **toda** curva, inclusive plana — resgate trivial, não metrológico. Medido no
   `fig2` fino: com `±0,02` a rampa dá res.máx **0,0346**; só com a janela
   horizontal, **0,0521**. Excluída de propósito.
2. **Mín/máx do dado INTERPOLADO**, não dos pontos amostrados. É a correção da
   2ª morte: com os pontos crus, a banda fica mais estreita em curvas esparsas e
   o resultado passa a depender de quem digitalizou.
3. **`N_fim` da janela métrica** (pós-trim, quando há trim) — um número único
   por curva, sem joelho e sem taxas locais.

### 2.1 Propriedade que cria risco, declarada

`r_i` sempre pertence à banda (pois `N_i` está na janela) ⇒ **`resid_banda ≤
|Δr|` em todo ponto**. A métrica é **unilateral**: só pode melhorar números —
a mesma propriedade que tornou vazio o headline "147→153" da 1ª tentativa.
A diferença é que ali a unilateralidade vinha acompanhada de **liberdade do
modelo**; aqui não há. Ainda assim, **"melhorou" não é evidência de nada**, e
os gates B1/B2/B3 existem exatamente para atacar o *onde*.

---

## 3. Implementação declarada

Campos novos ao lado dos atuais: `mae_band`, `maxerr_band`, `maxerr_band_at`,
`resid_std_band`, `metric_band`, `band_lo`, `band_hi`, `band_hn`. Nada é
sobrescrito. Não se toca em `align`, `FLOOR_TRIM`, `trim_n_max`, física ou
`engine_fingerprint()`.

---

## 4. GATES — cada um com a conta **rodada**

**B0 — INVARIÂNCIA À AMOSTRAGEM** *(a morte da 2ª tentativa vira gate)*.
*Critério:* na mesma curva física em duas digitalizações (`fig2_single`
canônica 15 pts × fina 124 pts), o **veredicto do tripé** deve ser idêntico para
as três formas, **e** o res.máx da forma que passa não pode diferir mais que
**20 %**.
*Conta rodada:* veredictos **F / P / F** em ambas. Res.máx da rampa **0,0521**
(15 pts) vs **0,0542** (124 pts) = **4,0 %**. ✔ satisfazível com folga.
*Declarado:* o **cliff** difere 35 % em magnitude (0,1783 vs 0,1319) — o gate
mira no veredicto e na curva que passa, não na magnitude de quem falha.

**B1 — DISCRIMINÂNCIA** *(o gate que matou as duas anteriores)*.
*Critério:* no `fig2_single`, nas **duas** digitalizações: a **rampa passa** o
tripé **e** o **cliff** e o **sem-forma** falham.
*Conta rodada:* rampa **0,0243/0,0521 (P)** e **0,0137/0,0542 (P)**; cliff
**0,0479/0,1783 (F)** e **0,0759/0,1319 (F)**; sem-forma idêntico ao cliff (o
cliff cai depois do último ponto do dado). ✔ satisfazível.

**B2 — não é afrouxamento cego.**
*Critério:* a **mediana** da melhora em res.máx nas 203 curvas < **0,005**.
*Conta rodada (2 curvas planas):* `liu2025_M16_amp0p25` 0,0945 → 0,0938
(**−0,0007**); `liu2025_M16_amp0p6` 0,0650 → 0,0650 (**0,0000**). Previsão:
mediana « 0,005. **Mas isto é medição real nas 203 e pode falhar** — é o gate
que impede a banda de ser um desconto uniforme.

**B3 — toda virada precisa de banda LARGA no ponto crítico.**
*Critério:* para cada curva que vire falha→passe, a **largura da banda** no
antigo ponto de máximo-resíduo deve exceder **0,05**.
*Conta:* uma virada exige reduzir o res.máx de `>0,10` para `<0,10`; larguras
`<0,05` só conseguem isso em curvas com res.máx antigo `<0,15`. Gate real e
falseável — é o análogo do M3/N3 que pegou brechas nas duas tentativas.

**B4 — teto de 25 viradas.** Ponto de **parada obrigatória** para reportar, não
critério de correção.

**B5 — fingerprint inalterado** (`4f5bedfbace4`). ✔ por construção.

**B6 — inércia declarada, NÃO exata.** A banda tem largura `≈ |dr/dN|·2·h_N`
mesmo no platô, então **não** há identidade bit-a-bit com a métrica de hoje —
e o gate **não** a exige (foi exatamente esse tipo de exigência impossível que
tornou o M0 da 1ª tentativa insatisfazível). *Critério:* em curvas planas
(largura máxima da banda < 0,02), `|Δ res.máx| ≤ 0,005`.
*Conta rodada:* −0,0007 e 0,0000 nas duas sondadas. ✔ satisfazível.

### Bloco C — a pergunta que motiva tudo (medição declarada, não gate)

As **16 curvas com `trim_n_max`**, pontuadas na curva **inteira** sob a banda:
quantas passam? Foi **0 de 16** sob a métrica de nível (§4.46). É este número
que diria se os trims podem cair.

### 4.1 Interpretação pré-declarada

| resultado | leitura |
|---|---|
| B0–B3, B5, B6 ✓ e B4 ✓ | métrica adotável; Bloco C vira insumo da decisão sobre os trims |
| **B1 ✗** | 3ª morte pela mesma causa ⇒ **a linha fecha em definitivo**; registrar que nenhuma métrica automática distingue formas no colapso, e que o trim por julgamento humano é a resposta final |
| **B0 ✗** | a banda herda a amostragem como a 2ª tentativa ⇒ **morre** |
| **B2 ✗** | é desconto uniforme disfarçado ⇒ **morre** |
| **B3 ✗** | há virada sem banda larga ⇒ brecha ⇒ **morre** |
| **B4 ✗** (> 25) | **PARAR** e reportar antes de adotar |
| **B6 ✗** | a banda mexe em curva plana mais que o declarado ⇒ revisar `FRAC_N` **em prereg novo**, não aqui |

---

## 5. O que NÃO está sendo proposto

- **Não** remover trim algum (Bloco C é medição).
- **Não** substituir os campos verticais (ficam, para auditoria).
- **Não** usar dispersão de espécime (44 %) como largura de banda: medido em
  rascunho, uma banda de 44 % da vida contém **tudo**, inclusive o cliff —
  seria honesta sobre o scatter e inútil como métrica. `FRAC_N` é erro de
  **digitalização**, não de espécime, e isso está declarado.
- **Não** adotar a rampa do Liu 2025 (segue em falha parcial, G1 12/15).
- **Não** mexer em física nem em fingerprint.

---

## 6. Reprodutibilidade

```bash
py -3.12 New_Theory/metrica_banda_gates.py
py -3.12 New_Theory/parallel_batch.py --workers 6 --store
```
