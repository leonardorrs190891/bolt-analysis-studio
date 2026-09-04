# Variável varrida não é réplica — os 9 tickets pagos, 2026-08-23

**Pedido do professor:** *"o que podemos fazer para não considerar replica uma variável?"* e,
em seguida, *"corrija tudo"*.

**Resposta em uma frase:** a condição de réplica passa a sair dos **inputs**, não de lista à
mão — as colisões de assinatura caíram de **57 para 21**, e as 21 que restam são todas
**corretas**.

Só-leitura na física: nada adotado, nada re-carimbado, fingerprint intocado.

---

## 1. O que estava errado

Uma curva era tratada como réplica de outra quando as duas tinham o mesmo
`to_solver_config()`. Isso é a regra certa — o problema é que a **variável que o paper
varre** não chegava ao `ValidationCase`. O `case_id` a nomeava (`lk19p8`, `Ra0p306`,
`af8p75kn`, `t12`, `reassy04`), ou seja **alguém já a leu do paper ao digitalizar**, e ela se
perdia no caminho até o dataclass.

Custo medido, e não é hipotético: esse defeito já **retratou exceções sete vezes** — carga
axial do ECCLES, grip do ICMEZ, rugosidade do CHU, protocolo do LU, espessura do ROUSSEAU,
condições do CACCESE, e o teste de premissa F5 lendo a `eccles fig7` como *"ensemble de 4
réplicas"*. Em todos, o modelo estava certo em espécie: **aos olhos dele elas eram réplicas**.

## 2. O que foi feito

Seis campos em `ValidationCase`, **lidos do `case_id`** por padrões explícitos por fonte
(`_varredura_por_curva`, em `core/validation_cases.py`):

| campo | fonte | lê de |
|---|---|---|
| `axial_force_amplitude_N` | LIU_2016 · LIU_2017_AXIAL | `af7p5kn`…`af12p5kn` |
| `roughness_Ra_um` | LI_2022_MARSTRUC · CHU_2026 | `Ra0p078`…`Ra0p8`, `Ra1p6um` |
| `grip_length_mm` | ICMEZ_2025 | `lk13p8` / `lk19p8` |
| `member_thickness_mm` | ROUSSEAU_2025 | `steel_t10` / `hdpe_t14` |
| `reassembly_count` | SUN_2025_REASSY | `reassy02`…`reassy10` |
| `specimen_label` | JCSR · CACCESE · GRZEJDA · LIU_2016 · SUN_CRIMP · QIN | material/ambiente, geometria/protocolo, posição, lubrificante/torque, graxa×porca, interferência |

Dois rótulos exigiram cuidado próprio:

- **`SUN_2025_CRIMP` varre DUAS coisas no mesmo nome** — lubrificação e tipo de porca — e
  **`nogrease` contém `grease`**, o trap de substring que o `CLAUDE.md` documenta. A
  alternância põe `nogrease` **primeiro**, senão toda curva seca é lida como engraxada.
  Medido: `nogrease_standard` × `grease_crimp`, corretos.
- **`QIN_2024` `i0pct`/`i0p6pct`/`i1p2pct`** é a **percentagem de interferência do ajuste**,
  `I = (d−D)/D × 100 %` — nomeada na nota de aparato (`qin2024acm.md`, L80-81). Entra como
  **rótulo, não número**, porque a própria nota registra que é *"state variable with no
  current analog in BAS V2"*: distinguir é o que se precisa; dar-lhe escala física afirmaria
  mais do que o modelo representa. ⚠️ Eu estava a um passo de rotular como *"variável i,
  significado desconhecido"* — a prova estava escrita no repositório, e o gotcha das quatro
  portas mede que ~6 de 20 conclusões erradas minhas tinham essa mesma propriedade.

**Padrões explícitos de propósito.** Um parser genérico acertaria mais casos e erraria **em
silêncio**; o que não casa fica em `0`/`""`, que aqui é afirmação de *"não se aplica"*, não
ausência.

## 3. O resultado

**57 → 21 colisões.** As 21 restantes, por que ficaram:

| fonte | n | por que está certo |
|---|---:|---|
| `LIU_2022_RETIGHT` | 17 | estágios `t0..t3` do **mesmo** ensaio; quem distingue é a cadeia `chain:"retight"` |
| `CACCESE_2009` | 2 | `tapered_45kN_rep1`×`rep2` = **réplica de verdade**, o par que mede o piso do D-I |
| `LU_2024` | 2 | `fig18_amp1p0`×`fig20_T22Nm` = **o mesmo ensaio em 2 figuras** (`_CID_NAO_COMPARAVEL`) |

⇒ o CACCESE caindo de 5 para **exatamente o par de réplicas** é a prova de que a guarda
separa réplica de variável varrida, em vez de só reduzir um número.

## 4. Três defeitos que só apareceram porque a guarda NOMEIA as curvas

**(a) `af8p75kn` tem dois dígitos depois do `p`.** Com `(?:p(\d))?` o casamento **inteiro**
falha (o `kn` não encaixa) ⇒ campo `0.0` em silêncio, e as curvas de 8,75 e 11,25 kN voltam a
colidir. Um parser genérico teria lido **8,7** e ninguém veria. Quem denunciou foi a guarda
listando o par que ainda colidia. Preso em `test_o_valor_lido_do_case_id_e_o_do_PAPER`, que
existe porque a guarda de colisão **não cobre isto**: ela só exige que as assinaturas
*difiram*, e valores errados também são distintos.

**(b) `\b` numa string não-raw é BACKSPACE, e ao contrário de `\d` não avisa.** O padrão que
escrevi como `(standard|crimp)\b` chegou ao arquivo como `(standard|crimp)\x08` — um byte de
controle **0x08 literal** dentro do `r"..."` — porque a escrita passou por uma string não-raw
que colapsou `\\b` em `\b`. Efeito: o regex do SUN nunca casava, `specimen_label` ficava `''`,
e a fonte seguia colidindo. **A assimetria é o que torna isto perigoso:** `\d` é escape
*inválido* ⇒ Python emite `SyntaxWarning` e **preserva** o texto (por isso os `\d` funcionaram);
`\b` é escape *válido* ⇒ conversão **silenciosa**. Os avisos de `\d` que eu tratei como
cosmética eram a metade **visível** do mesmo problema. Diagnóstico que fechou: `co_consts` do
`__code__` mostra o padrão **como está no arquivo** — eu vinha testando o regex
**redigitando-o**, que é testar a intenção, não o artefato. Varredura confirmou **1** byte
0x08 no arquivo e nenhum outro caractere de controle.

**(c) `grip_length_mm` colide com o V1, e não é a mesma grandeza.** O
`CoupledLooseningConfig.grip_length_mm` do `solver_worker` é o grip **total** (default 48 mm =
3·d para M16); o `lk13p8` do ICMEZ é o comprimento agarrado daquele rig (**13,8 mm**). Emitir
o campo em `to_solver_config()` sobrescreveria o do V1 em silêncio, com fator ~3,5. Registrado
no próprio campo.

## 5. Os campos são INERTES na física — quatro medições independentes

1. **Nenhum dos 6 nomes é campo de `JointMaterial`** ⇒ `material_kwargs_for`, que filtra pelo
   dataclass, não os passa (`test_os_campos_novos_sao_INERTES_na_fisica`).
2. **`to_solver_config()` não os emite** (medido: 8 chaves, nenhuma delas).
3. **Nenhum consumidor em `src/` os lê de um `ValidationCase`** — todos os acertos do grep são
   parâmetros homônimos do V1, que tiram valor da geometria dos elementos.
4. **Zero leitura dinâmica** (`vars`/`asdict`/`fields(case)`) no caminho da física, e o
   `to_dict()` enumera campos **por nome** ⇒ campo novo não vaza, tem de ser adicionado à mão.

Confirmação empírica: re-simulação de **17 curvas** — as 9 fontes tocadas mais controles
(`bauer2024_M8_fig6_rep1`, `eccles2010_fig6`) — com **Δ = 0,000e+00 exato em todas**.

⚠️ **A inércia é DELIBERADA.** Os campos servem à **detecção de réplica**. Levá-los à física é
passo separado e gateado — foi assim com o `external_axial_N`, cuja camada C3 (piso anulável)
acabou **falsificada** pela monotonia piso-vs-axial. Campo que entra no registry e na física no
mesmo commit não tem como ser falsificado em separado.

⚠️ **Erro meu no caminho, e vale como método:** tentei provar a inércia comparando
`config_used` do store contra `_effective_overrides` e obtive **210 de 210 divergentes** — o
que li, por um instante, como regressão total. Não era: são **objetos diferentes**
(`config_used` é o registro dos inputs, com `mode`/`emb_um`/`grip_mm` e o `overrides`
aninhado; `_effective_overrides` devolve os kwargs achatados). *"Tudo divergiu"* quase nunca é
regressão — é assinatura de comparação errada, porque **mudança estreita toca conjunto
estreito**. Seis campos lidos de nomes de arquivo não poderiam tocar curvas da âncora interna. É a porta
**(A)** do gotcha das quatro portas, e eu caí nela **duas vezes** nesta mesma tarefa (a
primeira foi medir colisões com o `_CAMPOS` antigo, que ainda não conhecia os campos novos).

## 6. O que isto DESTRAVA — e a medição é honesta sobre o limite

A lista manual `_SEM_FAMILIA_MECANICA` bloqueia **81 curvas em 14 fontes** de entrar em
família automática. Ela existe porque a chave de pareamento é
`(src, delta_mm, F_amp_N, mode)` — **cega** a grip, rugosidade, espessura, axial, espécime.

Simulação só-leitura, lista **desligada** e chave **estendida** pelos 6 campos novos + os 2 do
axial:

| | curvas em família automática |
|---|---:|
| chave cega (hoje, sem o bloqueio) | **74** |
| chave estendida | **24** |

⇒ **−68 % de pareamento espúrio**, e o resíduo se separa em duas classes.

**Correto — 15 curvas que DEVEM continuar pareadas:**

| par | por que está certo |
|---|---|
| `CACCESE rep1+rep2` | réplica de verdade (o par do piso do D-I) |
| `YANG_2021 r1+r2+r3` | três réplicas reais, já declaradas |
| `CHU test5+test6_repeat` | repetição da mesma condição, dita no nome |
| `LU amp1p0+T22Nm` | o mesmo ensaio em duas figuras |
| `LIU_2016 1e6cyc+5e6cyc` | mesma condição, durações diferentes |
| `ECCLES` ×4 sem axial | mesma condição nominal — inclui o `fig8a`×`fig8c`, par legítimo que o bloqueio manual **proibia** |

**Fontes RESOLVIDAS por inteiro** (zero família espúria): `ICMEZ_2025` · `JCSR_2023` ·
`QIN_2024` · `ROUSSEAU_2025` · `SUN_2025_CRIMP`, e o `CHU_2026` reduzido à repetição genuína.

⚠️ **Sobram 9 curvas em TRÊS tickets — e o achado mais útil desta medição é que os três pedem
campo que o registry JÁ TEM:**

| fonte | pares que sobram | variável ausente | já existe? |
|---|---|---|---|
| `LI_2022_TRIBOINT` | 10 Hz + 15 Hz + 20 Hz | **frequência** | ✅ `frequency_Hz` |
| `LI_2022_MARSTRUC` | 5 + 10 + 15 kN a Ra 0,8 | **pré-carga** | ✅ `initial_preload_N` |
| `KARLSEN_2022` | `M42_HV_run21p0` + `M42_vibralock_torqued_run29p0` (mesmo F_amp 274 kN) | **dispositivo de travamento** | ✅ `locking_device_type` (em `LoadingData`) |

⇒ **a lista manual compensa uma CHAVE GROSSA — não falta de dado.** Isso muda o custo da rota:
levar `frequency_Hz` e `initial_preload_N` à chave é uma linha cada, não campanha de
digitalização.

## 6b. O precedente que valida a tese — e ele foi pago à mão, curva por curva

O par `eccles2010_fig8a`×`fig8c` **já é declarado** (`_PARES_REPLICA_DECLARADOS`, prereg
`eccles-par-replica-declarado`, 2026-08-15), e **duas provas de exceção assinadas repousam no
piso dele**. O motivo registrado do re-cálculo daquele piso, citado do próprio
`report_html.py`:

> *"O anterior (0.257/0.083) era o piso **INVÁLIDO** que a P-15 retratou: dispersão entre
> cargas axiais de 0 a 3,5 kN, **a variável varrida do paper**. O válido vem do par declarado
> fig8a×fig8c — baseline1/baseline2, **rótulo DO AUTOR**, ambos axial=0."*

⇒ em agosto o projeto **já havia diagnosticado exatamente este defeito**, e o consertou
**declarando um par à mão** para uma fonte. Este trabalho é o mesmo conserto feito
**sistemicamente**, a partir do input em vez do julgamento. E a existência dessas duas provas
é a razão concreta pela qual a §7 não é formalidade: mexer na chave sem gate poderia derrubar
o denominador de exceções assinadas.

## 7. ✅ ASSINADO E EXECUTADO no mesmo dia

O professor assinou o ITEM X e a chave estendida foi adotada —
`New_Theory/chave_estendida_pareamento_resultado.md`, prereg
`specs/2026-08-23-chave-estendida-pareamento-prereg.md`, **8 gates verdes e G6 reprovando
como escrito** (gate mal especificado, mantido vermelho).

O número que a execução acrescentou a este documento: a cegueira **inflava** a barra de σ
do `ECCLES_2010` em **51 %** (piso 0,0852 com chave cega × **0,0565** com a chave
estendida). Barra inflada não reprova — **aprova**. O defeito premiava a si mesmo, e é por
isso que o teste central da entrega proíbe qualquer piso de subir, em vez de contar
famílias.

Texto original desta seção, preservado:

## 7b. O que precisava de assinatura

Estender a chave de pareamento **mexe na medição do piso**, e o piso é o que assina exceções
F7. Não é mudança de sessão: pede prereg com gates (nenhuma exceção assinada pode perder a
prova; nenhum piso pode subir de modo que aprove curva hoje reprovada) e re-medição das 44
provas vigentes. A medição da §6 é o **payload** dessa proposta, não a execução dela.

## Reprodutibilidade

```bash
py -3.12 -m pytest tests/test_variavel_varrida_nao_e_replica.py -q   # 18 testes
```

A guarda **falha quando a dívida cai** — de propósito, para forçar o registro de qual campo
resolveu. O baseline vigente é 3 entradas, todas da classe **(L) legítima**.
