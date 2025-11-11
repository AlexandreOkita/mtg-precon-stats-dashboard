import requests
import json

class ScryfallAPI:
    BASE_URL = "https://api.scryfall.com"

    def get_card_by_name(self, name): # type: ignore

        response = requests.get(f"{self.BASE_URL}/cards/named", params={"exact": name}) # type: ignore
        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    def scryfall_oracle_search(self, query): # type: ignore

        response = requests.get(f"{self.BASE_URL}/cards/search", params={"q": query}) # type: ignore
        if response.status_code == 200:
            return response.json()
        else:
            return None
        
if __name__ == "__main__":
    api = ScryfallAPI()
    query = "set:eoc otag:spot_removal"
    card_data = api.scryfall_oracle_search(query) # type: ignore
    print(json.dumps(card_data, indent=2)) # type: ignore
