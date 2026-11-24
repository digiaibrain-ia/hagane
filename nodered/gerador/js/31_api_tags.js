// [F] GET /baggio/api/tags -> contrato de tags (so os itens monitorados). SOMENTE LEITURA.
msg.payload = global.get("baggio_contrato");
msg.headers = { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", "Access-Control-Allow-Origin": "*" };
msg.statusCode = 200;
return msg;
