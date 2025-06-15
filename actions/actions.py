# actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

# Point this at your deployed backend
BACKEND_URL = "https://ecommerce-mini-bmvg0dtq8-movsum-aghakishiyevs-projects.vercel.app"

class ActionProductPrice(Action):
    def name(self) -> Text:
        return "action_product_price"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 1. Get the product name entity
        product_query = next(tracker.get_latest_entity_values("product"), None)
        if not product_query:
            dispatcher.utter_message(text="Sorry, I didn’t catch the product name.")
            return []

        # 2. Fetch all products and pull out the `products` array
        try:
            resp_all = requests.get(f"{BACKEND_URL}/api/products")
            resp_all.raise_for_status()
            data_all = resp_all.json()
            all_products = data_all.get("products", [])
        except Exception:
            dispatcher.utter_message(text="I’m having trouble fetching the product list right now.")
            return []

        # 3. Find a matching product by name
        matched = [
            p for p in all_products
            if product_query.lower() in p.get("name", "").lower()
        ]
        if not matched:
            dispatcher.utter_message(text=f"I couldn’t find any product matching “{product_query}.”")
            return []

        # 4. Grab its MongoDB _id
        product_meta = matched[0]
        prod_id = product_meta.get("_id") or product_meta.get("id")
        if not prod_id:
            dispatcher.utter_message(text=f"I found the product but couldn't get its ID.")
            return []

        # 6. Reply with the price
        price = product_meta.get("price")
        name = product_meta.get("name", product_query)
        dispatcher.utter_message(text=f"The price of {name} is ${price}.")
        return []


class ActionCheckAvailability(Action):
    def name(self) -> Text:
        return "action_check_availability"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        product_query = next(tracker.get_latest_entity_values("product"), None)
        if not product_query:
            dispatcher.utter_message(text="Which product are you asking about?")
            return []

        # Fetch all products
        try:
            resp_all = requests.get(f"{BACKEND_URL}/api/products")
            resp_all.raise_for_status()
            data_all = resp_all.json()
            all_products = data_all.get("products", [])
        except Exception:
            dispatcher.utter_message(text="I can’t reach the product list right now.")
            return []

        matched = [
            p for p in all_products
            if product_query.lower() in p.get("name", "").lower()
        ]
        if not matched:
            dispatcher.utter_message(text=f"No product matches “{product_query}.”")
            return []

        prod_id = matched[0].get("_id") or matched[0].get("id")
        if not prod_id:
            dispatcher.utter_message(text="I found the product but couldn't get its ID.")
            return []

        # Fetch details by ID
        try:
            resp_detail = requests.get(f"{BACKEND_URL}/api/products/{prod_id}")
            resp_detail.raise_for_status()
            product = resp_detail.json()
        except Exception:
            dispatcher.utter_message(text="I found the product but can’t get its stock status.")
            return []

        stock = product.get("stock", 0)
        name = product.get("name", product_query)
        if stock > 0:
            dispatcher.utter_message(text=f"Yes, {name} is in stock ({stock} available).")
        else:
            dispatcher.utter_message(text=f"Sorry, {name} is currently out of stock.")
        return []


class ActionHandleAttributeQuery(Action):
    def name(self) -> Text:
        return "action_handle_attribute_query"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 1. Extract entities
        product_q = next(tracker.get_latest_entity_values("product"), None)
        memory_q  = next(tracker.get_latest_entity_values("memory"), None)
        price_q   = next(tracker.get_latest_entity_values("price"), None)

        # 2. Fetch all products once
        try:
            resp = requests.get(f"{BACKEND_URL}/api/products")
            resp.raise_for_status()
            payload = resp.json()
            products = payload.get("products", [])
        except Exception:
            dispatcher.utter_message(text="Sorry, I can’t reach the product service right now.")
            return []

        # 3. Apply filters
        def matches(p):
            name = p.get("name", "").lower()
            details = p.get("details", {})
            price = p.get("price", 0)
            mem_options = p.get("available_memory", [])

            if product_q and product_q.lower() not in name:
                return False
            if memory_q:
                # match exact memory option, case-insensitive
                if not any(memory_q.lower() == m.lower() for m in mem_options):
                    return False
            if price_q:
                try:
                    threshold = float(price_q)
                    # assume user means “under threshold” unless phrasing says “above”
                    text = tracker.latest_message.get("text", "").lower()
                    if "above" in text or "over" in text:
                        if price <= threshold: return False
                    else:
                        if price >= threshold: return False
                except ValueError:
                    pass
            return True

        matched = [p for p in products if matches(p)]

        # 4. Build a response
        if not matched:
            dispatcher.utter_message(text="I couldn’t find any products matching your criteria.")
            return []

        # Limit to top 5 matches
        matched = matched[:5]
        lines = []
        for p in matched:
            name  = p.get("name")
            price = p.get("price")
            mems  = ", ".join(p.get("available_memory", []))
            lines.append(f"• {name}: ${price} – Memory options: {mems}")

        reply = "Here are some products I found:\n" + "\n".join(lines)
        dispatcher.utter_message(text=reply)
        return []