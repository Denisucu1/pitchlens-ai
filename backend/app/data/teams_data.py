from typing import Tuple
from app.data.models import TeamProfile, PlayerProfile, PitchCoordinates

def get_premier_teams() -> Tuple[TeamProfile, TeamProfile]:
    """
    Returns two highly realistic, synthetic Premier League teams with full squad profiles
    and real-time tracking attributes.
    """
    home_team = TeamProfile(
        id="team_cannons",
        name="London Cannons",
        short_name="CAN",
        primary_color="#EF0107",  # Red
        secondary_color="#FFFFFF",
        formation="4-3-3",
        manager="Mikel Alvez",
        tactical_style="High-Press Positional Play",
        players=[
            PlayerProfile(id="can_01", name="David Ramos", number=1, position="GK", team_id="team_cannons", pace=68, stamina=80, passing_skill=82, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="can_04", name="Ben Whitefield", number=4, position="RB", team_id="team_cannons", pace=81, stamina=86, passing_skill=84, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="can_02", name="William Salinas", number=2, position="CB", team_id="team_cannons", pace=83, stamina=88, passing_skill=80, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="can_06", name="Gabriel Santos", number=6, position="CB", team_id="team_cannons", pace=80, stamina=90, passing_skill=78, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="can_12", name="Jurrien Timmons", number=12, position="LB", team_id="team_cannons", pace=84, stamina=85, passing_skill=83, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="can_05", name="Thomas Parton", number=5, position="CDM", team_id="team_cannons", pace=74, stamina=89, passing_skill=86, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="can_41", name="Declan Brooks", number=41, position="CM", team_id="team_cannons", pace=82, stamina=96, passing_skill=88, current_coords=PitchCoordinates(x=45.0, y=35.0)),
            PlayerProfile(id="can_08", name="Martin Osorio", number=8, position="CAM", team_id="team_cannons", pace=79, stamina=92, passing_skill=94, current_coords=PitchCoordinates(x=58.0, y=60.0)),
            PlayerProfile(id="can_07", name="Bukayo Smith", number=7, position="RW", team_id="team_cannons", pace=89, stamina=91, passing_skill=89, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="can_11", name="Gabriel Martin", number=11, position="LW", team_id="team_cannons", pace=93, stamina=88, passing_skill=82, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="can_29", name="Kai Haverton", number=29, position="ST", team_id="team_cannons", pace=84, stamina=90, passing_skill=85, current_coords=PitchCoordinates(x=72.0, y=50.0))
        ]
    )

    away_team = TeamProfile(
        id="team_titans",
        name="Manchester Titans",
        short_name="TIT",
        primary_color="#6CABDD",  # Sky Blue
        secondary_color="#1C2C5B",
        formation="4-2-3-1",
        manager="Pep Quintana",
        tactical_style="Fluid Spatial Dominance",
        players=[
            PlayerProfile(id="tit_31", name="Edson Moises", number=31, position="GK", team_id="team_titans", pace=70, stamina=82, passing_skill=89, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="tit_02", name="Kyle Walken", number=2, position="RB", team_id="team_titans", pace=92, stamina=88, passing_skill=79, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="tit_03", name="Ruben Diaspro", number=3, position="CB", team_id="team_titans", pace=79, stamina=90, passing_skill=85, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="tit_25", name="Manuel Akanji", number=25, position="CB", team_id="team_titans", pace=82, stamina=87, passing_skill=82, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="tit_24", name="Josko Gvardiol", number=24, position="LB", team_id="team_titans", pace=85, stamina=89, passing_skill=86, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="tit_16", name="Rodrigo Cascante", number=16, position="CDM", team_id="team_titans", pace=76, stamina=94, passing_skill=92, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="tit_08", name="Mateo Kovacic", number=8, position="CM", team_id="team_titans", pace=81, stamina=88, passing_skill=89, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="tit_17", name="Kevin De Bruyn", number=17, position="CAM", team_id="team_titans", pace=80, stamina=89, passing_skill=97, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="tit_47", name="Phil Folden", number=47, position="RW", team_id="team_titans", pace=88, stamina=90, passing_skill=90, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="tit_10", name="Jack Grealish", number=10, position="LW", team_id="team_titans", pace=83, stamina=86, passing_skill=88, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="tit_09", name="Erling Holand", number=9, position="ST", team_id="team_titans", pace=92, stamina=92, passing_skill=78, current_coords=PitchCoordinates(x=35.0, y=50.0))
        ]
    )

    return home_team, away_team
