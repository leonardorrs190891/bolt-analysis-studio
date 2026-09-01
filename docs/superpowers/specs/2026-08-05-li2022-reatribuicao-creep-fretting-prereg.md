# Prereg — re-atribuição `creep`→`fretting` no LI_2022, pelo mecanismo dos autores

**2026-08-05** · decisão D-O (por delegação, MANDATO PERMANENTE) · fingerprint
de partida `e38eed05fa47`.

## ⚠️ Slip de sequenciamento, declarado antes de qualquer número

**Lancei a varredura de nível (`k_wear_flank`) ANTES de escrever este prereg.**
Ela é a medição que os gates julgam, não um pré-teste — a ordem estava errada.

**O que preserva a substância:** ao escrever este documento a saída da
varredura está **vazia** (o `| tail` retém tudo até o processo terminar) e eu
**não vi nenhum resultado dela**. Os gates abaixo são fixados sem conhecer o
desfecho. Verificável: o arquivo de tarefa estava vazio no momento da escrita.

Se algum gate abaixo falhar, o veredicto é o do gate — não haverá reescrita.

## O que os PRÉ-TESTES já estabeleceram (esses sim, antes)

**Sonda de teto de autoridade** (charter, pré-teste 2), razão de perda 20 Hz/10 Hz:

| cenário | razão | leitura |
|---|---:|---|
| base | **1,005** | o modelo é cego à frequência |
| só input corrigido (Fig. 8b) | 0,716 | 57 % da lacuna |
| só `C_creep=0` | **1,000** | **nada** isolado |
| **`C_creep=0` + input** | **0,539** | **92 % da lacuna** |
| DADO | **0,498** | |

**Achado que muda o desenho: `creep=0` sozinho não move a razão.** A
dependência de frequência só aparece **com os dois juntos**. São dois defeitos
**acoplados** — o input errado tornava a re-atribuição invisível, e a
atribuição errada tornava a correção de input insuficiente. É por isso que
quatro tentativas anteriores nesta fonte não convergiram.

**E o teto é 0,539, não 0,498.** Por isso o gate deste prereg **não pede
0,498**: pedir o valor do dado reprovaria uma alavanca que fecha 92 % da
lacuna — foi exatamente o erro que cometi no D-N (pedi 0,478, que só um flanco
de 100 % daria).

## A claim, e sua procedência

**O modelo põe 36,5 % da perda em CREEP onde o paper mede FRETTING DE ROSCA.**

* **Fig. 9** do paper: *"SEM photo of bolt thread surface topography at
  N = 2×10⁵"* — três micrografias da superfície da **rosca**.
* Texto (p6): a maior oscilação *"resulting in aggravation of the **fretting
  wear** at the contact interface and **increased damage to the thread
  surface**"*.
* Fatias medidas **dentro da janela** (`align − ratio_cru(fim)`): flanco
  **56,8 %**, creep **36,5 %**, embedding 6,7 %.

**Precedente exato na campanha:** a adoção do **LIU_2016** (2026-07-30) foi
*"re-atribuição da cauda **creep→fretting** L1 pelo mecanismo dos AUTORES"* e
levou a fonte a **14/14**. Mesmo movimento, mesma direção, mesma classe.

## Escopo: 2 mudanças, 1 número fitado

1. **Input (0 números):** `F_amp` por caso pelas razões medidas na Fig. 8(b) —
   10 Hz **inalterado** (referência), 15 Hz ×0,783, 20 Hz ×0,611.
2. **Atribuição (0 números):** `C_creep = 0` **só nesta fonte**.
3. **Nível (1 número):** `k_wear_flank` re-fitado, porque foi calibrado com o
   creep absorvendo 36,5 % — quando a atribuição muda, o fit contra a
   atribuição velha **perde procedência** (regra já aplicada no re-fit do HDPE
   do Rousseau e no `C_creep` do CACCESE).

⚠️ **Risco declarado:** `C_creep = 1,8667e-11` é o valor do bloco `shared`
canônico, com procedência de âncora (§4.7). Zerá-lo **só aqui** exige
justificativa própria, e a justificativa é o mecanismo medido pelos autores. Se
o gate falhar, **cai esta hipótese**, não o `C_creep` global.

## Gates (IMUTÁVEIS a partir daqui)

- **G1 (MECANISMO — o gate que decide):** a razão de perda 20 Hz/10 Hz tem de
  cair de 1,005 para **≤ 0,56**. Banda escolhida a partir do **teto medido**
  (0,539), não do dado (0,498) — e o resíduo de 0,041 fica **declarado e
  atribuído** ao embedding remanescente (6,7 %, cego à frequência; a álgebra
  prevê 0,513 com x=0,933).
- **G2 (ordenação):** perda(10 Hz) > perda(15 Hz) > perda(20 Hz), estrita.
- **G3 (isolamento):** `C_creep=0` **só** nos 4 casos do `LI_2022_TRIBOINT`;
  todas as outras 206 curvas do store **bit-idênticas**. O `shared` canônico
  **não é tocado**.
- **G4 (ganho):** ≥ **2** das 4 curvas da fonte no tripé, e a
  `axialmin_10Hz` (a da fila) entre elas. Se ela não entrar, **NÃO ADOTA** —
  fechar as outras três sem a da fila seria trocar o alvo.
- **G5 (nenhum caso pior):** nenhuma das 4 piora > **+0,010** em qualquer perna
  em relação ao baseline. **Inclui a `axial_10Hz_full`**, e este prereg
  **proíbe** resolvê-la por declaração (regra do mandato: estatuto não se
  decide como consequência de gate).
- **G6 (procedência escrita):** o `prov` cita a Fig. 9 (micrografias), a frase
  dos autores, o precedente LIU_2016 e diz que `k_wear_flank` é **fit de 1
  número** sob a atribuição corrigida.
- **G7 (fronteira de grade):** se o `k_wear_flank` adotado cair no extremo da
  grade varrida, **estender antes de adotar**.
- **G8 (sincronia):** adoção ⇒ re-stamp uniforme dos 210 + censo/docs/páginas/
  testes no MESMO commit.

### Ramos

- **ADOTA** — G1..G5.
- **FALSIFICADO (a atribuição não é a causa)** — G1 falha: nem com creep
  zerado e input corrigido a razão desce a ≤0,56.
- **NÃO ADOTA (o nível não fecha)** — G1/G2/G3 passam mas o G4 falha: a forma
  está certa e o nível não alcança. Registrar com o número; **não** soltar um
  segundo parâmetro.
- **NÃO ADOTA (a curva longa paga)** — G5 reprova na `axial_10Hz_full`.
- **INCONCLUSIVO** — a injeção não chega ao engine.

## Previsão registrada

Espero **G1 passar** (teto 0,539 ≤ 0,56 já medido) e **G2 passar**. Espero o
`k_wear_flank` subir ~**1,6×** (de 2,154e-13 para ~3,5e-13), porque é o fator
que devolve os 36,5 % que o creep carregava. Espero a `axialmin_10Hz`
**fechar** — ela precisa de −5 % no MAE e o input dela não muda, mas o nível
sim. **Não sei** o que acontece com a `axial_10Hz_full`: ela é 10 Hz (input
inalterado) e a re-atribuição muda a **forma** da cauda dela, que é o defeito
original; pode fechar ou pode estourar o G5. É ela o ponto de tensão.
