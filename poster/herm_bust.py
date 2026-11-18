# Bust for the herm (Hermes head on a pillar) in poster-networking-herm.html.
# Crops statue-hermes-halftone.png (made by halftone_hermes.py) to head + shoulders and gives it a classic
# rounded bust cut at the bottom, so it can sit on a plinth. Usage: python3 herm_bust.py
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
im = Image.open('statue-hermes-halftone.png')
k = im.width / 750                                    # halftone covers preview x 120..870, y 40..640
box = [int(v) for v in ((190-120)*k, 0, (690-120)*k, (585-40)*k)]
b = im.crop(box); W, H = b.size
cut = Image.new('L', b.size, 0); d = ImageDraw.Draw(cut)
# rounded bust bottom: an ellipse whose lower arc forms the cut, plus everything above its centre
d.ellipse((W*.02, -H*.35, W*.98, H*.985), fill=255)
d.rectangle((0, 0, W, H*.3), fill=255)
cut = cut.filter(ImageFilter.GaussianBlur(3))
a = np.asarray(b.split()[3]).astype(float) * np.asarray(cut).astype(float) / 255
b.putalpha(Image.fromarray(a.astype(np.uint8)))
b.save('herm-bust.png', optimize=True); print(b.size)
