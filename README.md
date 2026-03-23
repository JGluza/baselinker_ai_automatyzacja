# BaseLinker SEO & Compliance Automator (GPT-4o)

Zaawansowane narzędzie w języku Python do automatycznej optymalizacji danych produktowych. Skrypt integruje system **BaseLinker** z modelem **OpenAI GPT-4o**, aby generować opisy przyjazne dla SEO oraz zgodne z polskimi przepisami dotyczącymi suplementów diety.

## Kluczowe funkcje
* **Automatyczny Copywriting SEO:** Przekształca surowe dane techniczne w atrakcyjne i ustrukturyzowane opisy HTML.
* **Weryfikacja Zgodności Prawnej (Compliance):** Automatycznie wykrywa i zamienia niedozwolone oświadczenia medyczne (niezgodne z regulacjami GIS/EFSA) na bezpieczne, opisowe sformułowania.
* **Zaawansowany Sanitizer HTML:** Autorski mechanizm oparty na Regex, który czyści kod ze zbędnych stylów i tagów śledzących, zachowując nienaruszoną strukturę tabel i zdjęć.
* **Dynamiczne Pola Dodatkowe:** Wyodrębnia i formatuje sekcje takie jak: *Składniki aktywne*, *Sposób użycia*, *Przechowywanie* oraz *Środki ostrożności*.
* **Pełna Integracja API:** Dwukierunkowa komunikacja z BaseLinker Inventory API oraz OpenAI Chat Completions.

## Bezpieczeństwo i Dobre Praktyki
* **Zarządzanie Sekretami:** Klucze API są przechowywane w zmiennych środowiskowych (`.env`), co zapobiega ich wyciekowi do repozytorium.
* **Walidacja Danych:** Skrypt wymusza format JSON z AI i weryfikuje integralność danych przed wysłaniem ich do bazy BaseLinkera.
* **Optymalizacja zapytań:** Implementacja przerw czasowych (sleep) i limitów, aby zapewnić stabilną pracę z limitami API.

## Stos technologiczny
* **Język:** Python 3.10+
* **Modele AI:** OpenAI GPT-4o
* **Integracje:** BaseLinker API
* **Biblioteki:** `requests`, `python-dotenv`, `re`, `json`

## Jak to działa
1. Pobranie danych produktu (nazwa, opisy) bezpośrednio z magazynu BaseLinker.
2. Wstępne czyszczenie kodu HTML z "śmieciowych" znaczników.
3. Przesłanie ustrukturyzowanego promptu do GPT-4o z uwzględnieniem rygorystycznych zasad prawnych.
4. Przetworzenie odpowiedzi JSON i automatyczna aktualizacja wielu pól produktu (opis główny + pola dodatkowe) za jednym razem.
