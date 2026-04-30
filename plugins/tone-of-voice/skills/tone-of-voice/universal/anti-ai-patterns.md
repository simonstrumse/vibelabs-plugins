# AI-fingeravtrykk — eliminer på sikte

Disse markørene avslører maskingenerert eller maskinoversatt tekst. Mennesker skriver sjelden slik. Søk etter dem i utkast før du sender.

## Universal-markører (alle språk, alle domener)

| KI-markør | Hvorfor det avslører seg | Hva du skriver istedenfor |
|---|---|---|
| Em-dash (—) i body-tekst | Strongest single signal — se egen regel | Punktum, komma, kolon, parenteser |
| Lik avsnittslengde gjennom hele teksten | Dødt tegn på generert tekst | Variér: 1-setnings sammen med 6-setnings |
| Triple-adjektiv ("den vakre, historiske, sjarmerende") | Generert tekst stabler adjektiv | Velg det ene som faktisk betyr noe |
| Wikipedia-åpning ("Vibelabs er et selskap som...") | Definisjon-stil | Start med noe spesifikt og uventet |
| Generisk CTA ("Book i dag!", "Ikke gå glipp av") | Salgsbot-floskler | Konkret oppfordring eller bare en lenke |
| Symmetriske kontraster ("Ikke bare X, men også Y") | Direkte oversettelse av "not only X, but also Y" | "Både X og Y" eller bare nevn dem |
| "Det er verdt å nevne/merke seg at..." | Tom filler — fjerner energi | Slett. Bare si tingen direkte. |
| "I denne mailen/artikkelen skal vi..." | Meta-referanse, ingen snakker sånn | Aldri. Start med substans. |
| Passiv form som default | "Mailen kan oppleves som..." vs "Du opplever mailen" | Aktiv form |
| AI-overdrivelse ("revolusjonerende", "transformativ") | Markedsfloskler | Konkret utfall |
| Forklaring av det åpenbare ("Som vi alle vet...") | Filler-flom | Hopp over |
| Overdreven hedge ("kanskje", "muligens", "trolig" stablet) | Usikker AI-output | Velg én eller fjern |
| Symmetrisk struktur ("Først X. Deretter Y. Til slutt Z.") | Format-koplet generert | Bryt strukturen, varier |

## Sjekk-rutinen

Før du leverer tekst, gjør disse stikkprøvene:

1. **Em-dash-search:** `grep "—"` — antall hits skal være 0 for body
2. **Adjektiv-stabel:** finn 3+ adjektiv på rad. Dropp 2 av 3.
3. **Setningslengde:** marker hver setning. Hvis alle er 8-15 ord, restruktur.
4. **Avsnittslengde:** alle avsnitt 3-4 setninger? Bryt opp.
5. **Floskler:** søk etter "verdt å nevne", "I denne", "Ikke bare", "Det er verdt"

## Pattern: humanitet over perfeksjon

Maskinell tekst er ofte gramatikalsk perfekt og rytmisk uniformt. Mennesker er rotete:
- Bruker fragmenter
- Begynner setninger med "Og" eller "Men"
- Stopper midt i tanken
- Bruker hverdagslige formuleringer

Litt rotete er menneskelig. Helt polert er AI.
