function organizarArquivosPorPessoa(e) {
  var sheet = e.range.getSheet();
  var row = e.range.getRow();
  
  // Evita rodar na linha de cabeçalho (A PRIMEIRA LINHA)
  if (row < 2) return; 

  // Pega os dados da linha que acabou de ser preenchida e os cabeçalhos
  var values = sheet.getRange(row, 1, 1, sheet.getLastColumn()).getValues()[0];
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];

  // ======== CONFIG ========
 
  var idPastaContrato = "COLE_O_ID_DA_PASTA_DO_CONTRATO_AQUI"; // Cole aqui o ID da pasta que você quer usar para armazenar as pastas dos usuários

  var colunaNome = "Nome"; // Nome exato da coluna do nome na sua planilha

  // Descobre em qual coluna está o "Nome"
  var indexNome = headers.indexOf(colunaNome);
  // Se não achar a coluna Nome, para o script
  if (indexNome === -1) return; 
  
  var nomeCandidato = values[indexNome];
  if (!nomeCandidato) return; // Se o nome estiver vazio, para


  nomeCandidato = String(nomeCandidato).trim();

  // ======== CRIAÇÃO DA PASTA DO USUÁRIO ========

  var pastaContrato = DriveApp.getFolderById(idPastaContrato);
  var pastaCandidato = pastaContrato.createFolder(nomeCandidato);

  // ======== LISTA DE COLUNAS COM ARQUIVOS ENVIADOS PELO USUÁRIO ========

  var colunasDeArquivos = [
    "FOTO CPF", 
    "COMPROVANTE DE RESIDENCIA", 
    "Diploma de graduação em medicina", 
    "Carteira do órgão"
  ];

  // Percorre cada coluna de arquivo configurada acima
  for (var c = 0; c < colunasDeArquivos.length; c++) {
    var nomeColuna = colunasDeArquivos[c];
    var indexColuna = headers.indexOf(nomeColuna);
    
    if (indexColuna !== -1) {
      var urlArquivo = String(values[indexColuna]);
      
      // Vê se tem um link do Drive na célula
      if (urlArquivo.indexOf("drive.google.com") !== -1 || urlArquivo.indexOf("open?id=") !== -1) {
        try {
          var fileId = extrairIdDoArquivo(urlArquivo);
          if (fileId) {
            var arquivo = DriveApp.getFileById(fileId);
            
            // Move o arquivo da pasta padrão bagunçada do automatica do Forms para a pasta do usuário
            arquivo.moveTo(pastaCandidato);
          }
        } catch (err) {
          Logger.log("Erro ao mover o arquivo da coluna " + nomeColuna + ": " + err.toString());
        }
      }
    }
  }
}

// Extrai o ID do arquivo pela URL do Forms
function extrairIdDoArquivo(url) {
  var match = url.match(/[-\w]{25,}/);
  return match ? match[0] : null;
}