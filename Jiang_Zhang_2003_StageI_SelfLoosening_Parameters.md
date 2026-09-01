# Parâmetros para Reprodução Numérica — Jiang, Zhang & Lee (2003)

**Referência completa:** Jiang, Y.; Zhang, M.; Lee, C.-H. "A Study of Early Stage Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 125, pp. 518–526, September 2003. DOI: 10.1115/1.1586936

**Software utilizado:** ABAQUS (solver com UMAT customizada) + Hypermesh (pré-processamento da malha)

**Objetivo:** Investigação experimental e numérica (FE elasto-plástica 3D) dos mecanismos do afrouxamento de Estágio I (perda de pré-carga sem rotação da porca) em juntas aparafusadas sob carga transversal cíclica.

---

## 1. Geometria do Parafuso

| Parâmetro | Valor |
|-----------|-------|
| Designação | **½ polegada (12.7 mm), tpi = 13** (UNC ½-13) |
| Diâmetro nominal | 12.7 mm (½ in) |
| Passo (pitch) | 1/13 in ≈ 1.954 mm |
| Comprimento total do parafuso | **57 mm** |
| Comprimento da parte rosqueada | **25 mm** |
| Material do parafuso | **Aço AISI 1070** |
| Fabricação | Usinado de barras redondas laminadas a quente; roscas **retificadas** (ground) |
| Tratamento térmico | **880°C por 4 horas**, seguido de resfriamento ao ar |

> **Nota importante:** Os parafusos foram **usinados e retificados**, não laminados. Isso significa que as tensões residuais são insignificantes, o que simplifica a modelagem. Parafusos comerciais (laminados a frio) teriam tensões residuais significativas que alterariam os valores quantitativos, mas não as conclusões gerais.

---

## 2. Geometria da Porca

| Parâmetro | Valor |
|-----------|-------|
| Tipo | Porca hexagonal **Grade 8** |
| Origem | Comercial (comprada) |
| Dureza | **HRC 26–34** |

---

## 3. Geometria do Conjunto (Junta)

### Componentes

| Componente | Material | Dimensão relevante |
|------------|----------|--------------------|
| Placas de aperto (2×) | **Aço AISI 4340** (alta resistência) | Espessura: **13 mm** cada |
| Célula de carga (load cell) | Aço | Espessura: **15 mm**; tipo washer, capacidade 15,000 lb (para parafuso ½ in) |
| Parafuso | AISI 1070 | Comprimento total: 57 mm |
| Porca | Grade 8 | — |

### Comprimentos efetivos

| Parâmetro | Valor |
|-----------|-------|
| Comprimento de aperto efetivo do parafuso | **41 mm** (2 × 13 mm placas + 15 mm célula de carga) |
| Comprimento do extensômetro (gage length) | **50.8 mm** |

### Condições de contorno

- **Placa inferior:** uma extremidade fixa (engaste)
- **Placa superior:** carga cisalhante ou deslocamento aplicado na extremidade oposta
- **Extensômetro:** uma perna em cada placa, medindo deslocamento relativo entre as duas placas dentro do *gage length* de 50.8 mm
- **Mola auxiliar:** rigidez de **100 N/mm**, acoplada à placa superior (para evitar singularidade numérica durante o escorregamento)

---

## 4. Propriedades dos Materiais

### 4.1 Aço AISI 1070 (material do parafuso) — Propriedades elásticas

| Parâmetro | Valor |
|-----------|-------|
| Módulo de elasticidade, *E* | **206.8 GPa** |
| Coeficiente de Poisson, *ν* | **0.3** |
| Tensão de escoamento monotônica (0.2% offset) | **449 MPa** |
| Tensão de escoamento cíclica (em cisalhamento), *k* | **130.0 MPa** |

> **Nota crítica:** A tensão de escoamento cíclica (*k* = 130 MPa) é **muito menor** que a tensão de escoamento monotônica (449 MPa). Isso é típico de materiais metálicos sob carregamento cíclico. O valor baixo permite a descrição detalhada do comportamento de plasticidade cíclica, incluindo *ratcheting* e relaxação de tensão. Corresponde à porção linear da curva tensão-deformação cíclica.

### 4.2 Aço AISI 1070 — Constantes do Modelo de Plasticidade Cíclica (Jiang-Sehitoglu)

O modelo utiliza **M = 5 partes de backstress** (backstress decomposition). As constantes foram obtidas experimentalmente por ensaios de deformação controlada em corpos de prova lisos cilíndricos, com tratamento térmico idêntico ao dos parafusos.

**Table 2 do artigo — Material Constants of 1070 Steel:**

| Constante | Valor |
|-----------|-------|
| *E* | 206.8 GPa |
| *ν* | 0.3 |
| *k* (yield stress in shear) | 130.0 MPa |

**Constantes de taxa de endurecimento (*c*⁽ⁱ⁾):**

| i | c⁽ⁱ⁾ |
|---|-------|
| 1 | 1633.0 |
| 2 | 493.4 |
| 3 | 149.1 |
| 4 | 45.0 |
| 5 | 13.6 |

**Constantes de saturação do backstress (*r*⁽ⁱ⁾) [MPa]:**

| i | r⁽ⁱ⁾ (MPa) |
|---|------------|
| 1 | 85.4 |
| 2 | 76.6 |
| 3 | 88.3 |
| 4 | 96.7 |
| 5 | 141.1 |

**Expoentes de ratcheting (*χ*⁽ⁱ⁾):**

| i | χ⁽ⁱ⁾ |
|---|-------|
| 1 | 5.0 |
| 2 | 5.0 |
| 3 | 5.0 |
| 4 | 5.0 |
| 5 | 5.0 |

> Todos os expoentes χ são iguais a 5.0.

### 4.3 Aço AISI 4340 (placas de aperto)

| Parâmetro | Valor |
|-----------|-------|
| Classificação | Aço de alta resistência |
| Comportamento | **Elástico** (somente o parafuso sofre plasticidade significativa) |

> As propriedades elasto-plásticas das placas e demais componentes **não foram necessárias** — apenas o parafuso experimenta deformação plástica cíclica significativa.

---

## 5. Modelo de Plasticidade Cíclica — Jiang-Sehitoglu

Este modelo foi implementado no ABAQUS via **sub-rotina UMAT** (user-defined material). É essencial para capturar o *ratcheting* de deformação e a relaxação de tensão que causam o afrouxamento de Estágio I.

### Equações constitutivas (Table 1 do artigo)

**Função de escoamento (von Mises):**
```
f = (S̃ - α̃):(S̃ - α̃) - 2k² = 0
```
onde S̃ = tensor desviador de tensão, α̃ = backstress, k = tensão de escoamento em cisalhamento.

**Lei de fluxo (associada):**
```
dε̃ᵖ = (1/h) × ⟨dS̃:ñ⟩ × ñ
```
onde ñ = normal à superfície de escoamento, h = módulo plástico.

**Regra de endurecimento cinemático (decomposição em M partes):**
```
α̃ = Σᵢ₌₁ᴹ α̃⁽ⁱ⁾

dα̃⁽ⁱ⁾ = c⁽ⁱ⁾ × r⁽ⁱ⁾ × [ ñ - (‖α̃⁽ⁱ⁾‖ / r⁽ⁱ⁾)^(χ⁽ⁱ⁾+1) × (α̃⁽ⁱ⁾ / ‖α̃⁽ⁱ⁾‖) ] × dp

(i = 1, 2, ..., M)
```
onde dp = incremento de deformação plástica equivalente.

### Implementação numérica

| Aspecto | Detalhe |
|---------|---------|
| Algoritmo de atualização de tensão | **Backward Euler** (explícito) |
| Método de solução da equação não-linear | **Newton** |
| Operador tangente | **Consistente** (consistent tangent operator) |
| Convergência global | **Newton-Raphson** com convergência quadrática garantida |
| Referência da implementação | Jiang, Xu & Sehitoglu (2002), *ASME J. Tribol.*, 124:699–708 |
| Referência do modelo de plasticidade | Jiang & Sehitoglu (1996), *ASME J. Appl. Mech.*, 63:720–733 |

---

## 6. Modelo de Atrito — Coulomb com Transição Exponencial

O escorregamento entre as duas placas de aperto segue o modelo de Coulomb com transição suave stick-to-slip:

```
μ = μ_k + (μ_s - μ_k) × exp(-d_c × γ̇)
```

| Parâmetro | Símbolo | Valor |
|-----------|---------|-------|
| Coeficiente de atrito estático | μ_s | **0.6** |
| Coeficiente de atrito cinético | μ_k | **0.2** |
| Coeficiente de decaimento | d_c | **10** |
| Taxa de escorregamento | γ̇ | Variável |

> **Nota:** O coeficiente de decaimento *d_c* tem influência **insignificante** nos resultados da simulação FE. Os valores de μ_s e μ_k foram obtidos por tentativa e erro, comparando curvas FE de carga transversal vs. deslocamento com dados experimentais (Fig. 11 do artigo).

### Interfaces de contato no modelo FE

O modelo possui **10 pares de contato**:

| Nº | Interface | Formulação |
|----|-----------|------------|
| 1–6 | Roscas engajadas do parafuso e da porca (6 filetes) | Contato com restrição de slip (altas tensões cisalhantes críticas para simular sticking) |
| 7 | Porca ↔ superfície de apoio | Penalty function |
| 8 | Duas placas de aperto (entre si) | Coulomb com transição exponencial (Eq. 1) |
| 9 | Placa inferior ↔ célula de carga | Penalty function |
| 10 | Cabeça do parafuso ↔ superfície de apoio | Penalty function |

> **Definição master/slave:** Superfície de contato do parafuso (malha fina) = **slave**; superfície da porca (malha mais grossa) = **master**.

---

## 7. Malha de Elementos Finitos

### Geometria simplificada

As roscas do parafuso e da porca foram simplificadas em **ranhuras circunferenciais** (circumferential grooves) — NÃO em geometria helicoidal. Isso é justificável para o Estágio I porque não há rotação da porca.

### Simetria

Apenas **metade** da estrutura foi modelada (simetria em relação ao plano x-y). Condição: deslocamentos em z = 0 fixos na direção z para todos os nós no plano x-y.

### Parâmetros da malha

| Parâmetro | Valor |
|-----------|-------|
| Total de nós | **10,836** |
| Total de elementos | **8,395** |
| Tipo de elemento | **Brick sólido de 8 nós** (C3D8 ou equivalente) |
| Nós na raiz da 1ª rosca engajada | **8 nós** (malha mais fina) |
| Nós na raiz da 2ª rosca engajada | **4 nós** |
| Nós nas demais raízes de rosca | **1 nó** |
| Número de roscas engajadas | **6** |

> **Refinamento estratégico:** A 1ª rosca engajada carrega **mais de 30%** da carga total (conforme Wang, Xu & Jiang, 1999). Portanto, a malha mais fina é concentrada nessa região.

### Estudo de sensibilidade de malha

| Modelo | Descrição | Resultado |
|--------|-----------|-----------|
| Modelo grosso | ~50% dos elementos do modelo atual | Resultados próximos ao experimental |
| Modelo fino (atual) | 8,395 elementos | Redução de clamping force ligeiramente maior |
| Diferença (elástico) | — | Tensões von Mises até **7% menores** no modelo grosso |
| Diferença (elastoplástico) | — | Tensões **menos de 3% menores** no modelo grosso |

> **Conclusão:** Quando ocorre deformação plástica, os gradientes de tensão/deformação diminuem perto da descontinuidade geométrica, tornando os resultados **menos sensíveis** à finura da malha.

---

## 8. Aplicação da Pré-carga — Método de Expansão Térmica Ortotrópica

A pré-carga foi simulada aplicando temperatura à **placa superior** (diferente do artigo de 2007, que aplica na célula de carga):

| Parâmetro | Valor |
|-----------|-------|
| Componente aquecido | **Placa superior** (upper plate) |
| Tipo de expansão | Ortotrópica — expansão **somente na direção axial** |
| Direções transversais | Coeficiente de expansão = 0 |
| Controle da pré-carga | Ajuste do coeficiente de expansão e/ou da temperatura |

---

## 9. Protocolo de Carregamento Transversal

### Dois tipos de experimentos e suas simulações FE

#### Tipo 1: Controlado por carga (load-controlled)

| Parâmetro | Valor |
|-----------|-------|
| Tipo de controle | Carga transversal totalmente reversa |
| Forma de onda | **Senoidal** |
| Lubrificante entre placas | **Nenhum** (contato seco) |
| Escorregamento entre placas | **Não houve** (o atrito estático seco permitiu grandes cargas sem deslizamento) |

#### Tipo 2: Controlado por deslocamento (displacement-controlled)

| Parâmetro | Valor |
|-----------|-------|
| Tipo de controle | Deslocamento relativo entre as placas (via extensômetro, *gage length* = 50.8 mm) |
| Forma de onda | **Senoidal** |
| Lubrificante entre placas | **Graxa** (para reduzir atrito e minimizar desgaste) |
| Trava de rosca (thread locker) | **Threadlocker 262** (Loctite — para aplicações de alta vibração/impacto; remoção requer ferramenta especial) |
| Objetivo da trava | **Garantir que nenhuma rotação da porca ocorra** (isolar Estágio I) |

### Frequência de teste

| Parâmetro | Valor |
|-----------|-------|
| Frequência | **0.25 – 0.5 Hz** |

### Protocolo FE — 4 steps por ciclo

1. Carga/deslocamento positivo (+x) até o máximo
2. Retorno ao zero
3. Carga/deslocamento negativo (−x) até o máximo
4. Retorno ao zero

| Parâmetro | Valor |
|-----------|-------|
| Incrementos por step | **15 a 20** |
| Ciclos simulados por caso | Até **32 ciclos** |
| Tempo computacional | **≈ 200 CPU horas** por simulação (Origin 2000, NCSA, ~2002) |

---

## 10. Casos de Carga Experimentais — 9 Combinações

Os resultados experimentais são apresentados na Fig. 3 do artigo. Os dados abaixo foram extraídos diretamente do texto e figuras.

### Fig. 3(a) — Grupo 1: Amplitudes maiores

| Caso | P₀ (kN) | Tipo de controle | ΔQ/2 (kN) | Δδ/2 (mm) | Lubrificante | Perda de P após 200 ciclos |
|------|---------|-----------------|-----------|-----------|-------------|---------------------------|
| 1 | 49.7 | Carga | 13.5 | — (sem slip) | Sem (seco) | Mínima (~poucos %) |
| 2 | 36.1 | Deslocamento | — | 0.61 | Com graxa | ~40–41% |
| 3 | 36.5 | Deslocamento | — | 0.46 | Com graxa | ~25–30% |
| 4 | 27.0 | Deslocamento | — | 0.48 | Com graxa | ~35–40% |
| 5 | 28.9 | Deslocamento | — | 0.62 | Com graxa | ~40% |

### Fig. 3(b) — Grupo 2: Pré-cargas maiores

| Caso | P₀ (kN) | Tipo de controle | ΔQ/2 (kN) | Δδ/2 (mm) | Lubrificante | Observação |
|------|---------|-----------------|-----------|-----------|-------------|------------|
| 6 | 41.0 | Deslocamento | — | 0.46 | Sem (seco) | Afrouxamento similar ao caso lubrificado |
| 7 | 41.0 | Deslocamento | — | 0.46 | Com graxa | Afrouxamento similar ao caso seco |
| 8 | 31.3 | Deslocamento | — | 0.62 | Com graxa | Grande perda de pré-carga |
| 9 | 31.0 | Deslocamento | — | 0.46 | Com graxa | Perda moderada |

### Faixa de pré-carga recomendada

Segundo Bickford e Eccles, a pré-carga adequada corresponde a **50–75% da tensão de escoamento nominal** do parafuso:

| Parâmetro | Valor |
|-----------|-------|
| Faixa de pré-carga para parafuso ½ in (1070 steel) | **25–40 kN** |

---

## 11. Resultados Quantitativos de Referência (para validação)

### Perda de clamping force — faixa geral

| Condição | Perda de P/P₀ após 200 ciclos |
|----------|-------------------------------|
| Carga controlada (sem slip entre placas) | **Poucos %** (mínima após primeiros ciclos) |
| Deslocamento controlado (com slip) | **10% a >41%** |
| 1º ciclo | **Maior redução** de todo o histórico |
| Tendência após 1º ciclo | Taxa de afrouxamento **decresce** com o número de ciclos |

### Tensões axiais no parafuso (P₀ = 41.7 kN, Δδ/2 = 0.46 mm)

| Condição | Tensão axial máxima | Localização |
|----------|--------------------|-|
| Após aplicação da pré-carga | **950 MPa** | Raiz da 1ª rosca engajada |
| Carga transversal no máximo (+x) | **1090 MPa** | Raiz da 1ª rosca engajada |
| Tensão de von Mises no pico | **>> σ_y (449 MPa)** | Raiz da 1ª rosca engajada |

> O parafuso fica sujeito a **flexão combinada + tração** quando a carga transversal é aplicada.

### Pressão de contato máxima

| Local | Valor |
|-------|-------|
| Superfície de contato da 1ª rosca engajada | **550 MPa** |
| Efeito na indentação | Insignificante durante a pré-carga e carregamento cíclico |

### Comportamento do material na raiz da 1ª rosca

O ponto material na raiz da 1ª rosca engajada exibe:

- **Relaxação de tensão:** tensão axial diminui progressivamente com os ciclos
- **Ratcheting de deformação:** deformação axial aumenta progressivamente com os ciclos
- **Loops de histerese:** Fig. 7 do artigo mostra os loops tensão-deformação do ciclo 1, 8 e 32

### Influência do atrito entre placas (validação FE)

| μ_k entre placas | Resultado (P₀ = 36 kN, Δδ/2 = 0.3 mm) |
|------------------|---------------------------------------|
| 0.3 | Praticamente idêntico |
| 0.5 | Praticamente idêntico |
| 0.8 | Praticamente idêntico |

> **Conclusão confirmada:** Quando o deslocamento é controlado, o coeficiente de atrito entre as placas **NÃO influencia** significativamente o afrouxamento de Estágio I.

---

## 12. Mecanismo Identificado — Estágio I

O afrouxamento de Estágio I é causado por:

1. **Plasticidade cíclica localizada** nas raízes dos filetes engajados, especialmente na 1ª rosca
2. **Ratcheting de deformação** — deformação plástica acumula progressivamente em uma direção
3. **Relaxação de tensão** — tensão axial na raiz da rosca diminui com os ciclos
4. **Redistribuição de tensões** — as tensões se redistribuem ao longo da seção transversal do parafuso, resultando em perda gradual da força de aperto

### Diferenças entre Estágio I e Estágio II

| Aspecto | Estágio I (este artigo) | Estágio II (Zhang & Jiang, 2007) |
|---------|------------------------|----------------------------------|
| Rotação da porca | **Nenhuma** | Progressiva |
| Mecanismo dominante | Plasticidade cíclica (ratcheting) | Microslip + momento fletor reverso |
| Duração típica | Primeiros ~200 ciclos | Centenas a milhares de ciclos |
| Perda de pré-carga | 10–40% | Até total |
| Modelo de material necessário | **Elasto-plástico cíclico** (Jiang-Sehitoglu) | Elástico linear |
| Geometria da rosca no FE | Ranhuras circunferenciais (OK) | **Hélice verdadeira** (necessária) |
| Comportamento do material | Aço 1070 (σ_y = 449 MPa) | Classe 10.9 (σ_y = 1040 MPa) |

---

## 13. Observações sobre Embedment

| Parâmetro | Valor |
|-----------|-------|
| Redução de clamping force por embedment | **≤ 2%** da pré-carga |
| Tempo de ocorrência | Poucos segundos após o aperto |
| Evolução posterior | Nenhuma redução adicional observada em horas |
| Contribuição para o afrouxamento cíclico | **Insignificante** |
| Pressão de contato máxima | 550 MPa (na 1ª rosca) — causa indentação desprezível |

---

## 14. Relação Clamping Force vs. Rotação da Porca

Dado experimental de referência (do artigo Jiang et al., 2001):

| Parâmetro | Valor |
|-----------|-------|
| Relação P vs. θ | **Aproximadamente linear** (tanto para aperto quanto para afrouxamento) |
| Redução de 1 kN na pré-carga | ≈ **2° de rotação** relativa entre porca e parafuso |
| Para perda de 5–17.5 kN (faixa do Estágio I) | Corresponderia a **10°–35°** de rotação (se fosse por back-off) |

> Este argumento demonstra que a perda de clamping force observada **não pode ser atribuída a rotação da porca** — seria visível a olho nu. Comprovado adicionalmente pelo uso de Threadlocker 262.

---

## 15. Nomenclatura Completa

| Símbolo | Descrição | Unidade |
|---------|-----------|---------|
| *d_c* | Coeficiente de decaimento (modelo de atrito) | — |
| *k* | Tensão de escoamento em cisalhamento | MPa |
| *P* | Força de aperto (clamping force) | kN |
| *P₀* | Pré-carga inicial (preload) | kN |
| *Q* | Carga transversal (cisalhante) | kN |
| *ΔQ/2* | Amplitude da carga transversal | kN |
| *Δδ/2* | Amplitude do deslocamento transversal relativo | mm |
| *ν* | Coeficiente de Poisson | — |
| *μ* | Coeficiente de atrito | — |
| *μ_s* | Coeficiente de atrito estático | — |
| *μ_k* | Coeficiente de atrito cinético | — |
| *γ̇* | Taxa de escorregamento (slip rate) | mm/s |
| *θ* | Ângulo de rotação da porca | ° (graus) |
| *c⁽ⁱ⁾* | Constante de taxa de endurecimento (backstress part i) | — |
| *r⁽ⁱ⁾* | Constante de saturação do backstress (part i) | MPa |
| *χ⁽ⁱ⁾* | Expoente de ratcheting (part i) | — |
| *M* | Número de partes do backstress | — |
| *dp* | Incremento de deformação plástica equivalente | — |
| *S̃* | Tensor desviador de tensão | MPa |
| *α̃* | Backstress total | MPa |
| *ñ* | Normal à superfície de escoamento | — |
| *h* | Módulo plástico | MPa |

---

## 16. Referências Essenciais para Reprodução

| Ref. | Conteúdo | Citação |
|------|----------|---------|
| [1] | Referência geral sobre juntas aparafusadas | Bickford, J.H. (1995), *An Introduction to the Design and Behavior of Bolted Joints*, 3rd Ed., Marcel Dekker |
| [20] | Software de pré-processamento | Hypermesh, Altair Engineering Inc. |
| [22] | Solver FE | ABAQUS (1999), User's Manual and Theory Manual, HKS |
| [24] | Modelo de plasticidade — Parte I (desenvolvimento) | Jiang, Y. & Sehitoglu, H. (1996), *ASME J. Appl. Mech.*, 63:720–725 |
| [25] | Modelo de plasticidade — Parte II (implementação e validação) | Jiang, Y. & Sehitoglu, H. (1996), *ASME J. Appl. Mech.*, 63:726–733 |
| [26] | Implementação FE da UMAT | Jiang, Y.; Xu, B.; Sehitoglu, H. (2002), *ASME J. Tribol.*, 124:699–708 |
| [31] | Relação torque-tensão experimental | Jiang, Y.; Chang, J.; Lee, C. (2001), *Int. J. Mat. Product Tech.*, 16:417–429 |

---

## 17. Checklist para Reprodução Numérica

- [ ] Criar geometria do parafuso UNC ½-13 com roscas simplificadas (ranhuras circunferenciais)
- [ ] Modelar apenas metade da estrutura (simetria em x-y)
- [ ] Criar 6 filetes engajados com refinamento progressivo (8 nós na raiz da 1ª rosca)
- [ ] Implementar modelo de plasticidade cíclica Jiang-Sehitoglu via UMAT com as 15 constantes da Tabela 2
- [ ] Configurar 10 pares de contato (6 roscas + 4 interfaces)
- [ ] Aplicar restrição de slip nas roscas (altas tensões cisalhantes críticas)
- [ ] Usar modelo de atrito exponencial (μ_s = 0.6, μ_k = 0.2, d_c = 10) entre as placas
- [ ] Aplicar pré-carga via expansão térmica ortotrópica na placa superior
- [ ] Simular carregamento cíclico em 4 steps/ciclo, com 15–20 incrementos/step
- [ ] Monitorar: força de aperto (integração de σ_axial na seção), loops de histerese na raiz da 1ª rosca, redistribuição de tensões ao longo dos ciclos
- [ ] Validar contra Fig. 9 do artigo (P/P₀ vs. número de ciclos)
