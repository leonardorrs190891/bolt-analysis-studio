# Prompt — atacar as curvas abertas do BAS_V2

Cole o bloco abaixo numa sessão nova. Ele é **auto-contido**: não pressupõe
contexto de conversa anterior, e manda a sessão medir o estado em vez de
acreditar em números escritos aqui (que envelhecem).

Gerado em 2026-08-17 contra o store `7a60cacb72de`, censo 144/205.

---

```
Trabalhe nas curvas ABERTAS do BAS_V2 — as que estão fora do tripé e NÃO têm
exceção nem declaração assinada. É a minha prioridade.

## 1. Primeiro MEÇA o estado; não confie em número escrito

    py -3.12 New_Theory/lista_abertas.py       # gera lista_abertas.md/.csv
    py -3.12 New_Theory/regra_de_parada_triagem.py

A lista é recomputada do store. Se ela discordar de qualquer número em prosa,
a lista está certa e a prosa envelheceu (§4.43 do MODEL_LEGITIMACY).

## 2. As abertas NÃO são uma fila única — são dois grupos com trabalhos opostos

Isto foi medido em 2026-08-16/17 e está em `New_Theory/plano_das_21_abertas.md`
e `New_Theory/piso_impossivel_nas_5_fontes.md`. Confirme, não repita:

GRUPO A — a fonte TEM piso de repetibilidade medido, e ele está ABAIXO do limite
global. Ou seja: o dado é mais repetível que a barra, a barra é generosa, e o σ
do modelo é ERRO REAL (1,8× a 23× o ruído do próprio dado). São ~6 curvas
(LU_2024 ×1, YANG_2021 ×3, LIU_2025 ×2).

GRUPO B — a fonte NÃO tem piso, e não é falta de procurar: ICMEZ (4 pares, TODOS
diferem em grip 13,8×19,8 mm), ROUSSEAU (par difere em espessura), SUN (pares
cruzam tratamento crimp/graxa), YANG_2023 e YANG_2019 (nenhuma condição
repetida existe). São ~15 curvas.

⛔ Para o GRUPO B, varrer alavanca é desperdício: não se sabe se o modelo erra
ou se a barra de 0,025 é dura demais, e a resposta NÃO está no modelo. A única
rota é dado novo (uma réplica na mesma condição, mesmo rig) — decisão do
professor, não sua.

## 3. O que JÁ FOI FALSIFICADO — leia antes de propor qualquer coisa

Cada curva aberta tem forma nomeada com documento (a coluna `forma_nomeada` do
`lista_abertas.csv`). Não re-descubra:

  ICMEZ ×5     New_Theory/icmez_arresto_sub_piso_resultado.md
               (o modelo trava num piso FITADO que o dado atravessa; 6 famílias
               falsificadas em 26 células; a capacidade `loose_arrest_residual`
               foi construída default-inerte e a ADOÇÃO reprovou nos gates)
  ROUSSEAU ×4  New_Theory/rousseau_ratchet_transferencia_resultado.md
               (k_ratchet falsificado em 10 células; ótimos por curva DISJUNTOS;
               ⚠️ `loose_amp_exp<1` AMPLIFICA em rig de slip pequeno — o
               parâmetro faz o oposto da intenção abaixo de LOOSE_AMP_REF=0,5mm)
  YANG_2021 ×3 New_Theory/yang2021_stick_sustentado_resultado.md
               (8 de 8 em STICK; o `gth` já está adotado e mexer nele dá NET ZERO)
  YANG_2023 ×3 New_Theory/yang2023_piso_nunca_lido.md
               (a rota do piso foi falsificada em 2026-08-16: o leitor canônico
               `floor_from_curve` devolve plateau=False nas 7 que afrouxam — o
               dado NÃO arresta, colapsa a 0,02–0,06)
  LIU_2025 ×2  New_Theory/liu2025_par_de_taxas_opostas.md
  SUN ×2       New_Theory/sun2025_canal_rotacional_morre_cedo.md
               New_Theory/sun_crimp_o_cadeado_estava_certo.md
  LU_2024 ×1   New_Theory/lu2024_T10Nm_embedding_sem_pressao_resultado.md
               (dois defeitos: o de 1º ciclo tem lei — `emb_pressure_exp`, já
               construída default-inerte — e NÃO fecha a curva; o terminal não
               tem lei nesta fonte porque o dado é não-monótono E PUBLICADO)

E a regra de parada foi medida em `New_Theory/regra_de_parada_medida_2026-08-16.md`:
ela DISPARA na fila julgável. Se você propuser trabalho ali, precisa dizer por
que o veredito dela não vale.

## 4. Como trabalhar (a disciplina não é opcional aqui)

- PREREG ANTES DE MEDIR, com gates congelados, em docs/superpowers/specs/.
  Inclua sempre o ramo INCONCLUSIVO ("o teste não testou") — sem ele o script é
  forçado a escolher entre PASSA e FALSIFICADO e escreve veredito sobre teste
  vazio.
- Registre uma PREDIÇÃO antes de rodar. Se o resultado bater, ótimo; se não
  bater, a discrepância é o achado.
- Gate de CONTROLE da fonte inteira ANTES de olhar a curva-alvo (precedente
  D-AB: a alavanca de melhor ajuste na alvo era a 2ª pior para a fonte).
- Procedência > fit. Ler um input (VDI, tabela do paper, platô do dado) vale
  mais que ajustar constante. Constante por curva sem procedência é proibida.
- `py -3.12`, nunca `python` (o do PATH é 3.13 sem numpy).
- Uma sessão por recurso: adoção de config é escritor único e re-carimba o store
  inteiro (~30 min). Confira `git log -1` do arquivo IMEDIATAMENTE antes de
  escrever, e releia o valor DEPOIS de escrever.

## 5. As armadilhas que já custaram caro aqui — todas medidas, não teóricas

1. `FLOOR_TRIM = 0.10` NÃO é filtro de métrica: ele ENCURTA A SIMULAÇÃO. Toda
   leitura de terminal (do dado OU do modelo) exige `FLOOR_TRIM = 0` num sandbox.
   Isso me mordeu QUATRO vezes num dia, sempre disfarçado de outra coisa — a
   última publicou um resultado positivo que era falso.
2. `np.interp` GRAMPEIA fora do domínio. Interpolar o modelo em N=99 numa
   simulação truncada em N=54 devolve o valor de 54 sem avisar.
3. Δ = 0 EXATO não é "parâmetro morto" até você conferir os COMPANHEIROS do
   canal (gates desligados, modo errado, canal em zero na decomposição).
4. Varredura MARGINAL acha ótimo CONDICIONAL. Forma e nível são acoplados — se
   você vai declarar "a constante está no ótimo", varra as duas juntas
   (precedente D-Z: a mesma constante saiu de "não melhora em dose nenhuma" para
   "melhora as três pernas" depois que a forma mudou).
5. Fatia grande na decomposição ≠ capacidade. Confira a MAGNITUDE ABSOLUTA do
   trecho-alvo antes de desenhar forma sobre um canal.
6. Pareamento de réplica inválido já foi invalidado SEIS vezes. Par declarado
   tem de ser a MESMA junta (grip, bitola, Rz, µ, modo, freq, drive) — há guarda
   em tests/test_par_de_replica_e_mecanicamente_identico.py.
7. `json.loads` não reclama de chave duplicada, e `getattr(mod, "X", {})`
   devolve {} em silêncio quando X é local a uma função. Releia o que escreveu.

## 6. O que CONTA como progresso, e o que não conta

CONTA:
  · uma curva fecha o tripé sob os gates de um prereg;
  · uma alavanca é FALSIFICADA com predição registrada (isso é resultado, não
    fracasso — é o que permite fechar uma classe honestamente);
  · um input passa a ser LIDO com procedência em vez de fitado;
  · um par de réplica VÁLIDO é declarado e destrava o piso de uma fonte
    (precedente: ECCLES fig8a×fig8c levou o limite de 0,025 para 0,0698).

NÃO CONTA:
  · baixar a barra de σ_res (no Grupo A o dado é 1,8–23× mais repetível que o
    limite; afrouxar esconderia erro real);
  · declarar curva para inflar o "resolvido" (declaração é "não dá para julgar",
    não "o modelo acertou");
  · constante por curva sem procedência;
  · qualquer número que suba sem prereg e sem gate.

## 7. Comece assim

Escolha UMA curva do GRUPO A (as do Grupo B estão bloqueadas por falta de dado),
leia o documento da forma nomeada dela, e me diga em 5 linhas: qual defeito está
nomeado, qual alavanca já foi falsificada, e o que você faria de DIFERENTE. Não
comece a varrer antes disso.

Se a sua conclusão for que não há rota, diga isso com número — é um resultado
válido e a campanha já o registrou várias vezes.
```

---

## Como eu usaria este prompt

**Não use para o Grupo B.** Ele diz isso explicitamente, mas vale repetir: são
15 das 21, e ali o trabalho não é de modelo — é uma réplica de ensaio.

**Use para o Grupo A, sabendo que a regra de parada dispara ali.** Se a sessão
nova encontrar rota, ótimo — o veredito da parada reabre sozinho (há guarda em
`tests/test_parada_reabre_quando_deve.py`). Se não encontrar, ela terá de dizer
com número, e isso confirma a parada em vez de desperdiçar o esforço.

**As duas curvas mais perto** são `yang2021_amp0p6mm_ax8kN_r1` (1,07× o limite) e
`liu2025_M16_fig2_single` (1,08×) — precisam de ~7 % de redução no σ_res. Mas as
duas estão em `classe_parada`, e o σ delas é 2,6× e 1,8× o ruído do próprio dado.
