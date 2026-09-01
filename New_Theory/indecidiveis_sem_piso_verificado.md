# As 10 "indecidíveis sem piso" estão **corretamente** classificadas — verificado curva a curva

**2026-08-14** · só-leitura · **nada adotado** · store `2c05ea70c046`, censo **147/205**.

## Por que verificar

A camada `indecidivel_sem_piso` (10 curvas, 17 % das 58 fora) é a única do estatuto cujo
rótulo *sugere* trabalho possível: *"falta 1 réplica"* lê-se como *"consiga a réplica e
destrava"*. Se alguma das 3 fontes tivesse par de **mesma condição** não aproveitado, o piso
sairia de graça e a curva sairia da indecidibilidade.

Vale medir porque uma delas está **a 21 % do limite**: a `sun2025…grease_crimp` faz
σ = **0,0303** contra o limite global 0,025, com MAE 0,0221 e res.máx 0,0886 — as outras duas
pernas **passam**. É a curva da biblioteca mais perto de mudar de estatuto por piso.

## As 10, por fonte

| fonte | n | há par de mesma condição? |
|---|---:|---|
| `ROUSSEAU_2025` | 4 | ❌ **bloqueado por decisão registrada** |
| `YANG_2023_IJPEM` | 4 | ❌ 4 amplitudes distintas (0,25 · 0,30 · 0,35 · 0,50 mm) |
| `SUN_2025_CRIMP` | 2 | ❌ **verificado agora**: as 8 do rig são 8 condições distintas |

### `ROUSSEAU_2025` — a prova gravada já respondia

O piso desta fonte foi **invalidado de propósito** no erratum de 2026-08-04: o par
aço-`t10`↔`t12` são **espessuras diferentes**, pareadas como réplicas por uma chave mecânica
cega à geometria per-case. Três exceções FORTE foram retratadas e o bloqueio é permanente
(`_SEM_FAMILIA_MECANICA`). ⇒ não é lacuna, é decisão — e reabri-la exigiria desfazer uma
retratação que a campanha fez contra si mesma.

### `SUN_2025_CRIMP` — medido nesta sessão

As 8 curvas do rig:

```
axial_F17.5kN_{crimp,standard}     transverse_grease_{crimp,standard}
axial_F7.5kN_{crimp,standard}      transverse_nogrease_{crimp,standard}
```

Cada uma é uma combinação **única** de (tipo de carga, nível, lubrificação, fixador). **Não
há duas curvas na mesma condição** ⇒ nenhum piso de repetibilidade é derivável, por
construção do ensaio. O paper varreu o espaço de condições, não a dispersão.

## Conclusão

⇒ **A camada está correta e o bloqueio é de DADO, não de método.** Destravá-la exigiria uma
segunda corrida na mesma condição, em qualquer das três fontes — e as três são de
literatura. A bancada que poderia produzi-la (UFU) **saiu do projeto** por decisão do
professor em 2026-08-01.

**Consequência prática:** as 10 não são fila de trabalho. Continuam contadas como *fora* na
leitura estrita (147/205), que é o correto — indecidível ≠ acerto do modelo —, mas nenhuma
sessão deve gastar tempo procurando piso para elas até que apareça dado novo.

⚠️ **A `sun2025…grease_crimp` fica registrada como a candidata mais próxima:** duas pernas
dentro, σ 21 % fora, e um piso de fonte de apenas 0,0303 bastaria. Se o `SUN_2025` publicar
réplica — ou se o professor autorizar tratar `crimp`↔`standard` como par mecânico, o que eu
**não** recomendo (é justamente o erro que o erratum do ROUSSEAU corrigiu) — ela é a primeira
a reavaliar.

## Reprodutibilidade

Classificação pelos helpers canônicos do `regra_de_parada_triagem.py` (`classificar`,
`piso_da_fonte`, `rh.limite_sres`); listagem das condições por
`case_registry.all_records()`. Segundos, só-leitura.
