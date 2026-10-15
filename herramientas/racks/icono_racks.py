"""Ícono del Tablero TV RACKS (racks/icon.png) — 14-oct-2026 (Moisés): el ícono del Dock decía otra cosa; el de Racks
usa el estilo de las estaciones RACKS (fondo azul, RACKS arriba, logo en caja blanca) con el texto TABLERO TV."""
from PIL import Image, ImageDraw, ImageFont
im=Image.open('app-habilitado/icon.png').convert('RGBA')
W,H=im.size; d=ImageDraw.Draw(im)
bg=im.getpixel((8,H-8))
d.rectangle([0,210,W,H],fill=bg)
f=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf',48)
for i,t in enumerate(['TABLERO TV']):
    w=d.textlength(t,font=f); x=(W-w)/2; y=245
    d.text((x+2,y+3),t,font=f,fill=(0,0,0,110)); d.text((x,y),t,font=f,fill='white')
im.save('racks/icon.png'); print('racks/icon.png',im.size)
