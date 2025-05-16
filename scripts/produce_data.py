import time
import json
import random
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer

KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "orders"

PRODUCER = KafkaProducer(bootstrap_servers=KAFKA_BROKER, value_serializer=lambda x:json.dumps(x).encode('utf-8'))

FAKER = Faker()

def generate_data():
    """Generate simulated user data"""
    data = {
        "order_id": FAKER.uuid4(),
        "user_id": random.randint(1000, 9999),
        "item": FAKER.word(),
        "quantity": random.randint(1, 10),
        "unit_price": round(random.uniform(10, 1000), 3),
        "total_amount": 0, 
        "payment_method": random.choice(["credit_card", "paypal", "cash"]),
        "location": {
            "city": FAKER.city(),
            "country": FAKER.country()
        },
        "event_time": datetime.now().isoformat()
    }

    data["total_amount"] = round(data["quantity"] * data["unit_price"], 3)
    
    print(data)
    
    return data

def main():
    try:
        while True:
            data = generate_data()
            
            PRODUCER.send(topic=KAFKA_TOPIC, value=data)
            PRODUCER.flush()
            
            time.sleep(random.randint(10, 30))
    except KeyboardInterrupt:
        print("STOPPING PRODUCER ...")
    finally:
        print("STOPPED PRODUCER")

if __name__ == "__main__":
    main()