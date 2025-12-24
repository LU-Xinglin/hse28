import requests
import json
import csv
from datetime import datetime
import random
import time

def fetch_and_process_data(url, page="10"):
    """
    acquire data and save to csv file
    sent POST request to the specified URL with page parameter,
    parse the JSON response, extract relevant fields, and save them to a CSV file.
    """
    post_data = {"page": page}
    try:
        # sent POST request
        response = requests.post(url, data=post_data, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # check response status
        response.raise_for_status()
        
        # parse JSON response
        data = response.json()
        
        # extract items
        items = data['data']['results']['Items']
        
        if not items:
            print("No data found for the given page.")
            return
        
        # cvs fieldnames
        csv_fieldnames = ['Date', 'District', 'Address', 'Transaction Price', 'Sq Price', 'Area', 'Source', 'Link']
        
        # generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"data_{page}.csv"
        
        # write to CSV file
        with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
            writer.writeheader()
            
            for item in items:
                row = {}
                
                # Date
                row['Date'] = item.get('transaction_date', item.get('detail_date', ''))
                
                # District
                row['District'] = item.get('detail_district', '')
                
                # Address
                row['Address'] = item.get('detail_address', '')
                
                # Transaction Price
                row['Transaction Price'] = item.get('detail_price', item.get('price', ''))
                
                # Sq Price (use detail_sqprice first, if not available use saleable_sqprice)
                row['Sq Price'] = item.get('detail_sqprice', item.get('saleable_sqprice', ''))
                
                # Area (use detail_saleable_area first, if not available use saleable_area)
                row['Area'] = item.get('detail_saleable_area', item.get('saleable_area', ''))
                
                # Source
                row['Source'] = item.get('detail_trans_type', item.get('source', ''))
                
                # Link (use detail_url)
                row['Link'] = item.get('detail_url', '')
                
                writer.writerow(row)
        
        print(f"Handled {len(items)} data，saved to {csv_filename}")
        
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Json Parse Error: {e}")
    except KeyError as e:
        print(f"Key Error: {e}")
        print("Possible structure change in the response data.")
    except Exception as e:
        print(f"Error when dealing with data: {e}")

# Example usage
url = "https://www.28hse.com/en/epi/latest_transaction/dosearch"
for i in range(1, 6):
    time.sleep(random.uniform(0.5, 2))
    fetch_and_process_data(url,page=i)


