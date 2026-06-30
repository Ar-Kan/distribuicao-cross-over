# Trabalho profissão distribuição

Projeto para estimar uma distribuição discreta de uso dos pesos de um equipamento
cross over a partir de sinais visuais de desgaste.

O equipamento observado tem 12 placas de 5 kg, totalizando pesos selecionáveis de
5 kg a 60 kg.

## Processamento das imagens

As imagens originais ficam preservadas em `imagens/`. O pré-processamento usa
OpenCV para gerar versões mais adequadas à inspeção visual e, futuramente, à
extração de métricas de desgaste.

Para rodar:

```powershell
uv run python processar_imagens.py
```

O script gera:

- `saidas/imagens_processadas/`: imagens melhoradas e versões analíticas em
  escala de cinza;
- `saidas/comparacoes/`: comparação lado a lado entre original e processada;
- `saidas/metricas_desgaste.csv`: estrutura inicial para registrar métricas por
  placa.

Pipeline atual:

1. leitura dos arquivos `.jpeg` em `imagens/`;
2. correção de contraste local com CLAHE no canal de luminosidade;
3. redução de ruído com filtro bilateral, preservando bordas;
4. realce moderado de nitidez com `unsharp mask`;
5. exportação de imagens coloridas processadas, imagens cinza analíticas e
   comparações antes/depois.

Nesta etapa ainda não há estimativa automática de desgaste por placa. Essa fase
será adicionada depois de validar visualmente se o pré-processamento preserva os
riscos, bordas, furos e áreas gastas dos pesos.
