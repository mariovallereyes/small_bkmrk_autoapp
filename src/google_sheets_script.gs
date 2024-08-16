function getUnreadEmails() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var threads = GmailApp.search('subject:YOUR_SUBJECT_KEYWORD is:unread after:YYYY/MM/DD');
  var label = GmailApp.getUserLabelByName("Processed");
  
  // Obtener la carpeta de Google Drive "YOUR_FOLDER_NAME"
  var folder = DriveApp.getFoldersByName("YOUR_FOLDER_NAME").next();

  // Si la etiqueta "Processed" no existe, crearla
  if (!label) {
    label = GmailApp.createLabel("Processed");
  }

  if (threads.length === 0) {
    Logger.log("No hay correos nuevos con el subject especificado.");
    return;
  }

  for (var i = 0; i < threads.length; i++) {
    var messages = threads[i].getMessages();
    for (var j = 0; j < messages.length; j++) {
      var message = messages[j];
      var body = message.getPlainBody().trim();
      var lines = body.split('\n');
      var tweetUrl = lines[0];
      var description = lines[2]; // Asumiendo que la segunda línea está vacía y la tercera tiene la descripción
      var sender = message.getFrom();
      var subject = message.getSubject();
      var date = message.getDate();
      
      // Procesar el adjunto
      var attachments = message.getAttachments();
      var attachmentUrl = "";
      if (attachments.length > 0) {
        var img = attachments[0];
        var file = folder.createFile(img);  // Subir el archivo a la carpeta
        attachmentUrl = "https://drive.google.com/open?id=" + file.getId();  // Generar el enlace al archivo
      }
      
      sheet.appendRow([date, sender, subject, tweetUrl, description, attachmentUrl]);
      
      // Marcar el mensaje como leído y aplicar la etiqueta de "Processed"
      message.markRead();
      label.addToThread(threads[i]);
    }
  }
}
