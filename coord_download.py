import requests

query = """
SELECT ?placeLabel ?coord WHERE {
  ?place wdt:P625 ?coord.
  ?place wdt:P31 ?type.
  VALUES ?type {
    wd:Q570116  # tourist attraction
    wd:Q839954  # historic site
    wd:Q9259    # UNESCO World Heritage Site
    wd:Q2221906 # landmark
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

url = "https://query.wikidata.org/sparql"
headers = {
    "Accept": "application/sparql-results+json"
}

response = requests.get(url, headers=headers, params={"query": query})

if response.status_code == 200:
    results = response.json()["results"]["bindings"]
    with open("coordinates.csv", "w", encoding="utf-8") as file:
        for item in results:
            coord = item["coord"]["value"]

            if coord.startswith("Point(") and coord.endswith(")"):
                coords_only = coord.replace("Point(", "").replace(")", "").strip()
                parts = coords_only.split()

                if len(parts) == 2:
                    lon, lat = parts
                    file.write(lat + "," + lon + "\n")
    print(f"✅ Готово! Сохранено {len(results)} координат в coordinates.txt")
else:
    print(f"❌ Ошибка: {response.status_code}")
