import json
import random
import uuid
from datetime import datetime, timedelta
import string

# Agent names with fixed UUIDs
agents = {
    "Sarah": str(uuid.uuid4()),
    "James": str(uuid.uuid4()),
    "Emma": str(uuid.uuid4()),
    "Michael": str(uuid.uuid4()),
    "Jessica": str(uuid.uuid4()),
    "David": str(uuid.uuid4()),
    "Sophie": str(uuid.uuid4()),
    "Ryan": str(uuid.uuid4()),
    "Olivia": str(uuid.uuid4()),
    "Nathan": str(uuid.uuid4())
}

# Customer issue templates
billing_issues = [
    "Hi, I just got my bill and theres a ${amount} charge I don't recognise???",
    "why is my bill so high this month? its usually around ${usual} but now its ${high}",
    "I paid my bill last week but got a overdue notice today",
    "can someone explain these extra charges on my bill please",
    "I think ive been double charged this month"
]

roaming_issues = [
    "Hi, I'm going to {destination} next week and need help with roaming",
    "how do I activate international roaming? flying to {destination} tomorrow",
    "what are the roaming rates for {destination}?",
    "my roaming isn't working and im in {destination} right now!!",
    "I want to add a travel pack for my trip to {destination}"
]

cancellation_issues = [
    "I want to cancel my service",
    "how do I port my number to another provider?",
    "whats the cancellation fee if I leave now?",
    "im not happy with the service and want to cancel",
    "moving overseas and need to cancel my plan"
]

technical_issues = [
    "my phone has no signal since this morning",
    "internet is really slow lately, whats going on?",
    "cant make calls but can receive them, help!",
    "my data isn't working properly",
    "phone keeps dropping out during calls"
]

plan_change_issues = [
    "I want to upgrade to a bigger data plan",
    "can I downgrade my plan? dont need this much data",
    "what plans do you have with more international minutes?",
    "I need to add another line to my account",
    "want to change from prepaid to postpaid"
]

new_service_issues = [
    "what new phone plans do you have?",
    "do you have any family plan deals?",
    "I'm interested in getting a new phone with a plan",
    "what data packs can I add to my current plan?",
    "do you have any student discounts?"
]

# Agent responses
agent_greetings = [
    "Hello! I'm {agent_name} from customer service. I'd be happy to help you with {issue_type}. Let me pull up your account details.",
    "Hi there! I'm {agent_name} and I'll assist you today. I understand you're having {issue_type}. Let me look into this for you.",
    "Good {time_of_day}! I'm {agent_name}. Thanks for contacting us. I see you need help with {issue_type}. Let me check your account."
]

# Destinations for roaming
destinations = ["Bali", "Thailand", "Singapore", "New Zealand", "Japan", "USA", "UK", "Vietnam", "Malaysia", "India"]

def generate_conversation_messages(contact_id, chat_id, phone_number, customer_id, agent_name, agent_id, start_date, conv_type):
    messages = []
    time_shift = 0
    message_num = 1
    
    # Generate opening customer message
    if conv_type == 'billing':
        opening = random.choice(billing_issues)
        opening = opening.replace("{amount}", str(random.randint(50, 300)))
        opening = opening.replace("{usual}", str(random.randint(40, 80)))
        opening = opening.replace("{high}", str(random.randint(100, 250)))
        issue_desc = "your billing inquiry"
    elif conv_type == 'roaming':
        opening = random.choice(roaming_issues)
        opening = opening.replace("{destination}", random.choice(destinations))
        issue_desc = "your international roaming query"
    elif conv_type == 'cancellation':
        opening = random.choice(cancellation_issues)
        issue_desc = "your cancellation request"
    elif conv_type == 'technical':
        opening = random.choice(technical_issues)
        issue_desc = "your technical issue"
    elif conv_type == 'plan_change':
        opening = random.choice(plan_change_issues)
        issue_desc = "your plan change request"
    else:  # new_service
        opening = random.choice(new_service_issues)
        issue_desc = "your inquiry about our services"
    
    # First customer message
    messages.append({
        "contact_id": contact_id,
        "start_date": start_date.isoformat() + "+10:00",
        "end_date": "",  # Will be filled later
        "chat_id": chat_id,
        "phone_number": phone_number,
        "chat_user_id": customer_id,
        "chat_text": opening,
        "chat_time_shift": time_shift,
        "chat_user_type": "customer",
        "message_number": message_num
    })
    
    # Agent response
    time_shift += random.randint(30, 90)
    message_num += 1
    
    hour = start_date.hour
    time_of_day = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
    
    greeting = random.choice(agent_greetings)
    greeting = greeting.replace("{agent_name}", agent_name)
    greeting = greeting.replace("{issue_type}", issue_desc)
    greeting = greeting.replace("{time_of_day}", time_of_day)
    
    messages.append({
        "contact_id": contact_id,
        "start_date": start_date.isoformat() + "+10:00",
        "end_date": "",
        "chat_id": chat_id,
        "phone_number": phone_number,
        "chat_user_id": agent_id,
        "chat_text": greeting,
        "chat_time_shift": time_shift,
        "chat_user_type": "agent",
        "message_number": message_num
    })
    
    # Generate rest of conversation
    conv_length = random.randint(6, 20)
    resolved = random.choice([True, False])
    
    # Continue conversation based on type
    if conv_type == 'billing':
        # Customer provides info
        time_shift += random.randint(15, 60)
        message_num += 1
        messages.append({
            "contact_id": contact_id,
            "start_date": start_date.isoformat() + "+10:00",
            "end_date": "",
            "chat_id": chat_id,
            "phone_number": phone_number,
            "chat_user_id": customer_id,
            "chat_text": "its account " + str(random.randint(1000, 9999)),
            "chat_time_shift": time_shift,
            "chat_user_type": "customer",
            "message_number": message_num
        })
        
        # Agent investigates
        time_shift += random.randint(45, 120)
        message_num += 1
        messages.append({
            "contact_id": contact_id,
            "start_date": start_date.isoformat() + "+10:00",
            "end_date": "",
            "chat_id": chat_id,
            "phone_number": phone_number,
            "chat_user_id": agent_id,
            "chat_text": "Thank you! I can see your account now. Let me investigate this charge for you. One moment please while I check the details.",
            "chat_time_shift": time_shift,
            "chat_user_type": "agent",
            "message_number": message_num
        })
        
        # Agent explains
        time_shift += random.randint(60, 120)
        message_num += 1
        if resolved:
            messages.append({
                "contact_id": contact_id,
                "start_date": start_date.isoformat() + "+10:00",
                "end_date": "",
                "chat_id": chat_id,
                "phone_number": phone_number,
                "chat_user_id": agent_id,
                "chat_text": "I've found the charge. It appears to be for international calls made on January 5th to the UK. The total duration was 45 minutes at $3.33 per minute. Would you like me to email you the detailed breakdown?",
                "chat_time_shift": time_shift,
                "chat_user_type": "agent",
                "message_number": message_num
            })
        else:
            messages.append({
                "contact_id": contact_id,
                "start_date": start_date.isoformat() + "+10:00",
                "end_date": "",
                "chat_id": chat_id,
                "phone_number": phone_number,
                "chat_user_id": agent_id,
                "chat_text": "I can see the charge but I'll need to escalate this to our billing team for further investigation. They'll contact you within 24-48 hours. Is that okay?",
                "chat_time_shift": time_shift,
                "chat_user_type": "agent",
                "message_number": message_num
            })
    
    elif conv_type == 'roaming':
        # Similar pattern for roaming conversations
        time_shift += random.randint(15, 60)
        message_num += 1
        messages.append({
            "contact_id": contact_id,
            "start_date": start_date.isoformat() + "+10:00",
            "end_date": "",
            "chat_id": chat_id,
            "phone_number": phone_number,
            "chat_user_id": customer_id,
            "chat_text": "yes please, I leave in " + str(random.randint(2, 7)) + " days",
            "chat_time_shift": time_shift,
            "chat_user_type": "customer",
            "message_number": message_num
        })
        
        time_shift += random.randint(30, 90)
        message_num += 1
        messages.append({
            "contact_id": contact_id,
            "start_date": start_date.isoformat() + "+10:00",
            "end_date": "",
            "chat_id": chat_id,
            "phone_number": phone_number,
            "chat_user_id": agent_id,
            "chat_text": "I can definitely help you set up roaming. We have a few options available. Our daily roaming pack is $5/day for 200MB, or you can use pay-as-you-go at $3/MB. Which would you prefer?",
            "chat_time_shift": time_shift,
            "chat_user_type": "agent",
            "message_number": message_num
        })
    
    # Add remaining messages to reach target length
    while message_num < conv_length:
        time_shift += random.randint(15, 90)
        message_num += 1
        
        if message_num % 2 == 1:  # Customer message
            customer_responses = [
                "ok thanks",
                "that sounds good",
                "can you explain more?",
                "I'm not sure about that",
                "yes please",
                "no that's not what I want",
                "how much will that cost?",
                "when will it be activated?"
            ]
            messages.append({
                "contact_id": contact_id,
                "start_date": start_date.isoformat() + "+10:00",
                "end_date": "",
                "chat_id": chat_id,
                "phone_number": phone_number,
                "chat_user_id": customer_id,
                "chat_text": random.choice(customer_responses),
                "chat_time_shift": time_shift,
                "chat_user_type": "customer",
                "message_number": message_num
            })
        else:  # Agent message
            agent_responses = [
                "I understand your concern. Let me see what other options we have.",
                "That's a great question. Let me clarify that for you.",
                "I've processed that request for you. It will be active within the next hour.",
                "Is there anything else I can help you with today?",
                "I've added a note to your account about this issue.",
                "Let me check if there are any current promotions that might help."
            ]
            messages.append({
                "contact_id": contact_id,
                "start_date": start_date.isoformat() + "+10:00",
                "end_date": "",
                "chat_id": chat_id,
                "phone_number": phone_number,
                "chat_user_id": agent_id,
                "chat_text": random.choice(agent_responses),
                "chat_time_shift": time_shift,
                "chat_user_type": "agent",
                "message_number": message_num
            })
    
    # Calculate end time
    end_date = start_date + timedelta(seconds=time_shift)
    
    # Update all messages with end_date
    for msg in messages:
        msg["end_date"] = end_date.isoformat() + "+10:00"
    
    return messages

# Generate all conversations
all_messages = []

for i in range(1000):
    # Generate unique IDs for this conversation
    contact_id = str(uuid.uuid4())
    chat_id = str(uuid.uuid4())
    customer_id = str(uuid.uuid4())
    
    # Choose a random agent for this conversation
    agent_name = random.choice(list(agents.keys()))
    agent_id = agents[agent_name]
    
    # Generate phone number
    phone_number = f"04{random.randint(10000000, 99999999)}"
    
    # Generate start timestamp
    start_date = datetime(2024, random.randint(1, 3), random.randint(1, 28), 
                         random.randint(8, 20), random.randint(0, 59), 0)
    
    # Choose conversation type based on distribution
    conv_type = random.choices(
        ['billing', 'roaming', 'cancellation', 'technical', 'plan_change', 'new_service'],
        weights=[25, 20, 15, 15, 15, 10]
    )[0]
    
    # Generate messages for this conversation
    conversation_messages = generate_conversation_messages(
        contact_id, chat_id, phone_number, customer_id, 
        agent_name, agent_id, start_date, conv_type
    )
    
    all_messages.extend(conversation_messages)

# Save to JSON file
with open('customer_service_chats.json', 'w') as f:
    json.dump(all_messages, f, indent=2)

print(f"Generated {len(all_messages)} messages across 1000 conversations")
print("Data saved to customer_service_chats.json")
