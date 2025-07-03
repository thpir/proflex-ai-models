import math
import datetime

class SunCalculator:
    def __init__(self):
        self.RAD = math.pi / 180.0
        self.ms_per_day = 1000 * 60 * 60 * 24
        self.J1970 = 2440588.0
        self.J2000 = 2451545.0
        self.earth_obliquity = self.RAD * 23.4397

    def __calculate_days(self, date: datetime.datetime):
        return self.__to_julian(date) - self.J2000
    
    # This part calculates the mean anomaly of the sun. The mean 
    # anomaly is an angle that represents the average angular speed 
    # of the Sun as it moves around the Earth (or more accurately, 
    # the Earth's average angular speed around the Sun). The formula 
    # is a linear approximation based on the number of days since 
    # J2000. The constants are empirical values derived from 
    # observations.
    def __calculate_solar_mean_anomaly(self, number_of_days):
        return self.RAD * (357.5291 + 0.98560028 * number_of_days)
    
    # This method calculates the ecliptic longitude (L). Ecliptic 
    # longitude is one of the coordinates used to define the Sun's 
    # position on the celestial sphere.
    def __calculate_ecliptic_longitude(self, solar_mean_anomaly):
        # This calculates the equation of center. It's a correction 
        # factor that accounts for the fact that the Earth's orbit 
        # is not perfectly circular. The equation of center is 
        # calculated using a series of sine terms (a Fourier series 
        # approximation), where sin(M), sin(2 * M), and sin(3 * M) 
        # represent the primary, secondary, and tertiary corrections, 
        # respectively. The constants (1.9148, 0.02, 0.0003) are 
        # empirical values.
        equation_of_center = self.RAD * (1.9148 * math.sin(solar_mean_anomaly) + 0.02 * math.sin(2 * solar_mean_anomaly) + 0.0003 * math.sin(3 * solar_mean_anomaly))
        # This is the perihelion of the Earth, which is the angular 
        # position of the Sun when the Earth is closest to it in its 
        # orbit. It's also converted to radians.
        perihelion = self.RAD * 102.9372
        return solar_mean_anomaly + equation_of_center + perihelion + math.pi

    def __calculate_declination(self, ecliptic_longitude, ecliptic_latitude):
        return math.asin(math.sin(ecliptic_latitude) * math.cos(self.earth_obliquity) + math.cos(ecliptic_latitude) * math.sin(self.earth_obliquity) * math.sin(ecliptic_longitude))
    
    def __calculate_right_ascension(self, ecliptic_longitude, ecliptic_latitude):
        return math.atan2(math.sin(ecliptic_longitude) * math.cos(self.earth_obliquity) - math.tan(ecliptic_latitude) * math.sin(self.earth_obliquity), math.cos(ecliptic_longitude))

    def __calculate_sun_coordinates(self, number_of_days):
        solar_mean_anomaly = self.__calculate_solar_mean_anomaly(number_of_days)
        ecliptic_longitude = self.__calculate_ecliptic_longitude(solar_mean_anomaly)
        return {
            "declination": self.__calculate_declination(ecliptic_longitude, 0),
            "right_ascension": self.__calculate_right_ascension(ecliptic_longitude, 0)
        }

    def __sidereal_time(self, days_since_epoch, lng_west_in_radians):
        return self.RAD * (280.16 + 360.9856235 * days_since_epoch) - lng_west_in_radians

    def __azimuth(self, hour_angle, lat_in_radians, declination):
        return math.atan2(math.sin(hour_angle), math.cos(hour_angle) * math.sin(lat_in_radians) - math.tan(declination) * math.cos(lat_in_radians))

    def __altitude(self, hour_angle, lat_in_radians, declination):
        return math.asin(math.sin(lat_in_radians) * math.sin(declination) + math.cos(lat_in_radians) * math.cos(declination) * math.cos(hour_angle))

    def __to_julian(self, date: datetime.datetime):
        return (date.timestamp() * 1000) / self.ms_per_day - 0.5 + self.J1970

    # This method calculates the position 
    # of the sun at a given date and location.
    # The altitude is in radians, where 0 is on the horizon and + is above horizon, - is below horizon.
    # The azimuth is in radians, where 0 is south, pi/2 is west, -pi/2 is east, and pi is north.
    def get_position(self, date: datetime, lat: float, lng: float):
        lng_west_in_radians = lng * -1 * self.RAD
        lat_in_radians = lat * self.RAD
        days_since_epoch = self.__calculate_days(date)
        # The sun's equatorial coordinates (specifically, right 
        # ascension and declination) for the given day (in days 
        # since epoch). These coordinates are relative to the 
        # celestial sphere.
        sun_coordinates = self.__calculate_sun_coordinates(days_since_epoch)
        # The hour angle is the angular difference between the local 
        # sidereal time and the sun's right ascension. It's essentially 
        # a measure of how far the sun is from its highest point in the 
        # sky (the meridian).
        hour_angle = self.__sidereal_time(days_since_epoch, lng_west_in_radians) - sun_coordinates["right_ascension"]
        return {
            "azimuth": self.__azimuth(hour_angle, lat_in_radians, sun_coordinates["declination"]),
            "altitude": self.__altitude(hour_angle, lat_in_radians, sun_coordinates["declination"])
        }
    
if __name__ == "__main__":
    # Example usage when run as a script:
    calculator = SunCalculator()
    date = input("Enter date and time (in format: 2025-02-11 11:25:18): ") # "2025-02-11 11:25:18"
    latitude = input("Enter latitude: ") # 51.21131496342009 = Brugge
    longitude = input("Enter longitude: ") # 3.2258847770102235 = Brugge
    output = calculator.get_position(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S"), float(latitude), float(longitude))
    print("On {0}, at latitude: {1} and logitude: {2}, the sun is at\n a) azimuth: {3} \n b) altitude: {4}".format(date, latitude, longitude, output["azimuth"], output["altitude"]))