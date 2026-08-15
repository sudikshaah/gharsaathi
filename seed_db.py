from app import create_app, db
from app.models.user import User
from app.models.profiles import Employer, Helper
from app.models.job import Skill, Job
from app.models.verification import VerificationRequest
from datetime import time, date, datetime

def seed():
    # Initialize application context
    app = create_app('development')
    with app.app_context():
        # Clear existing tables to start fresh
        db.drop_all()
        db.create_all()
        
        print("Creating Skills Lookup Table...")
        skills_data = [
            ('cook', 'North Indian Cooking'),
            ('cook', 'Baking & Pastry'),
            ('cook', 'Continental Cuisines'),
            ('maid', 'Floor Mopping & Sweeping'),
            ('maid', 'Utensil Washing'),
            ('maid', 'Ironing & Laundry'),
            ('driver', 'Manual Transmission Driving'),
            ('driver', 'Automatic Transmission Driving'),
            ('babysitter', 'Infant Care & Feeding'),
            ('caregiver', 'Elderly Patient Assistance')
        ]
        
        skills_map = {}
        for category, name in skills_data:
            skill = Skill(category=category, skill_name=name)
            db.session.add(skill)
            skills_map[name] = skill
        db.session.commit()

        print("Creating User Accounts...")
        # 1. Admin
        admin_user = User(phone_number="12345678", role="admin")
        admin_user.password = "admin123"
        db.session.add(admin_user)

        # 2. Employer
        employer_user = User(phone_number="87654321", role="employer")
        employer_user.password = "employer123"
        db.session.add(employer_user)

        # 3. Helper 1 (Sita - Cook, local)
        helper_user1 = User(phone_number="11112222", role="helper")
        helper_user1.password = "helper123"
        db.session.add(helper_user1)

        # 4. Helper 2 (Ramesh - Driver, far away)
        helper_user2 = User(phone_number="33334444", role="helper")
        helper_user2.password = "helper123"
        db.session.add(helper_user2)
        
        db.session.commit()

        print("Creating Employer Profile...")
        employer = Employer(
            user_id=employer_user.id,
            family_name="Sharma Family",
            address_line1="C-42, Vasant Kunj",
            address_line2="Sector B",
            city="New Delhi",
            state="Delhi",
            pincode="110070",
            latitude=28.5398,
            longitude=77.1554,
            verified_status="verified"
        )
        db.session.add(employer)
        db.session.commit()

        print("Creating Helper Profiles...")
        # Helper 1 (Local, Cook, Verified, 5 yrs exp, expected 12k)
        helper1 = Helper(
            user_id=helper_user1.id,
            full_name="Sita Ram",
            age=34,
            gender="female",
            religion="Hindu",
            languages_spoken="Hindi, Panjabi",
            experience_years=5,
            expected_salary=12000.00,
            work_type="live_out",
            location_pincode="110070",  # Same pincode!
            latitude=28.5412,           # ~150 meters away!
            longitude=77.1560,
            is_vaccinated=True,
            is_police_verified=True,
            is_background_checked=True,
            overall_rating=4.8
        )
        # Associate cook skills
        helper1.skills.append(skills_map['North Indian Cooking'])
        helper1.skills.append(skills_map['Utensil Washing'])
        db.session.add(helper1)

        # Helper 2 (Far, Driver, Unverified, 2 yrs exp, expected 18k)
        helper2 = Helper(
            user_id=helper_user2.id,
            full_name="Ramesh Singh",
            age=29,
            gender="male",
            religion="Hindu",
            languages_spoken="Hindi, English",
            experience_years=2,
            expected_salary=18000.00,
            work_type="live_in",
            location_pincode="110001",  # Far pincode
            latitude=28.6139,           # Far coordinates
            longitude=77.2090,
            is_vaccinated=True,
            is_police_verified=False,
            is_background_checked=False,
            overall_rating=4.0
        )
        helper2.skills.append(skills_map['Manual Transmission Driving'])
        db.session.add(helper2)
        
        db.session.commit()

        # Add dummy verification request for Sita (Approved by Admin)
        doc1 = VerificationRequest(
            user_id=helper_user1.id,
            document_type='aadhaar',
            document_path='/static/uploads/dummy_aadhaar.png',
            ocr_name='Sita Ram',
            ocr_document_number='9876-5432-1111',
            ocr_dob='1992-05-15',
            status='Approved',
            reviewed_by=admin_user.id,
            reviewed_at=datetime.utcnow(),
            remarks='Aadhaar matching verification OK'
        )
        db.session.add(doc1)
        
        # Add dummy verification request for Ramesh (Pending Review)
        doc2 = VerificationRequest(
            user_id=helper_user2.id,
            document_type='police_clearance',
            document_path='/static/uploads/dummy_pcc.pdf',
            ocr_name='Ramesh Singh',
            ocr_document_number='PCC-2026-880022',
            ocr_dob='1997-08-20',
            status='Pending'
        )
        db.session.add(doc2)
        
        db.session.commit()

        print("Creating Sample Job Listings...")
        # Job 1 (Looking for Cook, salary 14k, requires 3 yrs exp, pincode 110070)
        job1 = Job(
            employer_id=employer.id,
            title="Need Daily Cook for Family of 4",
            category="cook",
            salary_offered=14000.00,
            working_hours_start=time(7, 30),
            working_hours_end=time(10, 30),
            gender_preference="female",
            language_requirements="Hindi",
            experience_required_years=3,
            accommodation_provided=False,
            food_provided=True,
            weekly_off_day="Sunday",
            address_pincode="110070",
            latitude=28.5398,
            longitude=77.1554,
            description="Looking for an experienced female cook for preparing breakfast and lunch daily. Punjabi cooking preference."
        )
        job1.skills.append(skills_map['North Indian Cooking'])
        db.session.add(job1)
        db.session.commit()

        print("Database Seeded Successfully!")
        print("\nTest logins:")
        print("  - Admin: phone 12345678, password admin123")
        print("  - Employer: phone 87654321, password employer123")
        print("  - Helper 1 (Sita): phone 11112222, password helper123")
        print("  - Helper 2 (Ramesh): phone 33334444, password helper123")

if __name__ == '__main__':
    seed()
