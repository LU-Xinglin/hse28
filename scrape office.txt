import requests
from lxml import html
import re, csv, time, random
from urllib.parse import urljoin

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.28hse.com/",
    "Connection": "keep-alive"
})

with open("office_transactions_rent_test.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Date","Month","District","Address","Transaction Price","Sq Price","Area","Source","Link","Type"])

def parse_price(text):
    num = re.sub(r"[^\d.]", "", text)
    return int(num) if "Leased" in text else 0

def clean_num(text):
    return int(re.sub(r"[^\d]", "", text)) if text else 0

for page in range(1, 100):
    list_url = f"https://www.28hse.com/en/estate/office?page={page}"
    resp = s.get(list_url)
    tree = html.fromstring(resp.text)
    
    items = tree.cssselect("div.item")
    detail_urls = [urljoin("https://www.28hse.com", item.get("href")) for item in items if '/detail/' in item.get("href", "")]
    
    for detail_url in detail_urls:
        print(f"Processing building: {detail_url}")
        district = ""
        for p in range(1, 3):
            url = f"{detail_url}/transaction/rent?page={p}"
            resp = s.get(url)
            t = html.fromstring(resp.text)
            
            if p == 1:
                divs = t.xpath("//div[@class='ui hidden less2 clearing divider']/following-sibling::div[1]/text()")
                # district = divs[0].split()[0] if divs else ""
                district = divs[0] if divs else ""
            
            trans_items = t.cssselect("tr[unit-id]")
            if not trans_items and p > 1: break
            
            rows = []
            for item in trans_items:
                date_xpath = item.xpath('.//i[@class="calendar alternate icon"]/following-sibling::text()')
                date = date_xpath[0].strip() if date_xpath else ""
                month = date[:7].replace("-", "") if date else ""
                
                header = item.cssselect("div.header")
                building_name = ""
                if header:
                    header_text = header[0].text_content()
                    building_name = header_text.split('|')[0].strip()
                
                addr_elem = item.cssselect("a[title]")
                unit_text = addr_elem[0].text_content().strip() if addr_elem else ""
                
                if unit_text and building_name and building_name in unit_text:
                    address = unit_text
                else:
                    address = f"{unit_text}, {building_name}" if unit_text else building_name     
                # Price
                price_xpath = item.xpath('.//div[contains(@class,"price")]//text()')
                price_text = "".join([t.strip() for t in price_xpath if t.strip() and "HKD" in t or "Leased" in t])
                price_text = re.search(r"HKD\$([\d,]+)", price_text).group(1).replace(",","") if "HKD" in price_text else ""
                
                # Link
                link = urljoin("https://www.28hse.com", addr_elem[0].get("href")) if addr_elem else ""
                
                # Area
                area_td = item.cssselect("td")[1].text_content().strip() if len(item.cssselect("td")) > 1 else ""
                area_match = re.search(r"Gross ([\d,]+)ft", area_td)
                area = clean_num(area_match.group(1)) if area_match else 0
                
                # Sq Price
                sq_elem = item.cssselect("span.unit_price")
                sq = clean_num(sq_elem[0].text_content()) if sq_elem else 0
                
                # Source
                source_labels = item.cssselect("div.ui.label")
                source = source_labels[1].text.strip() if len(source_labels) > 1 else ""
                
                if date and price_text:
                    rows.append([date, month, district, address, parse_price(f"Leased HKD${price_text}"), sq, area, source, link, "Rent"])  # Type 顺便改成 Rent          
            print(f"Building {detail_url} page {p} found {len(rows)} records")
            if rows:
                with open("office_transactions_rent_test.csv", "a", newline="", encoding="utf-8-sig") as f:
                    w = csv.writer(f)
                    w.writerows(rows)
            
            time.sleep(random.uniform(1, 2))
    print(f"Completed page {page}")
