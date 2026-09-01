# Prereg — `run14p2` entra na classe `k_ratchet` do M30 HV (D-Z)

**2026-08-07 (manhã)** · classe **parcimônia — zero número novo** · gates
escritos ANTES da execução · store `1c118e405a42` · autorização do professor:
*"adote se os gates passarem"*.

## O alvo

`karlsen2022_M30_HVtorqued_run14p2` é **a única curva da fila form-limited**
(triagem re-medida hoje: 139 no tripé, 66 fora, 1 form-limited). Estado:
**0,0898 / 0,2363 / 0,0854** — MAE 1,80×, res.máx 2,36×, σ **já dentro**
(0,95× do limite 0,0903).

## O defeito, medido

O resíduo cresce **monotonicamente** de +0,0000 (ciclo 0) a **+0,2363**
(ciclo 269), com viés **+0,0879** e **|viés|/MAE = 0,98** — deriva de nível
quase pura, não dispersão. Até o ciclo 99 o erro é ≤0,021; ele nasce na segunda
metade.

Decomposição no fim: **afrouxamento rotacional 78 %** · wear 12 % ·
embedding 9 % · creep 1 %. ⇒ o modelo **afrouxa devagar demais** no canal que o
`k_ratchet` governa. Autoridade do canal sobre o defeito: dominante.

## A hipótese: classe existente, valor existente

Três espécimes do KARLSEN já carregam `k_ratchet` per-espécime, autorizado pelo
professor em 2026-07-12 como **dispersão de coating HV**:

| espécime | k_ratchet |
|---|---:|
| `run7p1` (M30 HV tensionada) | **0,005** |
| `run2p2` (M30 HV tensionada) | **0,005** (convergiu no D-Y) |
| `run20p0` (M42 HV) | 0,00097 |

⚠️ **Ressalva declarada:** a `run14p2` é HV **TORQUEADA**; as outras duas M30
são **tensionadas**. Método de aperto diferente ⇒ classe de espécime
legitimamente distinta, e por isso isto é **hipótese medida**, não herança.

**Controle físico que sustenta a transferência:** as `vibralock` **não** têm o
parâmetro e **passam** (`run9p0` 0,0125/0,0323/0,0140 · `vibralock_torqued_
run16p0` 0,0474/0,0753/0,0235) — coerente com a rotação suprimida
cinematicamente pela porca wedge-cam. A classe é da **superfície HV**, não do
método de aperto, e a `run14p2` é HV.

## Premeasure (varredura de 8 pontos)

| `k_ratchet` | MAE | res.máx | σ | tripé |
|---|---:|---:|---:|---|
| nominal (ausente) | 0,0898 | 0,2363 | 0,0854 | não |
| 0,003 | 0,0215 | 0,0642 | 0,0283 | **sim** |
| 0,004 | 0,0185 | 0,0301 | 0,0135 | **sim** (ótimo de MAE) |
| **0,005** | **0,0455** | **0,0706** | **0,0218** | **sim** |
| 0,007 | 0,0993 | 0,1678 | 0,0580 | não |

**Adota-se 0,005 e NÃO o ótimo 0,004** — a regra do **D-I** proíbe escolher pelo
MAE; escolhe-se o que **compartilha**. Resultado: **zero parâmetro novo** na
campanha; o quarto espécime entra numa classe existente com o valor existente.

## Edição

Uma só, em `New_Theory/adopted_configs.json`: nova chave
`KARLSEN_2022_run14p2` com o `cfg` do grupo + `k_ratchet: 0.005`, e `prov`
declarando a classe, o valor compartilhado e a ressalva torqueada/tensionada.

## Gates (IMUTÁVEIS a partir daqui)

- **G1 (predição registrada, ±0,010/perna):** MAE **0,0455** · res.máx
  **0,0706** · σ_res **0,0218** ⇒ **entra no tripé**. Fora ⇒ INCONCLUSIVO e
  rollback pelo backup.
- **G2 (parcimônia, a razão do passo):** o valor adotado é **0,005**, idêntico
  ao de `run7p1`/`run2p2` — **nenhum número novo**. Se a curva só fechar com
  valor exclusivo, **não adota**: o ganho seria de censo, não de física.
- **G3 (isolamento):** as outras **10** curvas do KARLSEN e as 194 restantes
  **bit-idênticas** na re-simulação.
- **G4 (piso intacto):** os pisos vêm de **dado contra dado**; esta mudança é só
  de parâmetro do modelo ⇒ `limite_sres(KARLSEN)` deve permanecer **0,0903** ao
  dígito. Qualquer movimento denuncia erro de execução.
- **G5 (sincronia):** store + reports + censo + docs + suíte no MESMO commit.

### Ramos

**ADOTA** (G1–G4) · **INCONCLUSIVO** (G1 fora — rollback) · **NÃO ADOTA**
(G2 falha).

### O que este passo NÃO faz

Não toca as outras 10 curvas do KARLSEN nem propõe valor novo. Não retira a
retratação F7 da `run14p2` (`_EXCECOES_RETRATADAS_F7_PERNA_DESCOBERTA`) — ela
fica como registro histórico correto: a exceção **era** improcedente, e a curva
passa agora **por mérito**, não por perdão.

### Consequência para a fila

Se adotado, a **fila form-limited fecha em 0** — o objetivo declarado do loop —
e por **mérito**, não por declaração. ⚠️ Isso não encerra a campanha: 23 curvas
seguem em `classe_parada` (**P-7**), 23 em exceção e 14 declaradas.
