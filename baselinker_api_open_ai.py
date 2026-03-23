import os
import requests
import json
import time
import re
from openai import OpenAI
from dotenv import load_dotenv

# Wczytywanie kluczy z pliku .env (bezpieczeństwo danych)
load_dotenv()

# KONFIGURACJA POBIERANA ZE ŚRODOWISKA
BL_TOKEN = os.getenv('BL_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')
INVENTORY_ID = 53860

# Mapowanie pól dodatkowych BaseLinker
EXTRA_FIELDS = {
    'how_to_use': 'extra_field_23935',  # Jak stosować
    'ingredients': 'extra_field_23936',  # Składniki aktywne
    'storage': 'extra_field_23937',  # Przechowywanie
    'precautions': 'extra_field_23938',  # Środki ostrożności
}

client = OpenAI(api_key=OPENAI_KEY)


def call_bl(method, parameters):
    """Komunikacja z API BaseLinker"""
    url = "https://api.baselinker.com/connector.php"
    data = {'token': BL_TOKEN, 'method': method, 'parameters': json.dumps(parameters)}
    try:
        result = requests.post(url, data=data).json()
        if result.get('status') != 'SUCCESS':
            print(f"[BŁĄD BL] {method}: {result}")
        return result
    except Exception as e:
        print(f"[BŁĄD POŁĄCZENIA]: {e}")
        return {}


def pre_clean_html(html: str) -> str:
    """Zaawansowane czyszczenie HTML z niepotrzebnych atrybutów i śmieci edytorskich"""
    if not html:
        return ''
    # Usuwanie divów z klasami śledzącymi/social media
    html = re.sub(
        r'<div[^>]*class="[^"]*(__fb|l9j0dhe7|j83agx80|ns4p8fja|cxgpxx05|rq0escxv|WaaZC|rPeykc|bsmXxe)[^"]*"[^>]*>.*?</div>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    # Usuwanie atrybutów inline przy zachowaniu tagów
    html = re.sub(r'\s(style|class|data-[a-z\-]+|id|role)="[^"]*"', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<span>([^<]*)</span>', r'\1', html)
    html = re.sub(r'<div[^>]*>\s*</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<ul[^>]*>\s*<li[^>]*>\s*</li>\s*</ul>', '', html, flags=re.DOTALL)
    html = re.sub(r'\n{3,}', '\n\n', html)
    html = re.sub(r'  +', ' ', html)
    return html.strip()


# PEŁNY PROMPT ZGODNY Z TWOIM ORYGINAŁEM (Kluczowy dla Compliance)
SYSTEM_PROMPT = """Jesteś doświadczonym copywriterem SEO i specjalistą ds. regulacji w branży suplementów diety i ziołolecznictwa. 
Twoje teksty są zgodne z polskim prawem (Ustawa o bezpieczeństwie żywności) i regulacjami UE dotyczącymi suplementów diety.

ZASADY NADRZĘDNE — ZAWSZE PRZESTRZEGAJ:
1. ZAKAZY PRAWNE: Nigdy nie stosuj sformułowań sugerujących działanie lecznicze ani diagnozowanie chorób.
   ZAKAZANE: "leczy", "lekarstwo", "kuruje", "eliminuje chorobę", "stosowany przy [choroba]", "działa jak lek".
   DOZWOLONE: "może wspierać", "pomaga utrzymać", "przyczynia się do", "wspomaga prawidłowe funkcjonowanie".
2. CLAIMS: Używaj wyłącznie claimów zatwierdzonych przez EFSA lub sformułowań opisowych.
3. SUPLEMENTY: Zawsze zaznacz że produkt jest suplementem diety, nie zastąpi zbilansowanej diety.
4. JSON: Zwracaj WYŁĄCZNIE poprawny JSON, zero tekstu poza nim. Zachowuj wszystkie tagi <img> w całości."""


def ai_process_content(name: str, description: str, extra_1: str) -> dict:
    """Procesowanie treści przez GPT-4o z zachowaniem pełnej struktury i wymogów prawnych"""
    desc_pre = pre_clean_html(description)
    extra_pre = pre_clean_html(extra_1)

    prompt = f"""Przygotuj zoptymalizowane treści produktowe dla suplementu diety ze sklepu zielarskiego: "{name}".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MATERIAŁ WEJŚCIOWY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Opis główny:
{desc_pre}

Opis dodatkowy 1:
{extra_pre}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZADANIE A — CZYSZCZENIE HTML (clean_description + clean_extra_1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Usuń wszystkie atrybuty style="...", class="...", data-*, id, role z tagów.
• Dozwolone tagi: <h2> <h4> <p> <br> <b> <strong> <ul> <ol> <li> <table> <tr> <td> <img>.
• Tagi <img> przepisz w 100% bez zmian (zachowaj src, width, height, alt).
• NIE skracaj, NIE parafrazuj, NIE pomijaj żadnego zdania ani tabeli z oryginału.
• Słowa kluczowe produktu (nazwa rośliny, forma, dawka) owijaj w <strong>.
• Nagłówki sekcji formatuj jako <h4>, akapity jako <p>, listy jako <ul><li>.
• Usuń zduplikowane informacje jeśli ta sama treść powtarza się dosłownie.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZADANIE B — SEKCJE DODATKOWE (how_to_use / ingredients / storage / precautions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wyodrębnij dane z opisów wejściowych i uzupełnij wiedzą ekspercką o produkcie "{name}".

[how_to_use] — "Jak stosować"
• Zacznij od: <h4>Jak stosować {name}:</h4>
• Podaj dawkę dzienną, porę przyjmowania, formę. Owijaj kluczowe frazy w <strong>.

[ingredients] — "Składniki aktywne"
• Zacznij od: <h4>Składniki aktywne {name}:</h4>
• Wymień składniki z dawkami + krótkie wyjaśnienie zgodne z EFSA. Użyj nazw łacińskich.

[storage] — "Przechowywanie"
• Zacznij od: <h4>Przechowywanie:</h4>
• Temperatura, wilgotność, dostęp dzieci.

[precautions] — "Środki ostrożności"
• Zacznij od: <h4>Środki ostrożności:</h4>
• Obowiązkowo: nie przekraczać dawki, nie zastępuje diety, konsultacja z lekarzem.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FORMAT ODPOWIEDZI (WYŁĄCZNIE JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{
  "clean_description": "...",
  "clean_extra_1": "...",
  "how_to_use": "...",
  "ingredients": "...",
  "storage": "...",
  "precautions": "..."
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[BŁĄD AI]: {e}")
        return {}


def update_and_verify(product_id: int):
    """Główna procedura aktualizacji produktu w BaseLinkerze"""
    print(f"\n[1/4] Pobieram produkt ID: {product_id}...")
    res = call_bl('getInventoryProductsData', {'inventory_id': INVENTORY_ID, 'products': [product_id]})

    products = res.get('products', {})
    if str(product_id) not in products:
        print(f"[BŁĄD] Nie znaleziono produktu.")
        return

    prod = products[str(product_id)]
    tf = prod.get('text_fields', {})

    print(f"[2/4] Procesowanie przez AI (może potrwać chwilę)...")
    processed = ai_process_content(tf.get('name', ''), tf.get('description', ''), tf.get('description_extra1', ''))

    if not processed: return

    print(f"[3/4] Wysyłanie aktualizacji do BaseLinker...")
    text_fields_payload = {
        'description': processed.get('clean_description'),
        'description_extra1': processed.get('clean_extra_1'),
    }
    for ai_key, bl_key in EXTRA_FIELDS.items():
        text_fields_payload[bl_key] = processed.get(ai_key, '')

    res_update = call_bl('addInventoryProduct', {
        'inventory_id': INVENTORY_ID,
        'product_id': product_id,
        'text_fields': text_fields_payload,
    })

    print(f"[4/4] Wynik: {res_update.get('status')}")
    if res_update.get('status') == 'SUCCESS':
        print("✓ Produkt został pomyślnie zaktualizowany i zoptymalizowany.")


if __name__ == "__main__":
    if not BL_TOKEN or not OPENAI_KEY:
        print("BŁĄD: Brak kluczy API. Upewnij się, że plik .env istnieje i zawiera poprawne dane.")
    else:
        # ID produktu do testu
        TEST_ID = 353879961
        update_and_verify(TEST_ID)