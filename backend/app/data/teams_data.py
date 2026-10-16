from typing import List, Dict
from app.data.models import TeamProfile, PlayerProfile, PitchCoordinates

def get_premier_league_teams() -> Dict[str, TeamProfile]:
    """
    Returns all 20 authentic Premier League clubs (2024-2026) with real rosters,
    formations, tactical profiles, and accurate player attributes.
    """
    teams = {}

    # 1. ARSENAL
    teams["arsenal"] = TeamProfile(
        id="arsenal",
        name="Arsenal",
        short_name="ARS",
        primary_color="#EF0107",
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
        primary_color="#6CABDD",
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
        primary_color="#C8102E",
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

    # 4. ASTON VILLA
    teams["astonvilla"] = TeamProfile(
        id="astonvilla",
        name="Aston Villa",
        short_name="AVL",
        primary_color="#95BFE5",
        secondary_color="#670E36",
        formation="4-2-3-1",
        manager="Unai Emery",
        tactical_style="Calculated Low-Block & Rapid Vertical Overload",
        players=[
            PlayerProfile(id="avl_23", name="Emiliano Martinez", number=23, position="GK", team_id="astonvilla", pace=68, stamina=84, passing_skill=85, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="avl_02", name="Matty Cash", number=2, position="RB", team_id="astonvilla", pace=84, stamina=88, passing_skill=78, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="avl_04", name="Ezri Konsa", number=4, position="CB", team_id="astonvilla", pace=82, stamina=88, passing_skill=80, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="avl_14", name="Pau Torres", number=14, position="CB", team_id="astonvilla", pace=77, stamina=85, passing_skill=88, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="avl_12", name="Lucas Digne", number=12, position="LB", team_id="astonvilla", pace=81, stamina=86, passing_skill=84, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="avl_08", name="Youri Tielemans", number=8, position="CDM", team_id="astonvilla", pace=74, stamina=88, passing_skill=91, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="avl_24", name="Amadou Onana", number=24, position="CM", team_id="astonvilla", pace=81, stamina=92, passing_skill=82, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="avl_07", name="John McGinn", number=7, position="CAM", team_id="astonvilla", pace=80, stamina=94, passing_skill=86, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="avl_31", name="Leon Bailey", number=31, position="RW", team_id="astonvilla", pace=92, stamina=84, passing_skill=82, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="avl_27", name="Morgan Rogers", number=27, position="LW", team_id="astonvilla", pace=86, stamina=88, passing_skill=84, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="avl_11", name="Ollie Watkins", number=11, position="ST", team_id="astonvilla", pace=89, stamina=91, passing_skill=81, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    # 5. TOTTENHAM HOTSPUR
    teams["tottenham"] = TeamProfile(
        id="tottenham",
        name="Tottenham Hotspur",
        short_name="TOT",
        primary_color="#132257",
        secondary_color="#FFFFFF",
        formation="4-3-3",
        manager="Ange Postecoglou",
        tactical_style="Ultra-High Defensive Line & Relentless Attacking",
        players=[
            PlayerProfile(id="tot_01", name="Guglielmo Vicario", number=1, position="GK", team_id="tottenham", pace=70, stamina=82, passing_skill=84, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="tot_23", name="Pedro Porro", number=23, position="RB", team_id="tottenham", pace=86, stamina=90, passing_skill=87, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="tot_17", name="Cristian Romero", number=17, position="CB", team_id="tottenham", pace=81, stamina=91, passing_skill=82, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="tot_37", name="Micky van de Ven", number=37, position="CB", team_id="tottenham", pace=95, stamina=89, passing_skill=81, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="tot_13", name="Destiny Udogie", number=13, position="LB", team_id="tottenham", pace=88, stamina=91, passing_skill=81, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="tot_29", name="Pape Matar Sarr", number=29, position="CDM", team_id="tottenham", pace=83, stamina=93, passing_skill=83, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="tot_30", name="Rodrigo Bentancur", number=30, position="CM", team_id="tottenham", pace=80, stamina=90, passing_skill=87, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="tot_10", name="James Maddison", number=10, position="CAM", team_id="tottenham", pace=80, stamina=87, passing_skill=92, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="tot_21", name="Dejan Kulusevski", number=21, position="RW", team_id="tottenham", pace=84, stamina=94, passing_skill=88, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="tot_07", name="Son Heung-min", number=7, position="LW", team_id="tottenham", pace=89, stamina=88, passing_skill=87, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="tot_19", name="Dominic Solanke", number=19, position="ST", team_id="tottenham", pace=86, stamina=90, passing_skill=79, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    # 6. CHELSEA
    teams["chelsea"] = TeamProfile(
        id="chelsea",
        name="Chelsea",
        short_name="CHE",
        primary_color="#034694",
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

    # 7. NEWCASTLE UNITED
    teams["newcastle"] = TeamProfile(
        id="newcastle",
        name="Newcastle United",
        short_name="NEW",
        primary_color="#241F20",
        secondary_color="#41B6E6",
        formation="4-3-3",
        manager="Eddie Howe",
        tactical_style="Aggressive Direct Transitions & Physical Press",
        players=[
            PlayerProfile(id="new_22", name="Nick Pope", number=22, position="GK", team_id="newcastle", pace=68, stamina=81, passing_skill=75, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="new_02", name="Kieran Trippier", number=2, position="RB", team_id="newcastle", pace=78, stamina=87, passing_skill=90, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="new_05", name="Fabian Schar", number=5, position="CB", team_id="newcastle", pace=75, stamina=86, passing_skill=85, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="new_33", name="Dan Burn", number=33, position="CB", team_id="newcastle", pace=72, stamina=88, passing_skill=76, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="new_20", name="Lewis Hall", number=20, position="LB", team_id="newcastle", pace=83, stamina=87, passing_skill=82, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="new_39", name="Bruno Guimaraes", number=39, position="CDM", team_id="newcastle", pace=79, stamina=94, passing_skill=91, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="new_07", name="Joelinton", number=7, position="CM", team_id="newcastle", pace=82, stamina=95, passing_skill=82, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="new_08", name="Sandro Tonali", number=8, position="CAM", team_id="newcastle", pace=84, stamina=91, passing_skill=88, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="new_23", name="Jacob Murphy", number=23, position="RW", team_id="newcastle", pace=88, stamina=86, passing_skill=80, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="new_10", name="Anthony Gordon", number=10, position="LW", team_id="newcastle", pace=93, stamina=91, passing_skill=81, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="new_14", name="Alexander Isak", number=14, position="ST", team_id="newcastle", pace=91, stamina=88, passing_skill=82, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    # 8. MANCHESTER UNITED
    teams["manunited"] = TeamProfile(
        id="manunited",
        name="Manchester United",
        short_name="MUN",
        primary_color="#DA291C",
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

    # 9. BRIGHTON & HOVE ALBION
    teams["brighton"] = TeamProfile(
        id="brighton",
        name="Brighton & Hove Albion",
        short_name="BHA",
        primary_color="#0057B8",
        secondary_color="#FFCD00",
        formation="4-2-3-1",
        manager="Fabian Hurzeler",
        tactical_style="Vertical Bait-and-Switch Build-up",
        players=[
            PlayerProfile(id="bha_01", name="Bart Verbruggen", number=1, position="GK", team_id="brighton", pace=68, stamina=80, passing_skill=87, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="bha_34", name="Joel Veltman", number=34, position="RB", team_id="brighton", pace=75, stamina=85, passing_skill=80, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="bha_05", name="Lewis Dunk", number=5, position="CB", team_id="brighton", pace=72, stamina=89, passing_skill=84, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="bha_29", name="Jan Paul van Hecke", number=29, position="CB", team_id="brighton", pace=78, stamina=88, passing_skill=82, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="bha_30", name="Pervis Estupinan", number=30, position="LB", team_id="brighton", pace=87, stamina=90, passing_skill=80, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="bha_20", name="Carlos Baleba", number=20, position="CDM", team_id="brighton", pace=84, stamina=92, passing_skill=85, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="bha_26", name="Yasin Ayari", number=26, position="CM", team_id="brighton", pace=80, stamina=88, passing_skill=84, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="bha_14", name="Georginio Rutter", number=14, position="CAM", team_id="brighton", pace=84, stamina=86, passing_skill=85, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="bha_11", name="Simon Adingra", number=11, position="RW", team_id="brighton", pace=90, stamina=85, passing_skill=81, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="bha_22", name="Kaoru Mitoma", number=22, position="LW", team_id="brighton", pace=91, stamina=88, passing_skill=86, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="bha_18", name="Danny Welbeck", number=18, position="ST", team_id="brighton", pace=82, stamina=86, passing_skill=80, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    # 10. WEST HAM UNITED
    teams["westham"] = TeamProfile(
        id="westham",
        name="West Ham United",
        short_name="WHU",
        primary_color="#7A263A",
        secondary_color="#1BB1E7",
        formation="4-2-3-1",
        manager="Julen Lopetegui",
        tactical_style="Physical Compact Block & Wide Transitions",
        players=[
            PlayerProfile(id="whu_23", name="Alphonse Areola", number=23, position="GK", team_id="westham", pace=68, stamina=80, passing_skill=78, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="whu_29", name="Aaron Wan-Bissaka", number=29, position="RB", team_id="westham", pace=87, stamina=88, passing_skill=78, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="whu_25", name="Jean-Clair Todibo", number=25, position="CB", team_id="westham", pace=82, stamina=86, passing_skill=82, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="whu_26", name="Max Kilman", number=26, position="CB", team_id="westham", pace=76, stamina=88, passing_skill=80, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="whu_33", name="Emerson", number=33, position="LB", team_id="westham", pace=82, stamina=87, passing_skill=81, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="whu_19", name="Edson Alvarez", number=19, position="CDM", team_id="westham", pace=75, stamina=91, passing_skill=82, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="whu_28", name="Tomas Soucek", number=28, position="CM", team_id="westham", pace=73, stamina=94, passing_skill=78, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="whu_10", name="Lucas Paqueta", number=10, position="CAM", team_id="westham", pace=79, stamina=89, passing_skill=91, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="whu_20", name="Jarrod Bowen", number=20, position="RW", team_id="westham", pace=87, stamina=92, passing_skill=83, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="whu_14", name="Mohammed Kudus", number=14, position="LW", team_id="westham", pace=90, stamina=89, passing_skill=84, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="whu_09", name="Michail Antonio", number=9, position="ST", team_id="westham", pace=84, stamina=86, passing_skill=75, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    # 11. AFC BOURNEMOUTH
    teams["bournemouth"] = TeamProfile(
        id="bournemouth",
        name="AFC Bournemouth",
        short_name="BOU",
        primary_color="#DA291C",
        secondary_color="#000000",
        formation="4-2-3-1",
        manager="Andoni Iraola",
        tactical_style="Aggressive Gegenpressing & Rapid Wing Circulation",
        players=[
            PlayerProfile(id="bou_13", name="Kepa Arrizabalaga", number=13, position="GK", team_id="bournemouth", pace=68, stamina=80, passing_skill=83, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="bou_15", name="Adam Smith", number=15, position="RB", team_id="bournemouth", pace=78, stamina=86, passing_skill=77, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="bou_27", name="Illia Zabarnyi", number=27, position="CB", team_id="bournemouth", pace=80, stamina=89, passing_skill=80, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="bou_05", name="Marcos Senesi", number=5, position="CB", team_id="bournemouth", pace=75, stamina=86, passing_skill=84, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="bou_03", name="Milos Kerkez", number=3, position="LB", team_id="bournemouth", pace=89, stamina=91, passing_skill=79, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="bou_04", name="Lewis Cook", number=4, position="CDM", team_id="bournemouth", pace=78, stamina=92, passing_skill=85, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="bou_10", name="Ryan Christie", number=10, position="CM", team_id="bournemouth", pace=81, stamina=95, passing_skill=84, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="bou_19", name="Justin Kluivert", number=19, position="CAM", team_id="bournemouth", pace=88, stamina=86, passing_skill=82, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="bou_24", name="Antoine Semenyo", number=24, position="RW", team_id="bournemouth", pace=89, stamina=90, passing_skill=81, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="bou_16", name="Marcus Tavernier", number=16, position="LW", team_id="bournemouth", pace=86, stamina=89, passing_skill=82, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="bou_09", name="Evanilson", number=9, position="ST", team_id="bournemouth", pace=85, stamina=87, passing_skill=79, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    # 12. BRENTFORD
    teams["brentford"] = TeamProfile(
        id="brentford",
        name="Brentford",
        short_name="BRE",
        primary_color="#D20000",
        secondary_color="#FFFFFF",
        formation="4-3-3",
        manager="Thomas Frank",
        tactical_style="Set-Piece Mastery & Dynamic Half-Space Breaks",
        players=[
            PlayerProfile(id="bre_01", name="Mark Flekken", number=1, position="GK", team_id="brentford", pace=68, stamina=80, passing_skill=84, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="bre_20", name="Kristoffer Ajer", number=20, position="RB", team_id="brentford", pace=81, stamina=87, passing_skill=79, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="bre_22", name="Nathan Collins", number=22, position="CB", team_id="brentford", pace=79, stamina=88, passing_skill=78, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="bre_05", name="Ethan Pinnock", number=5, position="CB", team_id="brentford", pace=77, stamina=90, passing_skill=76, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="bre_03", name="Rico Henry", number=3, position="LB", team_id="brentford", pace=91, stamina=88, passing_skill=78, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="bre_06", name="Christian Norgaard", number=6, position="CDM", team_id="brentford", pace=74, stamina=92, passing_skill=86, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="bre_27", name="Vitaly Janelt", number=27, position="CM", team_id="brentford", pace=78, stamina=93, passing_skill=82, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="bre_08", name="Mathias Jensen", number=8, position="CAM", team_id="brentford", pace=76, stamina=88, passing_skill=87, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="bre_19", name="Bryan Mbeumo", number=19, position="RW", team_id="brentford", pace=89, stamina=91, passing_skill=84, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="bre_23", name="Keane Lewis-Potter", number=23, position="LW", team_id="brentford", pace=87, stamina=86, passing_skill=79, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="bre_11", name="Yoane Wissa", number=11, position="ST", team_id="brentford", pace=88, stamina=87, passing_skill=79, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    # 13. FULHAM
    teams["fulham"] = TeamProfile(
        id="fulham",
        name="Fulham",
        short_name="FUL",
        primary_color="#FFFFFF",
        secondary_color="#CC0000",
        formation="4-2-3-1",
        manager="Marco Silva",
        tactical_style="Fluid Possession & Aggressive Overlapping Fullbacks",
        players=[
            PlayerProfile(id="ful_01", name="Bernd Leno", number=1, position="GK", team_id="fulham", pace=68, stamina=82, passing_skill=83, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="ful_21", name="Timothy Castagne", number=21, position="RB", team_id="fulham", pace=82, stamina=88, passing_skill=79, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="ful_05", name="Joachim Andersen", number=5, position="CB", team_id="fulham", pace=76, stamina=88, passing_skill=87, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="ful_03", name="Calvin Bassey", number=3, position="CB", team_id="fulham", pace=84, stamina=89, passing_skill=78, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="ful_33", name="Antonee Robinson", number=33, position="LB", team_id="fulham", pace=92, stamina=94, passing_skill=80, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="ful_16", name="Sander Berge", number=16, position="CDM", team_id="fulham", pace=79, stamina=90, passing_skill=83, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="ful_18", name="Andreas Pereira", number=18, position="CM", team_id="fulham", pace=80, stamina=88, passing_skill=88, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="ful_32", name="Emile Smith Rowe", number=32, position="CAM", team_id="fulham", pace=83, stamina=86, passing_skill=87, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="ful_17", name="Alex Iwobi", number=17, position="RW", team_id="fulham", pace=85, stamina=91, passing_skill=83, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="ful_11", name="Adama Traore", number=11, position="LW", team_id="fulham", pace=96, stamina=85, passing_skill=76, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="ful_07", name="Raul Jimenez", number=7, position="ST", team_id="fulham", pace=78, stamina=84, passing_skill=81, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    # 14. WOLVERHAMPTON WANDERERS
    teams["wolves"] = TeamProfile(
        id="wolves",
        name="Wolverhampton Wanderers",
        short_name="WOL",
        primary_color="#FDB913",
        secondary_color="#231F20",
        formation="4-2-3-1",
        manager="Gary O'Neil",
        tactical_style="Vertical Wing Dribble & Central Anchor",
        players=[
            PlayerProfile(id="wol_01", name="Jose Sa", number=1, position="GK", team_id="wolves", pace=68, stamina=80, passing_skill=80, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="wol_02", name="Matt Doherty", number=2, position="RB", team_id="wolves", pace=78, stamina=86, passing_skill=78, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="wol_24", name="Toti Gomes", number=24, position="CB", team_id="wolves", pace=82, stamina=88, passing_skill=76, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="wol_15", name="Craig Dawson", number=15, position="CB", team_id="wolves", pace=70, stamina=87, passing_skill=77, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="wol_03", name="Rayan Ait-Nouri", number=3, position="LB", team_id="wolves", pace=88, stamina=89, passing_skill=85, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="wol_05", name="Mario Lemina", number=5, position="CDM", team_id="wolves", pace=79, stamina=93, passing_skill=83, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="wol_08", name="Joao Gomes", number=8, position="CM", team_id="wolves", pace=82, stamina=95, passing_skill=82, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="wol_20", name="Tommy Doyle", number=20, position="CAM", team_id="wolves", pace=78, stamina=88, passing_skill=85, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="wol_21", name="Rodrigo Gomes", number=21, position="RW", team_id="wolves", pace=89, stamina=86, passing_skill=79, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="wol_10", name="Matheus Cunha", number=10, position="LW", team_id="wolves", pace=88, stamina=89, passing_skill=86, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="wol_09", name="Jorgen Strand Larsen", number=9, position="ST", team_id="wolves", pace=82, stamina=87, passing_skill=78, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    # 15. EVERTON
    teams["everton"] = TeamProfile(
        id="everton",
        name="Everton",
        short_name="EVE",
        primary_color="#003399",
        secondary_color="#FFFFFF",
        formation="4-4-1-1",
        manager="Sean Dyche",
        tactical_style="Direct Aerial Duels & Resolute Low-Block",
        players=[
            PlayerProfile(id="eve_01", name="Jordan Pickford", number=1, position="GK", team_id="everton", pace=68, stamina=82, passing_skill=88, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="eve_18", name="Ashley Young", number=18, position="RB", team_id="everton", pace=76, stamina=84, passing_skill=81, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="eve_06", name="James Tarkowski", number=6, position="CB", team_id="everton", pace=72, stamina=92, passing_skill=78, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="eve_32", name="Jarrad Branthwaite", number=32, position="CB", team_id="everton", pace=83, stamina=89, passing_skill=81, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="eve_19", name="Vitalii Mykolenko", number=19, position="LB", team_id="everton", pace=82, stamina=89, passing_skill=78, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="eve_27", name="Idrissa Gueye", number=27, position="CDM", team_id="everton", pace=76, stamina=91, passing_skill=80, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="eve_42", name="Tim Iroegbunam", number=42, position="CM", team_id="everton", pace=81, stamina=88, passing_skill=79, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="eve_16", name="Abdoulaye Doucoure", number=16, position="CAM", team_id="everton", pace=80, stamina=94, passing_skill=79, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="eve_11", name="Jack Harrison", number=11, position="RW", team_id="everton", pace=84, stamina=89, passing_skill=81, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="eve_07", name="Dwight McNeil", number=7, position="LW", team_id="everton", pace=79, stamina=91, passing_skill=86, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="eve_09", name="Dominic Calvert-Lewin", number=9, position="ST", team_id="everton", pace=86, stamina=88, passing_skill=76, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    # 16. CRYSTAL PALACE
    teams["crystalpalace"] = TeamProfile(
        id="crystalpalace",
        name="Crystal Palace",
        short_name="CRY",
        primary_color="#1B458F",
        secondary_color="#C4122E",
        formation="3-4-2-1",
        manager="Oliver Glasner",
        tactical_style="Aggressive Central Pressing Traps & Dual 10s",
        players=[
            PlayerProfile(id="cry_01", name="Dean Henderson", number=1, position="GK", team_id="crystalpalace", pace=68, stamina=80, passing_skill=80, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="cry_17", name="Nathaniel Clyne", number=17, position="CB", team_id="crystalpalace", pace=78, stamina=85, passing_skill=77, current_coords=PitchCoordinates(x=80.0, y=25.0)),
            PlayerProfile(id="cry_06", name="Marc Guehi", number=6, position="CB", team_id="crystalpalace", pace=82, stamina=89, passing_skill=84, current_coords=PitchCoordinates(x=80.0, y=50.0)),
            PlayerProfile(id="cry_05", name="Maxence Lacroix", number=5, position="CB", team_id="crystalpalace", pace=88, stamina=87, passing_skill=78, current_coords=PitchCoordinates(x=80.0, y=75.0)),
            PlayerProfile(id="cry_12", name="Daniel Munoz", number=12, position="RWB", team_id="crystalpalace", pace=87, stamina=94, passing_skill=81, current_coords=PitchCoordinates(x=65.0, y=15.0)),
            PlayerProfile(id="cry_03", name="Tyrick Mitchell", number=3, position="LWB", team_id="crystalpalace", pace=84, stamina=91, passing_skill=78, current_coords=PitchCoordinates(x=65.0, y=85.0)),
            PlayerProfile(id="cry_20", name="Adam Wharton", number=20, position="CM", team_id="crystalpalace", pace=77, stamina=89, passing_skill=90, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="cry_18", name="Daichi Kamada", number=18, position="CM", team_id="crystalpalace", pace=78, stamina=88, passing_skill=85, current_coords=PitchCoordinates(x=55.0, y=62.0)),
            PlayerProfile(id="cry_07", name="Ismaila Sarr", number=7, position="CAM", team_id="crystalpalace", pace=92, stamina=86, passing_skill=80, current_coords=PitchCoordinates(x=45.0, y=30.0)),
            PlayerProfile(id="cry_10", name="Eberechi Eze", number=10, position="CAM", team_id="crystalpalace", pace=87, stamina=89, passing_skill=91, current_coords=PitchCoordinates(x=45.0, y=70.0)),
            PlayerProfile(id="cry_14", name="Jean-Philippe Mateta", number=14, position="ST", team_id="crystalpalace", pace=84, stamina=89, passing_skill=78, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    # 17. NOTTINGHAM FOREST
    teams["nottingham"] = TeamProfile(
        id="nottingham",
        name="Nottingham Forest",
        short_name="NFO",
        primary_color="#DD0000",
        secondary_color="#FFFFFF",
        formation="4-2-3-1",
        manager="Nuno Espirito Santo",
        tactical_style="Solid Mid-Block & Lightning Wing Transitions",
        players=[
            PlayerProfile(id="nfo_26", name="Matz Sels", number=26, position="GK", team_id="nottingham", pace=68, stamina=80, passing_skill=79, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="nfo_34", name="Ola Aina", number=34, position="RB", team_id="nottingham", pace=88, stamina=89, passing_skill=80, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="nfo_05", name="Murillo", number=5, position="CB", team_id="nottingham", pace=83, stamina=89, passing_skill=86, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="nfo_31", name="Nikola Milenkovic", number=31, position="CB", team_id="nottingham", pace=76, stamina=88, passing_skill=77, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="nfo_15", name="Alex Moreno", number=15, position="LB", team_id="nottingham", pace=87, stamina=88, passing_skill=81, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="nfo_22", name="Ryan Yates", number=22, position="CDM", team_id="nottingham", pace=75, stamina=94, passing_skill=79, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="nfo_28", name="Elliot Anderson", number=28, position="CM", team_id="nottingham", pace=82, stamina=90, passing_skill=84, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="nfo_10", name="Morgan Gibbs-White", number=10, position="CAM", team_id="nottingham", pace=84, stamina=92, passing_skill=89, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="nfo_21", name="Anthony Elanga", number=21, position="RW", team_id="nottingham", pace=94, stamina=87, passing_skill=80, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="nfo_14", name="Callum Hudson-Odoi", number=14, position="LW", team_id="nottingham", pace=89, stamina=86, passing_skill=83, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="nfo_11", name="Chris Wood", number=11, position="ST", team_id="nottingham", pace=76, stamina=87, passing_skill=76, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    # 18. LEICESTER CITY
    teams["leicester"] = TeamProfile(
        id="leicester",
        name="Leicester City",
        short_name="LEI",
        primary_color="#003090",
        secondary_color="#FDBE11",
        formation="4-2-3-1",
        manager="Steve Cooper",
        tactical_style="Vertical Counters & Penalty Box Overloads",
        players=[
            PlayerProfile(id="lei_30", name="Mads Hermansen", number=30, position="GK", team_id="leicester", pace=68, stamina=80, passing_skill=84, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="lei_02", name="James Justin", number=2, position="RB", team_id="leicester", pace=84, stamina=88, passing_skill=79, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="lei_03", name="Wout Faes", number=3, position="CB", team_id="leicester", pace=77, stamina=88, passing_skill=78, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="lei_05", name="Caleb Okoli", number=5, position="CB", team_id="leicester", pace=82, stamina=87, passing_skill=75, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="lei_16", name="Victor Kristiansen", number=16, position="LB", team_id="leicester", pace=83, stamina=89, passing_skill=78, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="lei_08", name="Harry Winks", number=8, position="CDM", team_id="leicester", pace=75, stamina=90, passing_skill=87, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="lei_24", name="Boubakary Soumare", number=24, position="CM", team_id="leicester", pace=79, stamina=88, passing_skill=81, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="lei_18", name="Jordan Ayew", number=18, position="CAM", team_id="leicester", pace=81, stamina=88, passing_skill=80, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="lei_07", name="Abdul Fatawu", number=7, position="RW", team_id="leicester", pace=92, stamina=87, passing_skill=81, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="lei_10", name="Stephy Mavididi", number=10, position="LW", team_id="leicester", pace=88, stamina=87, passing_skill=81, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="lei_09", name="Jamie Vardy", number=9, position="ST", team_id="leicester", pace=85, stamina=88, passing_skill=77, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    # 19. SOUTHAMPTON
    teams["southampton"] = TeamProfile(
        id="southampton",
        name="Southampton",
        short_name="SOU",
        primary_color="#D71920",
        secondary_color="#130C0E",
        formation="4-3-3",
        manager="Russell Martin",
        tactical_style="Extreme Short-Passing Possession & Build-Up from Deep",
        players=[
            PlayerProfile(id="sou_30", name="Aaron Ramsdale", number=30, position="GK", team_id="southampton", pace=68, stamina=82, passing_skill=85, current_coords=PitchCoordinates(x=95.0, y=50.0)),
            PlayerProfile(id="sou_16", name="Yukinari Sugawara", number=16, position="RB", team_id="southampton", pace=84, stamina=89, passing_skill=82, current_coords=PitchCoordinates(x=75.0, y=15.0)),
            PlayerProfile(id="sou_06", name="Taylor Harwood-Bellis", number=6, position="CB", team_id="southampton", pace=78, stamina=88, passing_skill=83, current_coords=PitchCoordinates(x=80.0, y=40.0)),
            PlayerProfile(id="sou_05", name="Jan Bednarek", number=5, position="CB", team_id="southampton", pace=74, stamina=88, passing_skill=79, current_coords=PitchCoordinates(x=80.0, y=60.0)),
            PlayerProfile(id="sou_03", name="Ryan Manning", number=3, position="LB", team_id="southampton", pace=80, stamina=87, passing_skill=81, current_coords=PitchCoordinates(x=75.0, y=85.0)),
            PlayerProfile(id="sou_04", name="Flynn Downes", number=4, position="CDM", team_id="southampton", pace=78, stamina=92, passing_skill=85, current_coords=PitchCoordinates(x=62.0, y=50.0)),
            PlayerProfile(id="sou_18", name="Mateus Fernandes", number=18, position="CM", team_id="southampton", pace=83, stamina=89, passing_skill=86, current_coords=PitchCoordinates(x=55.0, y=38.0)),
            PlayerProfile(id="sou_20", name="Kamaldeen Sulemana", number=20, position="CAM", team_id="southampton", pace=92, stamina=84, passing_skill=78, current_coords=PitchCoordinates(x=52.0, y=62.0)),
            PlayerProfile(id="sou_33", name="Tyler Dibling", number=33, position="RW", team_id="southampton", pace=86, stamina=85, passing_skill=84, current_coords=PitchCoordinates(x=42.0, y=15.0)),
            PlayerProfile(id="sou_10", name="Adam Lallana", number=10, position="LW", team_id="southampton", pace=75, stamina=82, passing_skill=88, current_coords=PitchCoordinates(x=42.0, y=85.0)),
            PlayerProfile(id="sou_09", name="Adam Armstrong", number=9, position="ST", team_id="southampton", pace=89, stamina=88, passing_skill=77, current_coords=PitchCoordinates(x=34.0, y=50.0))
        ]
    )

    # 20. IPSWICH TOWN
    teams["ipswich"] = TeamProfile(
        id="ipswich",
        name="Ipswich Town",
        short_name="IPS",
        primary_color="#00448A",
        secondary_color="#FFFFFF",
        formation="4-2-3-1",
        manager="Kieran McKenna",
        tactical_style="Brave High-Tempo Pressing & Direct Wing Overloads",
        players=[
            PlayerProfile(id="ips_01", name="Arijanet Muric", number=1, position="GK", team_id="ipswich", pace=68, stamina=80, passing_skill=83, current_coords=PitchCoordinates(x=5.0, y=50.0)),
            PlayerProfile(id="ips_40", name="Axel Tuanzebe", number=40, position="RB", team_id="ipswich", pace=83, stamina=86, passing_skill=78, current_coords=PitchCoordinates(x=25.0, y=85.0)),
            PlayerProfile(id="ips_26", name="Dara O'Shea", number=26, position="CB", team_id="ipswich", pace=78, stamina=88, passing_skill=79, current_coords=PitchCoordinates(x=20.0, y=60.0)),
            PlayerProfile(id="ips_06", name="Luke Woolfenden", number=6, position="CB", team_id="ipswich", pace=76, stamina=87, passing_skill=78, current_coords=PitchCoordinates(x=20.0, y=40.0)),
            PlayerProfile(id="ips_03", name="Leif Davis", number=3, position="LB", team_id="ipswich", pace=86, stamina=91, passing_skill=86, current_coords=PitchCoordinates(x=25.0, y=15.0)),
            PlayerProfile(id="ips_05", name="Sam Morsy", number=5, position="CDM", team_id="ipswich", pace=76, stamina=93, passing_skill=82, current_coords=PitchCoordinates(x=38.0, y=50.0)),
            PlayerProfile(id="ips_12", name="Jens Cajuste", number=12, position="CM", team_id="ipswich", pace=81, stamina=89, passing_skill=82, current_coords=PitchCoordinates(x=46.0, y=35.0)),
            PlayerProfile(id="ips_20", name="Omari Hutchinson", number=20, position="CAM", team_id="ipswich", pace=88, stamina=87, passing_skill=84, current_coords=PitchCoordinates(x=58.0, y=62.0)),
            PlayerProfile(id="ips_07", name="Wes Burns", number=7, position="RW", team_id="ipswich", pace=89, stamina=86, passing_skill=78, current_coords=PitchCoordinates(x=68.0, y=85.0)),
            PlayerProfile(id="ips_23", name="Sammie Szmodics", number=23, position="LW", team_id="ipswich", pace=85, stamina=91, passing_skill=81, current_coords=PitchCoordinates(x=68.0, y=15.0)),
            PlayerProfile(id="ips_19", name="Liam Delap", number=19, position="ST", team_id="ipswich", pace=88, stamina=89, passing_skill=78, current_coords=PitchCoordinates(x=74.0, y=50.0))
        ]
    )

    return teams
