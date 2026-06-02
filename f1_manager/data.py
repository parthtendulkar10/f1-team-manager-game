"""Template data for the F1 manager game."""

MANUFACTURERS = [
    {"name": "Ferrari", "backing": 120_000_000, "marketing": 75},
    {"name": "Aston Martin", "backing": 95_000_000, "marketing": 68},
    {"name": "Renault", "backing": 100_000_000, "marketing": 60},
    {"name": "Porsche", "backing": 90_000_000, "marketing": 65},
]

TEAM_PRINCIPALS = [
    {"name": "Mika Salo", "background": "Ex-F1 driver", "stats": {"strategy": 78, "development": 65, "driver_management": 72, "marketing": 50}},
    {"name": "Elena Rossi", "background": "Senior race strategist", "stats": {"strategy": 84, "development": 76, "driver_management": 60, "marketing": 52}},
    {"name": "Hector Alvarez", "background": "Championship football manager", "stats": {"strategy": 66, "development": 54, "driver_management": 80, "marketing": 79}},
    {"name": "Priya Shah", "background": "Former chief engineer", "stats": {"strategy": 74, "development": 88, "driver_management": 58, "marketing": 48}},
]

DRIVER_POOL_STARTER = [
    {"name": "Liam Costa", "tier": "F2", "skill": 67, "market_value": 4_000_000},
    {"name": "Eva Moreau", "tier": "F2", "skill": 70, "market_value": 5_200_000},
    {"name": "Noah Redding", "tier": "Retired Returnee", "skill": 69, "market_value": 6_000_000},
    {"name": "Sofia Iliev", "tier": "F2", "skill": 65, "market_value": 3_500_000},
]

DRIVER_POOL_UNLOCKED = [
    {"name": "Marco Bellini", "tier": "Established F1", "skill": 80, "market_value": 14_000_000},
    {"name": "Jun Park", "tier": "Established F1", "skill": 83, "market_value": 16_500_000},
    {"name": "Aleksei Volkov", "tier": "Top Driver", "skill": 87, "market_value": 22_000_000},
]

STAFF_TEMPLATES = [
    {"name": "Chief Aerodynamicist", "skill": 73},
    {"name": "Head of Strategy", "skill": 76},
    {"name": "Performance Engineer", "skill": 70},
]

SPONSOR_TYPES = ["Tech Conglomerate", "Luxury Watch Brand", "Energy Drink", "Fintech Firm", "Global Logistics"]
