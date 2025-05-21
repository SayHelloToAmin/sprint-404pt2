
import json
import re
import os

persian_to_english_digits = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

def parse_price(price_str):
    if not price_str:
        return None
    digits = price_str.split("تومان")[0].strip().translate(persian_to_english_digits).replace(",", "")
    return int(digits) if digits.isdigit() else None

def parse_area(area_str):
    if not area_str:
        return None
    digits = area_str.translate(persian_to_english_digits)
    return int(digits) if digits.isdigit() else None

def parse_room_count(room_str):
    if not room_str:
        return None
    digits = re.findall(r'\d+', room_str.translate(persian_to_english_digits))
    return int(digits[0]) if digits else None

def parse_year(built_year_str):
    if not built_year_str:
        return None
    built_year_str = built_year_str.translate(persian_to_english_digits)
    if "قبل" in built_year_str:
        digits = re.findall(r'\d+', built_year_str)
        return int(digits[0]) - 1 if digits else 1369
    digits = re.findall(r'\d+', built_year_str)
    return int(digits[0]) if digits else None

def extract_features(features_list):
    flags = {
        "parking": False,
        "anbari": False,
        "balcony": False
    }
    for f in features_list or []:
        f = f.strip()
        if "پارکینگ" in f:
            flags["parking"] = True
        if "انباری ندارد" in f:
            flags["anbari"] = False
        elif "انباری" in f:
            flags["anbari"] = True
        if "بالکن" in f:
            flags["balcony"] = True
    return flags

def clean_real_estate(raw_data):
    cleaned = {
        "title": raw_data.get("title"),
        "address": raw_data.get("address"),
        "price": parse_price(raw_data.get("price_total")),
        "area": parse_area(raw_data.get("area")),
        "room_count": parse_room_count(raw_data.get("room_count")),
        "built_year": parse_year(raw_data.get("built_year")),
        "features": extract_features(raw_data.get("features")),
        "image_urls": raw_data.get("images", []),
        "url": raw_data.get("url")
    }
    return cleaned

def clean_all_ads(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"{input_file} not found")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_ads = json.load(f)

    cleaned_ads = []
    for i, ad in enumerate(raw_ads):
        try:
            cleaned_ads.append(clean_real_estate(ad))
        except Exception as e:
            pass

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_ads, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(cleaned_ads)} ads has been cleaned up and saved in {output_file}")

if __name__ == "__main__":
    clean_all_ads("data/scraped_ads.json", "data/ads_cleaned.json")
