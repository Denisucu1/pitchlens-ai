from typing import Optional
from app.data.models import (
    MatchEvent, EventType, ShotOutcome, RhythmState,
    PersonalizedNarrative, Language, PlayerProfile
)

class PersonalizationStoryEngine:
    """
    Stage E: Audience Personalization & Multi-Language Storytelling Layer
    Transforms the same underlying event intelligence into distinct, bespoke narratives:
    - Casual Fan: High energy, relatable, dramatic broadcast storytelling.
    - Data-Hungry Analyst: Quantitative, tactical terminology, xG, pass difficulty, pitch geometry.
    - Player Focused: Dedicated spotlight tracking performance, work rate, and milestones.
    Supports English (EN), Romanian (RO), and Spanish (ES).
    """

    def generate_narrative(
        self,
        event: MatchEvent,
        rhythm: RhythmState,
        focused_player: Optional[PlayerProfile] = None,
        language: Language = Language.EN
    ) -> PersonalizedNarrative:
        
        lang_str = str(language.value if hasattr(language, "value") else language).lower()
        if "ro" in lang_str:
            return self._generate_romanian(event, rhythm, focused_player)
        elif "es" in lang_str:
            return self._generate_spanish(event, rhythm, focused_player)
        else:
            return self._generate_english(event, rhythm, focused_player)

    def _generate_english(self, event: MatchEvent, rhythm: RhythmState, focused_player: Optional[PlayerProfile]) -> PersonalizedNarrative:
        # 1. Casual Fan Narrative
        if event.event_type == EventType.GOAL:
            casual = f"🔥 INCREDIBLE GOAL! {event.player.name} fires a sensational rocket into the net! The stadium erupts!"
        elif event.event_type == EventType.SHOT:
            casual = f"⚡ Close call! {event.player.name} unleashes a stinging drive from distance, tested the keeper!"
        elif event.event_type == EventType.TACKLE:
            casual = f"🛡️ Brilliant crunching tackle by {event.player.name}! Snuffing out the danger right on time."
        else:
            casual = f"⚽ Smooth build-up play as {event.player.name} switches play swiftly under pressure."

        # 2. Data Analyst Narrative
        if event.event_type == EventType.GOAL:
            analyst = (
                f"[xG: {event.xG:.2f} | Shot Speed: {event.shot_speed_kmh} km/h] "
                f"{event.player.name} converts high-value box delivery. Control index peaked at {rhythm.control_vs_chaos_index:.1f}% "
                f"during possession chain {event.possession_chain_id}."
            )
        elif event.event_type == EventType.SHOT:
            analyst = (
                f"[Shot Event | xG: {event.xG:.2f}] Velocity: {event.shot_speed_kmh} km/h from ({event.location.x:.1f}, {event.location.y:.1f}). "
                f"Defensive pressure at release: {event.pressure_intensity:.1f}%."
            )
        elif event.event_type == EventType.PASS:
            diff_str = f"Diff: {event.pass_difficulty_rating:.2f}" if event.pass_difficulty_rating else "Standard"
            analyst = (
                f"[Pass Event | {event.pass_distance_m}m @ {event.ball_speed_kmh} km/h] "
                f"{event.player.name} -> {event.recipient.name if event.recipient else 'space'}. {diff_str}. "
                f"Sector: {rhythm.dominant_zone}."
            )
        else:
            analyst = (
                f"[{event.event_type.upper()} | Pressure: {event.pressure_intensity:.1f}%] "
                f"Chaos rating: {100.0 - rhythm.control_vs_chaos_index:.1f}%. Sprint recorded: {event.player_speed_kmh} km/h."
            )

        # 3. Player Focused Narrative
        player_focus = None
        if focused_player:
            if event.player.id == focused_player.id:
                player_focus = (
                    f"⭐ {focused_player.name} Active: Clocked at {event.player_speed_kmh} km/h. "
                    f"Total ground covered: {focused_player.distance_covered_meters:.0f}m across {focused_player.sprint_count} sprints."
                )
            else:
                player_focus = (
                    f"👀 Tracking {focused_player.name}: Holding position at ({focused_player.current_coords.x:.1f}, {focused_player.current_coords.y:.1f}) "
                    f"while {event.player.name} drives play in {rhythm.dominant_zone}."
                )

        return PersonalizedNarrative(
            minute=event.minute,
            second=event.second,
            casual_fan_narrative=casual,
            data_analyst_narrative=analyst,
            player_focus_narrative=player_focus,
            language=Language.EN
        )

    def _generate_romanian(self, event: MatchEvent, rhythm: RhythmState, focused_player: Optional[PlayerProfile]) -> PersonalizedNarrative:
        # Casual Fan (RO)
        if event.event_type == EventType.GOAL:
            casual = f"🔥 GOOOL FABULOS! {event.player.name} trimite o ghiulea imparabilă direct în plasă! Tribunele explodează!"
        elif event.event_type == EventType.SHOT:
            casual = f"⚡ Ce ocazie! {event.player.name} trage puternic de la distanță, portarul respinge cu greu!"
        elif event.event_type == EventType.TACKLE:
            casual = f"🛡️ Intervenție defensivă excelentă a lui {event.player.name}! Oprește un atac periculos."
        else:
            casual = f"⚽ Construcție rapidă de pase orchestrată de {event.player.name} sub presiunea adversă."

        # Data Analyst (RO)
        if event.event_type == EventType.GOAL:
            analyst = (
                f"[xG: {event.xG:.2f} | Viteză Șut: {event.shot_speed_kmh} km/h] "
                f"{event.player.name} finalizează cu eficiență maximă. Indicele de Control a atins {rhythm.control_vs_chaos_index:.1f}% "
                f"în lanțul de posesie {event.possession_chain_id}."
            )
        elif event.event_type == EventType.SHOT:
            analyst = (
                f"[Șut | xG: {event.xG:.2f}] Viteză minge: {event.shot_speed_kmh} km/h din coordonate ({event.location.x:.1f}, {event.location.y:.1f}). "
                f"Presiune adversă: {event.pressure_intensity:.1f}%."
            )
        elif event.event_type == EventType.PASS:
            diff_str = f"Dificultate: {event.pass_difficulty_rating:.2f}" if event.pass_difficulty_rating else "Standard"
            analyst = (
                f"[Pasă | {event.pass_distance_m}m la {event.ball_speed_kmh} km/h] "
                f"{event.player.name} -> {event.recipient.name if event.recipient else 'spațiu liber'}. {diff_str}. "
                f"Zonă: {rhythm.dominant_zone}."
            )
        else:
            analyst = (
                f"[{event.event_type.upper()} | Presiune: {event.pressure_intensity:.1f}%] "
                f"Indice Haos: {100.0 - rhythm.control_vs_chaos_index:.1f}%. Viteză sprint: {event.player_speed_kmh} km/h."
            )

        # Player Focus (RO)
        player_focus = None
        if focused_player:
            if event.player.id == focused_player.id:
                player_focus = (
                    f"⭐ {focused_player.name} în acțiune: Înregistrat la {event.player_speed_kmh} km/h. "
                    f"Distanță parcursă: {focused_player.distance_covered_meters:.0f}m în {focused_player.sprint_count} sprinturi."
                )
            else:
                player_focus = (
                    f"👀 Urmărire {focused_player.name}: Menține poziția la ({focused_player.current_coords.x:.1f}, {focused_player.current_coords.y:.1f}) "
                    f"în timp ce {event.player.name} dictează jocul în zona centrală."
                )

        return PersonalizedNarrative(
            minute=event.minute,
            second=event.second,
            casual_fan_narrative=casual,
            data_analyst_narrative=analyst,
            player_focus_narrative=player_focus,
            language=Language.RO
        )

    def _generate_spanish(self, event: MatchEvent, rhythm: RhythmState, focused_player: Optional[PlayerProfile]) -> PersonalizedNarrative:
        # Casual Fan (ES)
        if event.event_type == EventType.GOAL:
            casual = f"🔥 ¡GOLAZO INCREÍBLE! ¡{event.player.name} revienta el balón al fondo de la red! ¡Delirio en las gradas!"
        elif event.event_type == EventType.SHOT:
            casual = f"⚡ ¡Uff, qué disparo! {event.player.name} prueba fortuna desde fuera del área con gran potencia."
        else:
            casual = f"⚽ Gran circulación de balón guiada por {event.player.name} rompiendo la presión rival."

        # Data Analyst (ES)
        if event.event_type == EventType.GOAL:
            analyst = (
                f"[xG: {event.xG:.2f} | Velocidad de tiro: {event.shot_speed_kmh} km/h] "
                f"{event.player.name} define con alta precisión. Índice de Control táctico en {rhythm.control_vs_chaos_index:.1f}%."
            )
        else:
            analyst = (
                f"[{event.event_type.upper()} | Presión: {event.pressure_intensity:.1f}%] "
                f"Velocidad de balón: {event.ball_speed_kmh or event.player_speed_kmh} km/h. Índice de Caos: {100.0 - rhythm.control_vs_chaos_index:.1f}%."
            )

        player_focus = f"⭐ Monitor de {focused_player.name}: Distancia recorrida {focused_player.distance_covered_meters:.0f}m." if focused_player else None

        return PersonalizedNarrative(
            minute=event.minute,
            second=event.second,
            casual_fan_narrative=casual,
            data_analyst_narrative=analyst,
            player_focus_narrative=player_focus,
            language=Language.ES
        )
