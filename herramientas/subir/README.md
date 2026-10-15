# Subir PDF/Excel a Dropbox desde la nube (Moisés, 14-oct-2026)

El conector de Dropbox solo sube texto y la nube no llega a Dropbox; antes se hacía con la iMac. Ahora lo hace un
robot de GitHub, CIFRADO (el repo es público):

- `python3 herramientas/subir/subir.py --repo <clon> --id <FS> "<archivo>=<ns>:<ruta>" ...` cifra los archivos con
  `subir_pub.pem`, los deja en `pedido/`, y el robot `.github/workflows/subir_dropbox.yml` los sube y contesta en
  `entrega/<FS>.json` (`ok`, `size` o `error`). Sale 0 si todo subió; `FALTA_TOKEN` si aún no está el token.
- Namespaces: `283552413` = carpeta de Moisés (rutas `/Dimaco/Mafesa/MO en proceso/...`);
  `15270085859` = `TRM Mafesa` (rutas `/Hoja de Procesos Mafesa Rev NN.xlsx`).
- Después de subir, la regla borra con el conector las versiones viejas que diga su regla.

## Puesta en marcha (una sola vez, la hace Moisés)
1. dropbox.com/developers/apps → Create app → Scoped access → Full Dropbox → nombre "DIMACO Regla".
   Pestaña Permissions: marcar `files.content.write` y `files.content.read` → Submit.
2. En Settings copiar App key y App secret.
3. Abrir `https://www.dropbox.com/oauth2/authorize?client_id=<APP_KEY>&token_access_type=offline&response_type=code`,
   Permitir y copiar el código.
4. GitHub → repo → Settings → Secrets and variables → Actions → New repository secret:
   `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`, `DROPBOX_CODE` (el código) y `SUBIR_PRIV` (la llave privada que te dio Claude).
5. Actions → "Dropbox · sacar token" → Run workflow (antes de que caduque el código). Deja `refresh.enc` cifrado.
   Después se puede borrar el secreto `DROPBOX_CODE`.
