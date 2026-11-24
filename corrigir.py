import glob

# Procura todos os arquivos .txt do seu projeto
for arquivo in glob.glob('*.txt'):
  with open(arquivo, 'r', encoding='utf-8') as f:
    texto = f.read()

  # Transforma vários espaços em um só
  texto_limpo = ' '.join(texto.split())

  with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(texto_limpo)
