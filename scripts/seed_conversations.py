#!/usr/bin/env python3
"""
Script to seed conversation and message data into the SupaHealth database.
Run this script to add sample conversation data for testing.
"""

import sys

# Add the app directory to the Python path
sys.path.append('/app')

from app.db.session import SessionLocal
from app.models.chat.conversation import ChatConversation
from app.models.chat.message import ChatMessage
from app.models.auth.user import AuthUser
from app.core.rid import generate_rid
from app.services.auth_service import get_password_hash


def get_user_by_email(db, email: str):
    """Get an existing user by email."""
    user = db.query(AuthUser).filter(AuthUser.email == email).first()
    if not user:
        raise ValueError(f"No user found with email: {email}")
    return user


def seed_conversations():
    """Seed the database with sample conversation and message data."""
    # Hardcoded user email
    USER_EMAIL = "jake@apple.com"
    
    db = SessionLocal()
    
    try:
        # Get existing user
        user = get_user_by_email(db, USER_EMAIL)
        print(f"✅ Using existing user: {user.id} ({user.email})")
        
        # Sample conversation data
        conversations_data = [
            {
                "title": "Weight Loss Journey",
                "messages": [
                    {"role": "user", "content": "Hi! I want to lose 15 pounds in the next 3 months. Can you help me create a plan?"},
                    {"role": "assistant", "content": "I'd be happy to help you create a sustainable weight loss plan! To lose 15 pounds in 3 months, we'll need to aim for about 1.25 pounds per week, which is a healthy and achievable goal. Let's start by discussing your current lifestyle, diet, and exercise habits."},
                    {"role": "user", "content": "I currently weigh 180 pounds and I'm 5'6\". I don't exercise much, maybe a 30-minute walk once a week. My diet isn't great - lots of takeout and processed foods."},
                    {"role": "assistant", "content": "Thanks for sharing! Based on your stats, your current BMI is around 29, so losing 15 pounds would put you in a much healthier range. Let's create a plan that focuses on gradual, sustainable changes:\n\n1. **Exercise**: Start with 3-4 walks per week, gradually increasing to 5-6 days\n2. **Diet**: Focus on whole foods, reduce processed foods, and practice portion control\n3. **Hydration**: Aim for 8-10 glasses of water daily\n\nWould you like me to create a specific weekly meal plan and exercise schedule?"},
                    {"role": "user", "content": "Yes, that sounds great! I'm particularly interested in meal planning since that's where I struggle most."},
                    {"role": "assistant", "content": "Perfect! Let's start with a simple meal planning approach. I'll create a basic framework you can follow:\n\n**Breakfast**: Protein + complex carbs (e.g., Greek yogurt with berries, or eggs with whole grain toast)\n**Lunch**: Lean protein + vegetables + healthy fats (e.g., grilled chicken salad with olive oil dressing)\n**Dinner**: Similar to lunch, but slightly larger portions\n**Snacks**: Nuts, fruits, or vegetables\n\nWould you like me to create a specific 7-day meal plan with shopping list?"}
                ]
            },
            {
                "title": "Fitness Routine Planning",
                "messages": [
                    {"role": "user", "content": "I want to start a fitness routine but I'm a complete beginner. What should I focus on first?"},
                    {"role": "assistant", "content": "Great question! For beginners, I recommend starting with the fundamentals:\n\n1. **Cardio**: Start with walking, then progress to jogging\n2. **Strength Training**: Bodyweight exercises like push-ups, squats, and planks\n3. **Flexibility**: Basic stretching or yoga\n4. **Consistency**: 3-4 days per week to start\n\nWhat's your current fitness level? Do you have any physical limitations or preferences?"},
                    {"role": "user", "content": "I'm pretty sedentary - desk job, no regular exercise. No major limitations, but I'm not very strong. I prefer working out at home."},
                    {"role": "assistant", "content": "Perfect! Home workouts are ideal for beginners. Here's a simple 3-day starter routine:\n\n**Day 1 - Upper Body**:\n- 10 push-ups (knee push-ups if needed)\n- 15 arm circles\n- 30-second plank\n- 10 tricep dips (using a chair)\n\n**Day 2 - Lower Body**:\n- 15 bodyweight squats\n- 10 lunges per leg\n- 20 calf raises\n- 30-second wall sit\n\n**Day 3 - Cardio**:\n- 20-minute walk or dance\n- 5-minute stretching\n\nStart with 1 set of each exercise, rest 30-60 seconds between exercises. Sound good?"}
                ]
            },
            {
                "title": "Nutrition Questions",
                "messages": [
                    {"role": "user", "content": "I'm confused about macros. What should my daily protein, carbs, and fat intake be?"},
                    {"role": "assistant", "content": "Great question! Macro ratios depend on your goals, but here are general guidelines for a balanced diet:\n\n**Protein**: 0.8-1.2g per pound of body weight\n- For you (180 lbs): 144-216g daily\n- Sources: chicken, fish, beans, Greek yogurt\n\n**Carbs**: 45-65% of total calories\n- Focus on complex carbs: whole grains, fruits, vegetables\n- Limit simple carbs: sugar, white bread, processed foods\n\n**Fat**: 20-35% of total calories\n- Healthy fats: olive oil, nuts, avocado, fatty fish\n- Limit saturated and trans fats\n\nWhat's your primary goal - weight loss, muscle gain, or maintenance?"},
                    {"role": "user", "content": "Weight loss is my main goal. I want to lose about 20 pounds total."},
                    {"role": "assistant", "content": "For weight loss, I'd recommend:\n\n**Protein**: 1g per pound (180g) - helps preserve muscle during weight loss\n**Carbs**: 40-50% of calories - focus on timing around workouts\n**Fat**: 25-30% of calories - keeps you satisfied\n\n**Calorie Target**: Start with 1,500-1,700 calories daily\n- Track for 2 weeks, adjust based on results\n- Aim for 1-2 pounds loss per week\n\n**Pro Tips**:\n- Eat protein with every meal\n- Load up on vegetables (low calorie, high volume)\n- Drink water before meals\n- Plan meals in advance\n\nWould you like me to create a sample day's meal plan with these macros?"}
                ]
            }
        ]
        
        # Create conversations and messages
        for conv_data in conversations_data:
            # Create conversation
            conversation_id = generate_rid("chat", "conversation")
            conversation = ChatConversation(
                id=conversation_id,
                title=conv_data["title"],
                user_id=user.id,
                status="active"
            )
            db.add(conversation)
            db.flush()  # Get the ID without committing
            
            print(f"✅ Created conversation: {conv_data['title']}")
            
            # Create messages for this conversation
            for i, msg_data in enumerate(conv_data["messages"]):
                message_id = generate_rid("chat", "message")
                message = ChatMessage(
                    id=message_id,
                    conversation_id=conversation_id,
                    role=msg_data["role"],
                    content=msg_data["content"],
                    user_id=user.id
                )
                db.add(message)
                print(f"  📝 Added {msg_data['role']} message: {msg_data['content'][:50]}...")
            
            print()  # Empty line for readability
        
        # Commit all changes
        db.commit()
        print("🎉 Successfully seeded conversation and message data!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Starting conversation data seeding...")
    seed_conversations()
    print("✅ Seeding complete!")
