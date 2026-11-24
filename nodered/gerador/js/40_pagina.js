// [F] GET /hagane -> entrega a pagina HTML (conteudo no no "template" ao lado).
msg.headers = { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" };
msg.statusCode = 200;
return msg;
