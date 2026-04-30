# Email domain — universal best practices

Aktiveres når tekst er en e-post (broadcast, transaksjonell, individuell).

## Subject-linje

- **Maks 70 tegn** — flere klienter trunkerer over dette
- Konkret over kreativ
- Vis hvem du er hvis ikke fra-feltet er kjent
- Ikke clickbait uten innhold ("Du vil ikke tro hva som...")
- Ikke for mange utropstegn

**Bra mønster:** `[Hva]: [konkret detalj]` eller `[Tema]. [Tilleggspoeng].`

Eksempler:
- ✅ "Vol. 3 er 11. mai. Vis frem det du bygger."
- ✅ "Masterclasses: Først ut VibeMarketing med Sean Percival" (55 tegn)
- ❌ "Spennende oppdatering fra oss!" (vagt)

## Preview text (skjult preheader)

Alltid inkluder. Vises i innboksen sammen med subject. Maks ~90 tegn.

Ikke gjenta subject — supplér.

```html
<div style="display:none;max-height:0;overflow:hidden;font-size:1px;line-height:1px;color:#ffffff;">
  Vol. 3 på Mesh 11. mai. Pluss to nye dagskurs og en ny masterclass.&nbsp;&zwnj;&nbsp;&zwnj;...
</div>
```

Padding av `&nbsp;&zwnj;` etter teksten forhindrer at e-post-klienter henter første linje av body som preview.

## Personalisering

Resend-syntaks: `{{{FIRST_NAME}}}` eller `{{{FIRST_NAME|fallback}}}`.

**Tom fallback** `{{{FIRST_NAME|}}}` gir trailing space hvis tom — accept det eller bytt til ren "Hei!".

**Med fallback** `{{{FIRST_NAME|der}}}` gir "Hei der!" for de uten navn — fungerer hvis fallback-ord er naturlig, men signaliserer template hvis tydelig.

**Ren "Hei!"** for alle: sikrest, ingen artefakter.

Beslutning: Hvis 90%+ har first_name, bruk variabel. Hvis under, ren "Hei!".

## Avsender

Format: `Navn fra Brand <email@domene.no>`

Eksempel: `Simon fra Vibelabs <simon@vibelabs.no>`

Ikke "noreply@" for marketing — folk vil kunne svare.

## Footer-essensials

Hver markedsmail må ha:

1. **Avmeldingslenke** (lovkrav i EU/Norge):
   ```html
   <a href="{{{RESEND_UNSUBSCRIBE_URL}}}">Avmeld deg</a>
   ```
2. **Avsenderidentifikasjon** — hvem som sender, hvor du er

Transaksjonelle mails (faktura, kvittering) trenger ikke avmeldingslenke, men marketing-broadcasts gjør.

## HTML-struktur

- **Inline CSS** — eksterne stylesheets fungerer ikke i de fleste e-post-klienter
- **Table-based layout** — mer pålitelig enn flexbox/grid på tvers av klienter
- **Maks 580px width** — passer mobile + desktop
- **Skjult preheader tidlig** — første tag i body
- **Mørke knapper på hvit bakgrunn** — universelt lesbart

## Opt-out banner (når du sender til ny audience)

For audiences som ikke har eksplisitt opted in (f.eks. event-deltakere som mottar nyhetsbrev første gang):

```
Du får dette fordi du var med på [event/årsak]. 
Vi sender [forventning: f.eks. "et par mails i måneden om X"]. 
[Avmeld deg her.]
```

Setter forventning + tydelig vei ut. Reduserer rapportering som spam.

## CTA-strategi

- **Maks 3-4 CTAs per mail** — flere skaper paralyse
- **Én primær CTA tidlig** — det viktigste
- **Sekundære CTAs lenger ned** — sortert etter prioritet
- **Varier wording**: "Meld deg på", "Sikre plass", "Les mer", "RSVP" — ikke samme på alle

## Diskontskoder

Hvis koden har regler (f.eks. "ikke gyldig for early-bird", "kun nye kunder"), si det rett ved siden av. Ikke skjul i fine print.

```
Bruk koden VIBENEWS20 for 20% rabatt (gjelder ikke early-bird).
```

## Test før send

- Send test til deg selv først
- Sjekk preview text vises
- Sjekk personalisering rendrer
- Sjekk alle lenker funker
- Sjekk avmeldingslenke funker
- Aktiver open + click tracking i avsender-dashboardet
