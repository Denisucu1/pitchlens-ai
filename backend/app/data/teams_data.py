from typing import List, Dict
from app.data.models import TeamProfile, PlayerProfile, PitchCoordinates

def get_premier_league_teams() -> Dict[str, TeamProfile]:
    """
    Returns authentic Premier League clubs with real rosters, formations,
    tactical profiles, and accurate player attributes.
    """
    teams = {}

    # 1. ARSENAL
    teams["arsenal"] = TeamProfile(
        id="arsenal",
        name="Arsenal",
        short_name="ARS",
        primary_color="#EF0107",  # Red
        secondary_color="#FFFFFF",
        formation="4-3-3",
        manager="Mikel Arteta",
        tactical_style="High-Press Positional Play",
        players=[
            PlayerProfile(id="ars_22", name="David Raya", number=22, position="GK", team_id="arsenal", pace=68, stamina=80, passing_skill=88, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="ars_04", name="Ben White", number=4, position="RB", team_id="arsenal", pace=81, stamina=86, passing_skill=84, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="ars_02", name="William Saliba", number=2, position="CB", team_id="arsenal", pace=84, stamina=89, passing_skill=82, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="ars_06", name="Gabriel Magalhaes", number=6, position="CB", team_id="arsenal", pace=81, stamina=90, passing_skill=79, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="ars_12", name="Jurrien Timber", number=12, position="LB", team_id="arsenal", pace=84, stamina=86, passing_skill=83, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="ars_05", name="Thomas Partey", number=5, position="CDM", team_id="arsenal", pace=73, stamina=88, passing_skill=87, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="ars_41", name="Declan Rice", number=41, position="CM", team_id="arsenal", pace=82, stamina=97, passing_skill=89, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="ars_08", name="Martin Odegaard", number=8, position="CAM", team_id="arsenal", pace=80, stamina=92, passing_skill=95, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="ars_07", name="Bukayo Saka", number=7, position="RW", team_id="arsenal", pace=88, stamina=92, passing_skill=90, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="ars_11", name="Gabriel Martinelli", number=11, position="LW", team_id="arsenal", pace=93, stamina=89, passing_skill=83, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="ars_29", name="Kai Havertz", number=29, position="ST", team_id="arsenal", pace=83, stamina=91, passing_skill=85, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    # 2. MANCHESTER CITY
    teams["mancity"] = TeamProfile(
        id="mancity",
        name="Manchester City",
        short_name="MCI",
        primary_color="#6CABDD",  # Sky Blue
        secondary_color="#1C2C5B",
        formation="4-2-3-1",
        manager="Pep Guardiola",
        tactical_style="Fluid Spatial Dominance",
        players=[
            PlayerProfile(id="mci_31", name="Ederson", number=31, position="GK", team_id="mancity", pace=70, stamina=82, passing_skill=92, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="mci_02", name="Kyle Walker", number=2, position="RB", team_id="mancity", pace=92, stamina=88, passing_skill=79, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="mci_03", name="Ruben Dias", number=3, position="CB", team_id="mancity", pace=79, stamina=90, passing_skill=85, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="mci_25", name="Manuel Akanji", number=25, position="CB", team_id="mancity", pace=82, stamina=87, passing_skill=83, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="mci_24", name="Josko Gvardiol", number=24, position="LB", team_id="mancity", pace=85, stamina=89, passing_skill=87, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="mci_16", name="Rodri", number=16, position="CDM", team_id="mancity", pace=76, stamina=95, passing_skill=94, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="mci_08", name="Mateo Kovacic", number=8, position="CM", team_id="mancity", pace=81, stamina=88, passing_skill=89, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="mci_17", name="Kevin De Bruyne", number=17, position="CAM", team_id="mancity", pace=80, stamina=89, passing_skill=97, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="mci_47", name="Phil Foden", number=47, position="RW", team_id="mancity", pace=88, stamina=90, passing_skill=91, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="mci_10", name="Jack Grealish", number=10, position="LW", team_id="mancity", pace=83, stamina=86, passing_skill=88, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="mci_09", name="Erling Haaland", number=9, position="ST", team_id="mancity", pace=93, stamina=92, passing_skill=79, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    # 3. LIVERPOOL
    teams["liverpool"] = TeamProfile(
        id="liverpool",
        name="Liverpool",
        short_name="LIV",
        primary_color="#C8102E",  # Liverpool Red
        secondary_color="#00B2A9",
        formation="4-3-3",
        manager="Arne Slot",
        tactical_style="High-Intensity Heavy Metal Pressing",
        players=[
            PlayerProfile(id="liv_01", name="Alisson Becker", number=1, position="GK", team_id="liverpool", pace=69, stamina=84, passing_skill=87, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="liv_66", name="Trent Alexander-Arnold", number=66, position="RB", team_id="liverpool", pace=82, stamina=88, passing_skill=96, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="liv_05", name="Ibrahima Konate", number=5, position="CB", team_id="liverpool", pace=84, stamina=88, passing_skill=78, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="liv_04", name="Virgil van Dijk", number=4, position="CB", team_id="liverpool", pace=82, stamina=91, passing_skill=86, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="liv_26", name="Andrew Robertson", number=26, position="LB", team_id="liverpool", pace=85, stamina=94, passing_skill=83, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="liv_38", name="Ryan Gravenberch", number=38, position="CDM", team_id="liverpool", pace=82, stamina=90, passing_skill=88, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="liv_10", name="Alexis Mac Allister", number=10, position="CM", team_id="liverpool", pace=78, stamina=92, passing_skill=91, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="liv_08", name="Dominik Szoboszlai", number=8, position="CAM", team_id="liverpool", pace=86, stamina=94, passing_skill=89, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="liv_11", name="Mohamed Salah", number=11, position="RW", team_id="liverpool", pace=90, stamina=91, passing_skill=88, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="liv_07", name="Luis Diaz", number=7, position="LW", team_id="liverpool", pace=92, stamina=90, passing_skill=83, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="liv_09", name="Darwin Nunez", number=9, position="ST", team_id="liverpool", pace=92, stamina=89, passing_skill=78, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    # 4. CHELSEA
    teams["chelsea"] = TeamProfile(
        id="chelsea",
        name="Chelsea",
        short_name="CHE",
        primary_color="#034694",  # Royal Blue
        secondary_color="#FFFFFF",
        formation="4-2-3-1",
        manager="Enzo Maresca",
        tactical_style="Vertical Positional Transition",
        players=[
            PlayerProfile(id="che_01", name="Robert Sanchez", number=1, position="GK", team_id="chelsea", pace=67, stamina=80, passing_skill=81, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="che_24", name="Reece James", number=24, position="RB", team_id="chelsea", pace=85, stamina=86, passing_skill=86, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="che_29", name="Wesley Fofana", number=29, position="CB", team_id="chelsea", pace=83, stamina=85, passing_skill=77, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="che_06", name="Levi Colwill", number=6, position="CB", team_id="chelsea", pace=80, stamina=86, passing_skill=84, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="che_03", name="Marc Cucurella", number=3, position="LB", team_id="chelsea", pace=82, stamina=92, passing_skill=81, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="che_25", name="Moises Caicedo", number=25, position="CDM", team_id="chelsea", pace=83, stamina=94, passing_skill=86, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="che_08", name="Enzo Fernandez", number=8, position="CM", team_id="chelsea", pace=78, stamina=91, passing_skill=91, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="che_20", name="Cole Palmer", number=20, position="CAM", team_id="chelsea", pace=85, stamina=89, passing_skill=93, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="che_11", name="Noni Madueke", number=11, position="RW", team_id="chelsea", pace=90, stamina=86, passing_skill=80, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="che_07", name="Pedro Neto", number=7, position="LW", team_id="chelsea", pace=92, stamina=88, passing_skill=82, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="che_15", name="Nicolas Jackson", number=15, position="ST", team_id="chelsea", pace=88, stamina=88, passing_skill=78, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    # 5. MANCHESTER UNITED
    teams["manunited"] = TeamProfile(
        id="manunited",
        name="Manchester United",
        short_name="MUN",
        primary_color="#DA291C",  # United Red
        secondary_color="#FBE122",
        formation="4-2-3-1",
        manager="Ruben Amorim",
        tactical_style="Fast-Break Direct Counter",
        players=[
            PlayerProfile(id="mun_24", name="Andre Onana", number=24, position="GK", team_id="manunited", pace=68, stamina=82, passing_skill=89, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="mun_20", name="Diogo Dalot", number=20, position="RB", team_id="manunited", pace=85, stamina=90, passing_skill=81, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="mun_04", name="Matthijs de Ligt", number=4, position="CB", team_id="manunited", pace=79, stamina=88, passing_skill=80, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="mun_06", name="Lisandro Martinez", number=6, position="CB", team_id="manunited", pace=81, stamina=91, passing_skill=85, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="mun_03", name="Noussair Mazraoui", number=3, position="LB", team_id="manunited", pace=82, stamina=87, passing_skill=83, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="mun_18", name="Casemiro", number=18, position="CDM", team_id="manunited", pace=68, stamina=85, passing_skill=83, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="mun_37", name="Kobbie Mainoo", number=37, position="CM", team_id="manunited", pace=81, stamina=91, passing_skill=88, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="mun_08", name="Bruno Fernandes", number=8, position="CAM", team_id="manunited", pace=80, stamina=96, passing_skill=94, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="mun_17", name="Alejandro Garnacho", number=17, position="RW", team_id="manunited", pace=91, stamina=87, passing_skill=80, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="mun_10", name="Marcus Rashford", number=10, position="LW", team_id="manunited", pace=91, stamina=86, passing_skill=82, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="mun_11", name="Rasmus Hojlund", number=11, position="ST", team_id="manunited", pace=89, stamina=88, passing_skill=77, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    return teams
