class Avion:
    """
    Représente un aéronef avec ses caractéristiques de vol essentielles.
    
    Attributes:
        icao24 (str): Adresse ICAO24 du transpondeur (identifiant unique)
        callsign (str): Indicatif d'appel de l'appareil
        longitude (float): Longitude en degrés (WGS-84)
        latitude (float): Latitude en degrés (WGS-84)
        velocity (float): Vitesse au sol en m/s
        true_track (float): Direction vraie en degrés (0 = nord)
        on_ground (bool): True si l'avion est au sol
    """
    
    def __init__(self, icao24, callsign, longitude, latitude, velocity, true_track, on_ground):
        self.icao24 = icao24
        self.callsign = callsign if callsign else "N/A"
        self.longitude = longitude
        self.latitude = latitude
        self.velocity = velocity if velocity is not None else 0.0
        self.true_track = true_track if true_track is not None else 0.0
        self.on_ground = on_ground
    
    @classmethod
    def from_state_vector(cls, state_vector):
        """
        Crée une instance d'Avion à partir d'un StateVector d'OpenSky API.
        
        Args:
            state_vector: Objet StateVector retourné par OpenSky API
            
        Returns:
            Avion: Instance d'Avion avec les données extraites
        """
        return cls(
            icao24=state_vector.icao24,
            callsign=state_vector.callsign.strip() if state_vector.callsign else None,
            longitude=state_vector.longitude,
            latitude=state_vector.latitude,
            velocity=state_vector.velocity,
            true_track=state_vector.true_track,
            on_ground=state_vector.on_ground
        )
    
    @classmethod
    def from_dict(cls, data):
        """
        Crée une instance d'Avion à partir d'un dictionnaire.
        
        Args:
            data (dict): Dictionnaire contenant les attributs de l'avion
            
        Returns:
            Avion: Instance d'Avion avec les données du dictionnaire
        """
        return cls(
            icao24=data['icao24'],
            callsign=data.get('callsign'),
            longitude=data.get('longitude'),
            latitude=data.get('latitude'),
            velocity=data.get('velocity'),
            on_ground=data.get('on_ground'),
            true_track=data.get('true_track')
        )
    
    def to_dict(self):
        """
        Convertit l'objet Avion en dictionnaire.
        
        Returns:
            dict: Dictionnaire contenant tous les attributs de l'avion
        """
        return {
            'icao24': self.icao24,
            'callsign': self.callsign,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'velocity': self.velocity,
            'true_track': self.true_track,
            'on_ground': self.on_ground
        }
    
    def get_velocity_kmh(self):
        """
        Retourne la vitesse en km/h.
        
        Returns:
            float: Vitesse en km/h
        """
        return self.velocity * 3.6
    
    def is_valid_position(self):
        """
        Vérifie si l'avion possède des coordonnées valides.
        
        Returns:
            bool: True si longitude et latitude ne sont pas None
        """
        return self.longitude is not None and self.latitude is not None
    
    def __repr__(self):
        """
        Représentation textuelle de l'objet Avion.
        
        Returns:
            str: Chaîne décrivant l'avion
        """
        status = "au sol" if self.on_ground else "en vol"
        return (f"Avion(icao24={self.icao24}, callsign={self.callsign}, "
                f"pos=({self.latitude:.2f}, {self.longitude:.2f}), "
                f"vitesse={self.get_velocity_kmh():.0f} km/h, "
                f"cap={self.true_track:.0f}°, {status})")
    


