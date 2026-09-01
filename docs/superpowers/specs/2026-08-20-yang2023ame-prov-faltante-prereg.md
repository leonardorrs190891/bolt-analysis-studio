# PREREG — a `prov` das 2 constantes do `YANG_2023_AME` (a suíte está VERMELHA e o texto já existe)

## Estado

**PENDENTE — aguarda assinatura.** Nada executado. Escrito em 2026-08-20 (23:5x) contra
o store **`89b1899f18c1`** (uniforme, 210 registros, zero divergentes), censo `_censo()`
tripé **166/205**.

⚠️ **A adoção é da sessão paralela** (`ba3d847`). Este prereg existe para que a execução
seja possível **sob gates** por quem chegar primeiro; a regra de 1 escritor por recurso
continua valendo para o `adopted_configs.json`.

---

## 1. O defeito: suíte vermelha desde 22:0x

```
tests/test_procedencia_catraca.py::test_passivo_de_procedencia_nao_cresce
   2 constante(s) NOVA(s) adotada(s) sem entrada em prov:
       YANG_2023_AME::N_emb
       YANG_2023_AME::emb_um
```

Introduzidas por **`ba3d847`** (22:0x, `git log -S "YANG_2023_AME"`). A suíte segue
vermelha há **mais de 1 h30**, e **uma adoção foi commitada nesse estado**
(`ae4b5aa`, 23:32 — correção de input no BAUER), contra a regra do charter *"suíte
completa antes de todo commit de adoção"*.

⚠️ **Isto não é acusação de número errado:** o `cfg` está certo e as métricas fecham
(0,0285/0,0388/0,0103 = 0,57×/0,39×/0,41×). O que falta é o **campo que diz de onde os
números vieram** — e a catraca de procedência existe justamente para que constante nova
não entre sem essa frase.

## 2. Por que isto NÃO é fabricar procedência

A tentação errada seria eu redigir uma origem plausível. **Não é o caso:** a origem está
**escrita no prereg dos próprios autores da adoção**
(`2026-08-20-yang2023ame-emb-lento-prereg.md`), e transcrevê-la para o `prov` é
exatamente a função do campo.

| fato | onde está escrito |
|---|---|
| física nomeada pelos AUTORES do paper — *"bolt-head embedment into the composite surface [é] the dominant, almost exclusive, preload-loss mechanism"* (CFRP S22, YC = 23 MPa; porca travante suprime rotação) | nota de aparato, citada no §2 do prereg |
| forma: `EmbeddingLoss` state-based com relógio lento (`N_emb` ≫ janela) — **a forma que os autores nomeiam** | §2 |
| números: regressão do closed-form **no dado cru**, `r = 1 − A·(1−e^{−N/τ})`, **r² = 0,92**, resid_máx 0,0174 | §2 |
| ⚠️ **degenerescência DECLARADA**: `(A, τ)` não se separam na janela de 1100 ciclos — **só a taxa `A/τ = 8×10⁻⁵/ciclo` é identificável**; log-creep fita igual (r² = 0,91) | §2 |
| escolha da célula: grade 3×3, **6 de 9 fecham**; célula por **centralidade** (3/3 vizinhos) + pior perna (0,57×) | §3 |
| contagem honesta: *"2 fitados com degenerescência DECLARADA (efetivamente 1 = a taxa regredida)"* | §3 |

⇒ a classe de procedência é **`fitado-this-rig` com o gate que a justificou**, que é
literalmente o que a mensagem do teste pede.

## 3. Texto proposto (transcrição, não invenção)

Para **ambos** os campos, chave composta `emb_um/N_emb` (idioma aceito pelo teste quando
um argumento cobre vários):

> `fitado-this-rig (regressao do closed-form no CRU: r = 1 - A*(1-e^{-N/tau}), r2=0.92,
> resid_max 0.0174; gate = grade 3x3 com 6/9 celulas fechando, celula por CENTRALIDADE
> 3/3 vizinhos + pior perna 0.57x). Forma NOMEADA PELOS AUTORES: nota de aparato G8
> registra bolt-head embedment na superficie do composito como mecanismo dominante e
> quase exclusivo (CFRP S22, YC=23 MPa, porca travante suprime rotacao).
> ⚠️ DEGENERESCENCIA DECLARADA: (A, tau) nao se separam na janela de 1100 ciclos — so' a
> TAXA A/tau = 8e-5/ciclo e identificavel, e log-creep fita igual (r2=0.91) ⇒ contam como
> 1 fitado efetivo, nao 2. Escopo: ESTA janela/carga (1 curva, 1100 ciclos, embedment
> dominante); extrapolacao viscoelastica de longo prazo NAO validada (o alvo A satura no
> bound = o dado nao contem a saturacao). Prereg: 2026-08-20-yang2023ame-emb-lento.`

## 4. Gates CONGELADOS

| # | gate | critério |
|---|---|---|
| **G1** | a catraca fecha | `test_procedencia_catraca` **4/4** (era 3 passed / 1 failed) |
| **G2** | métrica intocada | `Δ = 0,0000` nas **210** curvas — `prov` é metadado e **não** entra em predição |
| **G3** | censo intacto | `_censo()` **bit-idêntico**: tripé 166 · resolvidos 188 · declarado_total 200 |
| **G4** | re-carimbo completo | o hash cobre a entry inteira **incl. `prov`** (precedente R2, 2026-08-16) ⇒ fingerprint MUDA e o store tem de ficar **uniforme nos 210**, zero divergentes |
| **G5** | o sintético não fica atrás | `exemplo_m12_sintetico` está **fora** do universo do `parallel_batch` ⇒ re-sim direta + carimbo manual, e **reler** depois de escrever (gotcha do `CLAUDE.md`) |
| **G6** | formato preservado | `git diff --numstat` do `adopted_configs.json` ≈ **2 linhas**; round-trip de formato conferido antes de escrever (precedente: +2,2 MB no store por `indent` errado) |
| **G7** | suíte | completa e **VERDE** — é o objetivo do item |

**Ramos:** `EXECUTA` · `RECUSA` (a ausência é deliberada ⇒ então a saída correta é
`_SEM_PROV_BASELINE` **com o motivo**, que o próprio teste oferece — não apagar o teste) ·
`INCONCLUSIVO` (o texto do prereg não sustenta a transcrição ⇒ quem adotou escreve).

## 4b. ⚠️ NÃO há deadlock — o precedente R2 já resolveu a aparência de impasse

Ao reler a regra do charter (*"suíte completa antes de todo commit de adoção"*) eu quase
publiquei que a situação é um **deadlock**: a suíte está vermelha, o único conserto limpo
**é** uma adoção (porque `prov` está dentro do hash), logo consertar exigiria violar a
regra que o conserto restaura.

**Falso, e a prova está no precedente que eu mesmo executei.** A **R2** (2026-08-16) foi
uma adoção de **metadado puro** — trocou dois rótulos `prov` do `ECCLES` sem tocar `cfg` —
e o seu gate de suíte diz, textualmente:

> **G5** suíte completa — ✅ **988 passed · 1 skipped, idêntico ao baseline**

⇒ o gate é de **NÃO-REGRESSÃO contra o baseline**, não de verde absoluto. Foi essa a
leitura que apliquei ao G6 do item W (1052 passed · 1 failed, com a falha atribuída por
medição a `ba3d847` e declarada em vez de silenciada), e é a mesma que vale aqui — com a
diferença favorável de que **este item existe para levar a contagem de 1 failed a 0**.

⚠️ Registro porque a conclusão errada era barata de publicar: *"impasse estrutural nas
regras da campanha"* soa profundo, custa zero para escrever, e estaria errada por não ter
lido o único precedente que trata exatamente do caso (adoção de metadado). Terceira vez em
dois dias que a prova gravada estava à frente da minha dúvida.

## 5. O que este item NÃO faz

- **Não** mexe em `cfg`: nenhum número de física muda, nenhuma curva se move.
- **Não** julga a adoção `ba3d847` — as métricas dela fecham com folga.
- **Não** inventa origem: cada frase do §3 tem linha correspondente no §2/§3 do prereg
  original, e a degenerescência vai escrita porque **omiti-la** é que seria super-afirmar.
