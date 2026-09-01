# O µ da interface é **medido** e cresce com a amplitude — e isso **explica** a Tabela 1 que eu declarara sem mecanismo

**2026-08-15 (madrugada)** · só-leitura · **nada adotado** · store `85e8104420b0`, censo
**141/205** · ⛔ **o item K está FECHADO** — ver a errata do §4: ele já estava
falsificado com prova de lei (§4.54a) e foi re-verificado hoje.

---

## 1. O que se digitalizou

A **Fig. 5(a)** do Chu 2026 (F₀ = 49 kN, Ra 0,4 µm) traz o **coeficiente de atrito medido
na interface porca-placa**, ciclo a ciclo, para três amplitudes. Extraída por **pixel
calibrado pelos ticks** — o mesmo método que, nesta sessão, reproduziu a Tabela 1 do artigo
em +1 % a partir da Fig. 2.

| curva | δ (mm) | µ inicial | µ final | N final | CSV |
|---|---:|---:|---:|---:|---|
| `Test1` | 0,3 | 0,078 | **0,135** | 1998 | `chu2026_mu_plate_D0p3.csv` |
| `Test2` | 0,4 | 0,114 | **0,258** | 1102 | `chu2026_mu_plate_D0p4.csv` |
| `Test4` | 0,7 | 0,139 | **0,473** | 1998 | `chu2026_mu_plate_D0p7.csv` |
| (`Test5`) | 1,0 | — | **0,6** | — | não está na Fig. 5; valor da **p.7** |

Validação: as durações batem com a Tabela 1 (`Test2` termina em **1102**, e o ensaio corre
a ~1105 ciclos) e os valores finais batem com a leitura visual da figura.

⚠️ **Isto corrige a minha própria nota do item K**, que dizia *"o µ cresce até 0,6"* como se
fosse o valor geral. **0,6 é o de δ = 1,0 mm** (citado na p.7 para casar a FEM com a Fig. 8);
na Fig. 5 o máximo é **0,473**.

## 2. ⚠️ O achado: isto EXPLICA a não-monotonicidade da Tabela 1

Eu havia estabelecido que *"nenhuma lei de potência única em δ ordena esta fonte"* — N até
0,9·F₀ vale **278** (δ=0,4) · **325** (0,5) · **406** (0,7) · **72** (1,0) — e registrei a
falta de mecanismo como aberta. **A Fig. 5 tem o mecanismo, medido:**

| δ | µ final medido | N até 0,9·F₀ |
|---:|---:|---:|
| 0,3 | 0,135 (plano) | **não afrouxa** |
| 0,4 | 0,258 | 278 |
| 0,7 | **0,473** | **406** |
| 1,0 | 0,6 (p.7) | **72** |

**Atrito maior ⇒ afrouxamento mais lento.** A δ=0,7 o µ mais que **triplica** e **freia** a
junta — por isso ela resiste 406 ciclos, *mais* que a de δ=0,4. A δ=1,0 o deslizamento é
grande o bastante para vencer antes de o atrito subir o suficiente.

⇒ **não é uma lei de amplitude estranha: é a competição entre atrito crescente e slip
crescente.** A "não-monotonicidade" some quando a variável escondida entra na conta.

## 3. Por que o modelo não pode reproduzir isso hoje

As **nove** curvas do `CHU_2026` rodam com **`mu = 0,15` constante**. Sem µ evolutivo, o
modelo não tem como frear a junta de δ=0,7 mais que a de δ=0,4 — e é exatamente essa
ordenação que a Tabela 1 exige.

✅ **E o engine já tem o mecanismo certo**: `mu_bearing_eff = µ·(1 − k_dmg_mu·D)` com
`k_dmg_mu` **negativo** faz o µ **subir** com o dano `D`, que por sua vez cresce da
dissipação por slip ⇒ **mais amplitude, mais D, mais µ**, que é a forma medida.

⚠️ **E a `test1` já carrega `k_dmg_mu = −2,43`** na config adotada — a única curva do CHU
com config própria, e a única que fecha quase perfeita (MAE 0,0035). O mecanismo está lá,
aplicado a **uma** curva, sem nunca ter sido confrontado com a Fig. 5.

## 4. ⛔ ERRATA (mesma sessão, 1 h depois): o item K JÁ ESTAVA FECHADO — e eu re-fiz trabalho feito

Ao procurar onde ligar o µ medido, encontrei três coisas, nesta ordem:

1. **`JointMaterial.mu_bearing_schedule` já existe** (F3, 2026-07-21, prereg `F3.2-CHU`) e
   o docstring **nomeia a Fig. 5 do Chu 2026** como o exemplo. É input de **medição**,
   declarado *"NUNCA fittable"*. ⇒ o meu plano de *calibrar* `c_D`/`k_dmg_mu` contra o µ era
   **ajustar o que o projeto decidiu medir**.
2. **A Fig. 5 já estava digitalizada** em `digitized_csv/chu2026ti_fig5_muplate_*.csv`. A
   minha digitalização é **duplicata** — o comando que a teria evitado é
   `ls digitized_csv/ | grep chu`. ✅ Serve como **replicação independente**: as duas
   concordam a **MAE 0,0026–0,0034** (viés ≈ 0) numa faixa de µ de 0,10 a 0,47 — ~1 % da
   faixa, e isso fixa o **piso de digitalização** desta figura.
3. **O experimento já tinha sido feito e o resultado gravado** (`chu_schedule_isolado.json`):
   o µ medido isolado dá MAE **0,11–0,17**, contra o critério congelado de <0,10.

### Re-medido hoje (fp `85e8104420b0`), porque §4.43 vale para fracasso também

| curva | store atual | com o µ medido | Δ MAE |
|---|---|---|---:|
| `test2` | 0,1567/0,5259/0,1909 | 0,1549/0,5213/0,1897 | −0,0018 |
| `test4` | 0,1352/0,2264/0,1250 | 0,1526/0,2360/0,1308 | **+0,0174** |
| `test7` | 0,1499/0,2702/0,1672 | 0,1422/0,2378/0,1597 | −0,0077 |
| `test8` | 0,1613/0,3932/0,1935 | 0,1536/0,3447/0,1828 | −0,0077 |

⇒ **efeito minúsculo e de sinal misto**; todas seguem em MAE 0,14–0,15. O veredito de
2026-07-21 **sobrevive** ao re-carimbo duplo do CHU (rz da sessão B + `D1p0`).

### E a razão é de LEI, já registrada: §4.54a

*"Chu = form-limited com prova em nível de lei: **µ medido prescrito ≈ inerte** — wear
disp-mode é **Archard, sem µ**."* Em modo deslocamento o canal dominante não contém µ, então
injetar o µ **certo** não pode mover o que domina a perda.

⇒ **item K CLOSED.** Não é "não tentamos": é *tentado, falsificado com prova de lei, e
re-verificado contra o fingerprint de hoje*.

## 5. O que deste documento SOBREVIVE

O §2 — a explicação **mecânica** da não-monotonicidade da Tabela 1 — é novo e não depende do
item K. Ele diz por que o **DADO** é não-monotônico (atrito cresce e freia a junta), e a
§4.54a diz por que o **MODELO** não pode usar isso. As duas juntas fecham o quadro: o
fenômeno tem mecanismo medido, e o engine não tem o canal por onde ele agiria.

## 6. (registro) O que isto habilitaria — plano SUPERADO pela errata acima

Calibrar `c_D` + `k_dmg_mu` **por fonte** contra as três curvas de µ — não contra a
pré-carga. Isso é qualitativamente diferente de tudo que a campanha fez nesta fonte:

* o alvo é uma quantidade **medida e publicada**, não a curva que se quer ajustar;
* há **três** curvas de µ para **dois** números ⇒ o ajuste é sobredeterminado;
* e o veredito na pré-carga vira **predição**, não ajuste.

⚠️ **Gate que a execução terá de carregar:** o `c_D`/`k_dmg_mu` ajustado ao µ **não pode**
ser re-ajustado se a pré-carga não fechar. Se a µ certa piorar a pré-carga, isso é
resultado — e é informação sobre o modelo, não licença para refitar.

## 7. O que NÃO se afirma

Não se afirma que isto fecha as curvas do CHU. A `test1` (δ=0,3) tem µ **plano** e já fecha;
as demais têm µ crescente e estão fora — e a errata do §4 mostra que a forma medida **NÃO**
as aproxima (efeito de sinal misto, ≤0,008 nas que melhoram).

## Reprodutibilidade

`chu_fig5_extrai.py` no scratchpad; CSVs em `New_Theory/chu2026_mu_medido/`.

⚠️ **Nota de método:** a 1ª calibração de y saiu errada — foram detectados **5** ticks para
**6** rótulos (0,0 a 0,5) e eu ancorei o zero no tick mais baixo *detectado*, que é 0,1. A
`Test1` saiu com **µ = −0,022**, valor impossível, e o absurdo denunciou na hora. O conserto
extrapola um passo abaixo do último tick **e afirma** que o zero cai na moldura inferior
(`assert`), para a próxima calibração não passar em silêncio.
