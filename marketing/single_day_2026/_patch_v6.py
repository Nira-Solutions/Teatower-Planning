"""Patch v6 : filtre cartoon léger sur les produits + fille en T-shirt Teatower avec son chat."""
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "starter_pack_single_day.html")
s = open(p, encoding="utf-8").read()

# 1) filtre cartoon léger sur les produits
s = s.replace(".side img,.side .crop{position:absolute;mix-blend-mode:multiply;filter:saturate(1.15)}",
              ".side img,.side .crop{position:absolute;mix-blend-mode:multiply;filter:url(#toon)}")
toon = """<svg width="0" height="0" style="position:absolute">
  <filter id="toon" color-interpolation-filters="sRGB">
    <feColorMatrix in="SourceGraphic" type="saturate" values="1.35" result="sat"/>
    <feComponentTransfer in="sat" result="post">
      <feFuncR type="discrete" tableValues="0 .18 .36 .55 .75 .9 1"/>
      <feFuncG type="discrete" tableValues="0 .18 .36 .55 .75 .9 1"/>
      <feFuncB type="discrete" tableValues="0 .18 .36 .55 .75 .9 1"/>
    </feComponentTransfer>
    <feColorMatrix in="SourceGraphic" type="matrix" values=".3 .59 .11 0 0  .3 .59 .11 0 0  .3 .59 .11 0 0  0 0 0 1 0" result="gray"/>
    <feConvolveMatrix in="gray" order="3" kernelMatrix="-1 -1 -1 -1 8 -1 -1 -1 -1" preserveAlpha="true" result="edge"/>
    <feComponentTransfer in="edge" result="lines">
      <feFuncR type="linear" slope="-2.2" intercept="1"/>
      <feFuncG type="linear" slope="-2.2" intercept="1"/>
      <feFuncB type="linear" slope="-2.2" intercept="1"/>
    </feComponentTransfer>
    <feBlend in="post" in2="lines" mode="multiply"/>
  </filter>
</svg>
"""
if 'id="toon"' not in s:
    s = s.replace('<div class="scene">', toon + '<div class="scene">', 1)

# 2) nouveau personnage
a = s.index("    <!-- personnage")
b = s.index("</svg>", s.index('<svg class="perso"')) + len("</svg>")
perso = """    <!-- personnage : fille en T-shirt Teatower avec son chat -->
    <div class="bub main">
      <svg class="perso" viewBox="0 0 460 820" width="454" height="814" style="position:absolute;left:0;top:0">
        <defs>
          <radialGradient id="skin" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#ffe0c4"/><stop offset="1" stop-color="#e9b48c"/></radialGradient>
          <radialGradient id="hair" cx="40%" cy="30%" r="75%"><stop offset="0" stop-color="#8a5a3b"/><stop offset="1" stop-color="#4a2c1a"/></radialGradient>
          <linearGradient id="tee" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ef8a4a"/><stop offset="1" stop-color="#c8602a"/></linearGradient>
          <linearGradient id="jean" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3f6596"/><stop offset="1" stop-color="#2a4670"/></linearGradient>
          <radialGradient id="cat" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#a9adb6"/><stop offset="1" stop-color="#6c717c"/></radialGradient>
        </defs>
        <g transform="translate(-30 -190) scale(1.2)">
          <!-- ombre -->
          <ellipse cx="214" cy="792" rx="110" ry="14" fill="#000" opacity=".45"/>
          <!-- jambes + baskets -->
          <rect x="160" y="600" width="46" height="165" rx="20" fill="url(#jean)"/>
          <rect x="222" y="600" width="46" height="165" rx="20" fill="url(#jean)"/>
          <ellipse cx="178" cy="770" rx="38" ry="18" fill="#f4f4f4"/>
          <ellipse cx="252" cy="770" rx="38" ry="18" fill="#f4f4f4"/>
          <rect x="142" y="774" width="72" height="8" rx="4" fill="#c25a22"/>
          <rect x="216" y="774" width="72" height="8" rx="4" fill="#c25a22"/>

          <!-- cou -->
          <rect x="198" y="405" width="32" height="40" rx="10" fill="#e3a77c"/>
          <!-- T-shirt + manches courtes -->
          <path d="M152 446 L112 500 L142 520 L166 486 Z" fill="url(#tee)"/>
          <path d="M276 446 L316 500 L286 520 L262 486 Z" fill="url(#tee)"/>
          <path d="M150 445 Q214 428 278 445 L292 615 Q214 632 136 615 Z" fill="url(#tee)"/>
          <path d="M190 436 Q214 452 238 436" stroke="#a84a18" stroke-width="7" fill="none" stroke-linecap="round"/>
          <!-- logo Teatower sur le T-shirt -->
          <image href="img/logo_blanc.svg" x="176" y="450" width="76" height="56"/>

          <!-- queue du chat qui pend -->
          <path d="M150 585 Q120 620 140 660 Q150 676 160 664 Q142 628 168 596 Z" fill="url(#cat)"/>
          <!-- corps du chat -->
          <ellipse cx="210" cy="570" rx="78" ry="40" fill="url(#cat)"/>
          <path d="M165 552 q8 14 0 30 M190 545 q8 16 0 36 M215 545 q8 16 0 36" stroke="#5a5f69" stroke-width="5" fill="none" stroke-linecap="round"/>
          <!-- tête du chat -->
          <path d="M248 508 L256 470 L276 496 Z" fill="#7d828c"/>
          <path d="M300 496 L320 470 L326 508 Z" fill="#7d828c"/>
          <path d="M254 492 L258 478 L268 492 Z M308 492 L318 478 L320 492 Z" fill="#f2a5b0"/>
          <ellipse cx="288" cy="528" rx="44" ry="38" fill="url(#cat)"/>
          <ellipse cx="272" cy="524" rx="8" ry="10" fill="#9fd36a"/><ellipse cx="304" cy="524" rx="8" ry="10" fill="#9fd36a"/>
          <ellipse cx="272" cy="525" rx="3" ry="8" fill="#1a1a1a"/><ellipse cx="304" cy="525" rx="3" ry="8" fill="#1a1a1a"/>
          <path d="M283 540 L293 540 L288 546 Z" fill="#f28a9a"/>
          <path d="M288 546 Q282 552 276 548 M288 546 Q294 552 300 548" stroke="#3a3a3a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
          <path d="M262 542 L236 538 M262 547 L238 550 M314 542 L340 538 M314 547 L338 550" stroke="#eee" stroke-width="2" stroke-linecap="round"/>

          <!-- bras qui tiennent le chat -->
          <path d="M128 510 Q140 590 200 598" stroke="url(#skin)" stroke-width="30" fill="none" stroke-linecap="round"/>
          <path d="M300 510 Q300 560 262 574" stroke="url(#skin)" stroke-width="30" fill="none" stroke-linecap="round"/>
          <circle cx="206" cy="596" r="17" fill="url(#skin)"/>
          <circle cx="258" cy="575" r="17" fill="url(#skin)"/>

          <!-- cheveux arrière + chignon -->
          <circle cx="214" cy="236" r="40" fill="url(#hair)"/>
          <path d="M120 330 Q118 240 214 236 Q310 240 308 330 L312 410 Q290 420 280 380 L148 380 Q138 420 116 410 Z" fill="url(#hair)"/>
          <!-- tête -->
          <ellipse cx="214" cy="330" rx="84" ry="88" fill="url(#skin)"/>
          <path d="M130 312 Q140 240 214 240 Q292 240 300 314 Q262 272 214 290 Q170 270 130 312 Z" fill="url(#hair)"/>
          <ellipse cx="166" cy="372" rx="15" ry="9" fill="#ff8f8f" opacity=".45"/>
          <ellipse cx="262" cy="372" rx="15" ry="9" fill="#ff8f8f" opacity=".45"/>
          <!-- yeux -->
          <circle cx="182" cy="340" r="8" fill="#2a1a12"/><circle cx="185" cy="337" r="2.6" fill="#fff"/>
          <circle cx="246" cy="340" r="8" fill="#2a1a12"/><circle cx="249" cy="337" r="2.6" fill="#fff"/>
          <path d="M166 310 Q180 302 196 308" stroke="#4a2c1a" stroke-width="5" fill="none" stroke-linecap="round"/>
          <path d="M232 308 Q248 302 262 310" stroke="#4a2c1a" stroke-width="5" fill="none" stroke-linecap="round"/>
          <!-- lunettes -->
          <circle cx="182" cy="340" r="27" fill="rgba(255,255,255,.18)" stroke="#151515" stroke-width="7"/>
          <circle cx="246" cy="340" r="27" fill="rgba(255,255,255,.18)" stroke="#151515" stroke-width="7"/>
          <path d="M209 338 Q214 332 219 338" stroke="#151515" stroke-width="6" fill="none"/>
          <path d="M155 336 L132 328" stroke="#151515" stroke-width="6" stroke-linecap="round"/>
          <path d="M273 336 L296 328" stroke="#151515" stroke-width="6" stroke-linecap="round"/>
          <!-- nez + sourire -->
          <path d="M214 352 Q210 366 218 368" stroke="#c98a62" stroke-width="4" fill="none" stroke-linecap="round"/>
          <path d="M190 386 Q214 408 240 386" stroke="#8a3a2a" stroke-width="6" fill="#fff" stroke-linecap="round"/>
        </g>
      </svg>"""
s = s[:a] + perso + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("ok, reste CHERCHE :", "CHERCHE" in s)
