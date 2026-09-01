# THETA_CSV manifest — rotacao da porca θ(N)

Primeiras curvas θ(N) do database (lacuna n.1, sec4.22). Extracao vetorial pymupdf (New_Theory/digitize_pdf_curves.py, agente 2026-07-08) do rousseau2025_materials_M12.pdf p7 (Fig 4 HDPE / Fig 5 aco). Anti-alucinacao: preload da MESMA cor calibrado contra digitized_csv (HDPE gate 1.4% PASS; aco 5.5% com OVERRIDE documentado — a referencia manual de 14-16 pts retifica o S; endpoint 1e-4; overlays em theta_csv/verification/). Fisica consistente: θ_fim t10>t12>t14 nos dois materiais. quality: measured (vetorial).

## rousseau2025_theta_hdpe_t10.csv
- pontos: 160
- colunas: `cycle,theta_deg`
- fonte/calibracao: fonte: rousseau2025_materials_M12.pdf pagina 7 figura 4, extracao vetorial pymupdf, calibracao vs preload do mesmo grafico: gate PASSA: vs rousseau2025_hdpe_t12.csv desvio 1.4% do span; overlay de verificacao em verification/rousseau2025_fig4_overlay.png

## rousseau2025_theta_hdpe_t12.csv
- pontos: 160
- colunas: `cycle,theta_deg`
- fonte/calibracao: fonte: rousseau2025_materials_M12.pdf pagina 7 figura 4, extracao vetorial pymupdf, calibracao vs preload do mesmo grafico: gate PASSA: vs rousseau2025_hdpe_t12.csv desvio 1.4% do span; overlay de verificacao em verification/rousseau2025_fig4_overlay.png

## rousseau2025_theta_hdpe_t14.csv
- pontos: 160
- colunas: `cycle,theta_deg`
- fonte/calibracao: fonte: rousseau2025_materials_M12.pdf pagina 7 figura 4, extracao vetorial pymupdf, calibracao vs preload do mesmo grafico: gate PASSA: vs rousseau2025_hdpe_t12.csv desvio 1.4% do span; overlay de verificacao em verification/rousseau2025_fig4_overlay.png

## rousseau2025_theta_steel_t10.csv
- pontos: 160
- colunas: `cycle,theta_deg`
- fonte/calibracao: fonte: rousseau2025_materials_M12.pdf pagina 7 figura 5, extracao vetorial pymupdf, calibracao vs preload do mesmo grafico: gate 3%-do-span REPROVADO (melhor: vs rousseau2025_steel_t12.csv 5.5% do span = 0.0205 abs); OVERRIDE documentado: refs steel_t10/t12 sao digitalizacoes manuais de 14-16 pts que retilinizam o colapso em S (t10 tem incrementos constantes 0.078/10 ciclos e desvia ate 0.175 no m

## rousseau2025_theta_steel_t12.csv
- pontos: 160
- colunas: `cycle,theta_deg`
- fonte/calibracao: fonte: rousseau2025_materials_M12.pdf pagina 7 figura 5, extracao vetorial pymupdf, calibracao vs preload do mesmo grafico: gate 3%-do-span REPROVADO (melhor: vs rousseau2025_steel_t12.csv 5.5% do span = 0.0205 abs); OVERRIDE documentado: refs steel_t10/t12 sao digitalizacoes manuais de 14-16 pts que retilinizam o colapso em S (t10 tem incrementos constantes 0.078/10 ciclos e desvia ate 0.175 no m

## rousseau2025_theta_steel_t14.csv
- pontos: 160
- colunas: `cycle,theta_deg`
- fonte/calibracao: fonte: rousseau2025_materials_M12.pdf pagina 7 figura 5, extracao vetorial pymupdf, calibracao vs preload do mesmo grafico: gate 3%-do-span REPROVADO (melhor: vs rousseau2025_steel_t12.csv 5.5% do span = 0.0205 abs); OVERRIDE documentado: refs steel_t10/t12 sao digitalizacoes manuais de 14-16 pts que retilinizam o colapso em S (t10 tem incrementos constantes 0.078/10 ciclos e desvia ate 0.175 no m

