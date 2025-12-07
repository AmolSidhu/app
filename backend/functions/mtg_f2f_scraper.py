from datetime import datetime
import pandas as pd
import unicodedata
import requests
import bs4
import time
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize_text(text):
    if not text:
        return ''
    return unicodedata.normalize("NFKC", text).strip()


def extract_data(data_block):
    fields = {}
    if not data_block:
        return fields

    for row in data_block.find_all("div", class_="bb-pdp-metafield"):
        text = row.get_text(separator=' ', strip=True)
        if ':' in text:
            label, val = text.split(':', 1)
            fields[normalize_text(label)] = normalize_text(val)
        else:
            fields[normalize_text(text)] = ''
    return fields


def mtg_f2f_scraper(file_path, serial, output_serial, output_path):
    path = file_path + serial + '.csv'

    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"[ERROR] Could not read input file {path}: {e}")
        return

    if 'Links' not in df.columns:
        print(f"[ERROR] Input file {path} must contain a 'Links' column.")
        return

    f2f_df = pd.DataFrame()

    for link, copies in zip(df['Links'], df['Copies']):
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for attempt in range(3):
                try:
                    results = requests.get(link, timeout=15)
                    if results.status_code == 200:
                        break
                    else:
                        print(f"[WARN] Non-200 ({results.status_code}) for {link}, retrying...")
                except requests.exceptions.RequestException as e:
                    print(f"[WARN] Request failed ({e}), retrying...")
                time.sleep(1.5)
            else:
                print(f"[ERROR] Failed to fetch {link} after 3 attempts.")
                continue

            soup = bs4.BeautifulSoup(results.text, 'lxml')

            play_block = soup.find("div", class_="product-info-left")
            price_block = soup.find("div", class_="product-info-right")

            if not play_block or not price_block:
                continue

            title_div = play_block.find("div", class_="product__title")
            card_name = normalize_text(title_div.get_text()) if title_div else "N/A"

            data = extract_data(play_block.find("div", class_="bb-pdp-metafields"))

            alt_art = data.get('Alternate Art Qualifier', 'N/A')
            card_set = data.get('Set', 'N/A')
            card_type = data.get('Type Line', data.get('Type', 'N/A'))
            card_finish = data.get('Finish', 'N/A')
            card_rarity = data.get('Rarity', 'N/A')
            card_text = data.get('Card Text', 'N/A')

            legality_dict = {}
            legalities = play_block.find("span", class_="bb-pdpm-data-legality")

            if legalities:
                for div in legalities.find_all("div", recursive=False):
                    try:
                        label = normalize_text(div.get_text(strip=True))
                        svg = div.find("svg")
                        if svg and svg.has_attr("id"):
                            svg_id = svg["id"]
                            if svg_id == "Groupe_3319":
                                legality_dict[label] = True
                            elif svg_id == "Groupe_3321":
                                legality_dict[label] = False
                    except Exception as inner_e:
                        print(f"[WARN] Error parsing legality div: {inner_e}")

            prices = price_block.find_all("div", class_="f2f-featured-variant")
            near_mint_price = lightly_played_price = "N/A"

            if len(prices) > 0:
                nm = prices[0].find("span", class_="price-item price-item--regular")
                near_mint_price = normalize_text(nm.get_text()) if nm else "N/A"

            if len(prices) > 1:
                lp = prices[1].find("span", class_="price-item price-item--regular")
                lightly_played_price = normalize_text(lp.get_text()) if lp else "N/A"

            df2f = pd.DataFrame({
                'Scrape Time': [current_time],
                'Card Name': [card_name],
                'Link': [link],
                'Alternate Art Qualifier': [alt_art],
                'Set': [card_set],
                'Type': [card_type],
                'Finish': [card_finish],
                'Rarity': [card_rarity],
                'Card Text': [card_text],
                'Near Mint Price': [near_mint_price],
                'Lightly Played Price': [lightly_played_price],
                'Commander Legal': [legality_dict.get('Commander', 'N/A')],
                'Legacy Legal': [legality_dict.get('Legacy', 'N/A')],
                'Modern Legal': [legality_dict.get('Modern', 'N/A')],
                "Not Tournament Legal": [legality_dict.get('Not Tournament Legal', 'N/A')],
                'Old School Legal': [legality_dict.get('Old School', 'N/A')],
                'Pauper Legal': [legality_dict.get('Pauper', 'N/A')],
                'Pioneer Legal': [legality_dict.get('Pioneer', 'N/A')],
                'Premodern Legal': [legality_dict.get('Premodern', 'N/A')],
                'Standard Legal': [legality_dict.get('Standard', 'N/A')],
                'Vintage Legal': [legality_dict.get('Vintage', 'N/A')],
                'Copies': [copies]
            })

            f2f_df = pd.concat([f2f_df, df2f], ignore_index=True)

            time.sleep(1.03)

        except Exception as e:
            print(f"[ERROR] Error processing {link}: {e}")
            continue

    output_dir = output_path + output_serial + '.csv'
    try:
        f2f_df.to_csv(output_dir, index=False, encoding='utf-8-sig')
    except Exception as e:
        print(f"[ERROR] Failed to save CSV to {output_dir}: {e}")