# Cobertura de dados p/ blocos MSD por fonte (2026-07-03)

O que cada fonte fornece para montar o modelo MSD além das curvas. Legenda:
✓ = reportado no paper e capturado na nota; (db) = não reportado, preencher com os
bancos do app (`core/databases/threads.json`, `materials.json` — dims ISO 4014/4032,
d2/d3 via ISO 724); ✗ = genuinamente ausente (assunção necessária, anotada).

Condições de ensaio (F0, amplitude/carga, frequência, ciclos, μ, lubrificação) estão
**100% capturadas** nos `ValidationCase`s de todas as fontes — a tabela abaixo cobre só
o que falta além disso.

| Fonte | Parafuso (spec/material) | Grip / l_K | Membros (mat./espessura) | Furo/arruelas | Extra p/ MSD | Lacunas |
|---|---|---|---|---|---|---|
| **Liu 2025** (M16 transversal) | M16x120 8.8 ✓ | ✗ (fixture L, não reportado) | fixture aço alta rigidez, esp. ✗ | (db) | trem de carga c/ sensor EVT-14 ✓ | grip, freq (só amostragem 200 Hz), μ |
| **Bauer 2024** | M8 + M12x1.5 ✓ | **l_K = 8 / 12 mm ✓** | aço, esp. ✗ | (db) | s_crit = 99 µm ✓ (âncora slip_onset) | freq (simbólica), materiais exatos |
| **Liu 2017** (axial) | M12x1.75 10.9, d1/d2/P ✓ | ✗ | aço alta resist., esp. ✗ | (db) | revestimentos PTFE/MoS2/TiN ✓ | grip, μ numérico |
| **Lu 2024** | M8 8.8 GB/T 5783 ✓ | ✗ | placa aço-níquel, Ra 0.8/1.6/3.2 ✓, esp. ✗ | (db) | **coef. de torque K=0.23–0.27 ✓** (→μ derivável) | grip, espessura |
| **Rousseau 2025** | M12x1.75 8.8 ✓ | **25/29/33 mm ✓** | **aço E~200 / HDPE E~1 GPa, t=10/12/14 ✓** | **furo 13.6, arruelas 2.4 mm ✓** | rolamentos INA (sem atrito parasita) ✓ | amplitude exata (Table 2 do PDF) |
| **Icmez 2025** ('demir2024') | M8x1.25 DIN 933/934 ✓ | **13.8 / 19.8 mm ✓** | aço, esp. ✗ | (db) | rig J160 DIN 65151 ✓; curva F-ângulo (Fig 3, não digit.) | freq (nominal 12.5), materiais |
| **Yang 2021** (composto) | M8x1.25x70 8.8 ✓ | ✗ | fixture cunha, esp. ✗ | (db) | ξ crítico = 0.075 mm/kN ✓; fase 90° ✓ | grip, μ |
| **Yang 2019** | M10 alta resist. ✓ | ✗ | 2 placas aço, esp. ✗ | (db) | protocolo amplitude variável ✓ | grip, grade exata, μ |
| **Karlsen 2022** | M30/M42 10.9 ✓ | ✗ | pacote grande, esp. ✗ | (db) | HV vs Vibralock ✓; tensioned vs torqued ✓ | grip, geometria do pacote |
| **Sandia 2021** | **⚠ diâmetro NÃO reportado** (SAE gr9, est. 1/4") | ✗ | C-beams 4340 ✓ | ✗ | parafuso instrumentado STRAINSERT ✓ | tamanho do parafuso, amplitude local |
| **Liu 2022** (reaperto) | M12x1.75 8.8, **35CrMn E=213 GPa ν=0.286 ✓** | ✗ (placas "mesma espessura", valor no PDF Fig 2) | **aço 45, E=209 GPa ν=0.269 ✓** | célula 20 mm no pacote ✓ | T=80 N·m ✓; μ≈0.2 ✓; protocolos de reaperto ✓ | espessura exata das placas |
| **Li 2022 Marine Struct** (creep) | **M16x80 304SS E=193 GPa ✓** | **L=20 mm ✓** | contato 60×60 mm ✓, D=60 ✓, E_P=206 ✓ | (db) | **Burgers K_B/K_P/K1/K2/C1/C2 ✓✓** (mola-amortecedor direto p/ camada de contato) | — (mais completo) |
| **Li 2022 Tribology** (axial×freq) | M10, A_s=58 mm² ✓ | ✗ | fixture Shimadzu, esp. ✗ | (db) | 3–5 repetições/grupo ✓ | grip, material, μ |
| **Yang 2023** (substituto) | M6x1.0x65 + M8x1.25x65 10.9 ✓ | ~25 mm (est.) ✓ | aço, esp. ✗ | **config MSD completa na nota** (d2, d3, cabeça, porca, furo) ✓ | nota tem tabela "MSD BUILDER CONFIGURATION" pronta ✓ | curvas aproximadas (tabela, não figura) |

## Como preencher as lacunas (regra prática)

1. **Geometria de rosca/cabeça/porca ausente** → `core/databases/threads.json` (ISO):
   nunca inventar; d2/d3 via ISO 724 (usar pitch_diameter, não minor — gotcha do CLAUDE.md).
2. **Grip length ausente** → estimar 2–3×d e marcar como estimativa no modelo (afeta k_bolt;
   sensibilidade baixa nos ajustes disp-mode, alta no axial force-mode — para o trilho axial
   do Liu 2017, vale extrair o grip do PDF antes de ajustar).
3. **μ ausente** → 0.15 seco (default V2) / 0.18 unlubricated Yang 2023 / derivar do coef.
   de torque quando reportado (Lu 2024, Liu 2022: K→μ via Motosh).
4. **Espessura de membros ausente** → single_shear preset do wizard já sintetiza; só o
   Rousseau exige as espessuras reais (é a variável do estudo — e estão capturadas).
5. **Sandia**: não usar como alvo primário de fitting (diâmetro desconhecido) — só validação
   de forma/slip-onset, como anotado.
