
import pytest
from app.services.match_engine import calculate_match_score, haversine_distance

class MockSkill:
    def __init__(self, name):
        self.skill_name = name

class MockDoc:
    def __init__(self, doc_type, status):
        self.document_type = doc_type
        self.status = status


class MockUser:
    def __init__(self, docs):
        self.verification_requests = MockCollection(docs)

class MockCollection:
    def __init__(self, items):
        self.items = items
    def filter_by(self, **kwargs):
        filtered = self.items
        for key, val in kwargs.items():
            filtered = [item for item in filtered if getattr(item, key) == val]
        return MockCollection(filtered)
    def first(self):
        return self.items[0] if self.items else None

class MockJob:
    def __init__(self, offered, exp_req, pincode, lat=None, lon=None, skills=None):
        self.salary_offered = offered
        self.experience_required_years = exp_req
        self.address_pincode = pincode
        self.latitude = lat
        self.longitude = lon
        self.skills = [MockSkill(s) for s in (skills or [])]

class MockHelper:
    def __init__(self, expected, exp, pincode, lat=None, lon=None, skills=None, docs=None, police=False, bg=False):
        self.expected_salary = expected
        self.experience_years = exp
        self.location_pincode = pincode
        self.latitude = lat
        self.longitude = lon
        self.skills = [MockSkill(s) for s in (skills or [])]
        self.user = MockUser([MockDoc(d[0], d[1]) for d in (docs or [])])
        self.is_police_verified = police
        self.is_background_checked = bg

def test_haversine_distance():
    # Coordinates for Delhi Center to Noida Center (approx 16-17 km)
    dist = haversine_distance(28.6139, 77.2090, 28.5355, 77.3910)
    assert dist is not None
    assert 15.0 < dist < 25.0
    
    # Exactly same point distance should be 0
    assert haversine_distance(28.6139, 77.2090, 28.6139, 77.2090) == 0.0

def test_exact_match():
    # Perfect match: identical location, lower salary expected, matches all skills, meets exp, verified.
    job = MockJob(
        offered=15000.0, 
        exp_req=3, 
        pincode="110070", 
        lat=28.5398, 
        lon=77.1554, 
        skills=["Cooking", "Cleaning"]
    )
    helper = MockHelper(
        expected=12000.0, 
        exp=5, 
        pincode="110070", 
        lat=28.5400, 
        lon=77.1555, 
        skills=["Cooking", "Cleaning"],
        docs=[("aadhaar", "Approved"), ("police_clearance", "Approved")]
    )
    
    score = calculate_match_score(job, helper)
    # Proximity <= 1km: 100% -> weighted 30%
    # Salary expected <= offered: 100% -> weighted 25%
    # Skills match: 100% -> weighted 20%
    # Exp >= req: 100% -> weighted 15%
    # Verified (Both): 100% -> weighted 10%
    # Total: 100%
    assert score == 100.0

def test_no_geo_pincode_fallback():
    # If coordinates are missing, pincodes match exactly
    job = MockJob(offered=10000.0, exp_req=0, pincode="110001", skills=[])
    helper = MockHelper(expected=10000.0, exp=0, pincode="110001", skills=[])
    
    # Location: identical pincode (100% -> 30% weight)
    # Salary: expected == offered (100% -> 25% weight)
    # Skills: both empty (100% -> 20% weight)
    # Experience: req=0 (100% -> 15% weight)
    # Verification: unverified (0% -> 0% weight)
    # Expected weighted: 30 + 25 + 20 + 15 = 90%
    assert calculate_match_score(job, helper) == 90.0
