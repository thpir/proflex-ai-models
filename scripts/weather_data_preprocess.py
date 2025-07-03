
import sys
import os

# Get the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the current directory to sys.path
sys.path.insert(0, current_dir)

import pandas as pd
import sun_calculator as sc

class WeatherDataPreprocess:
    def preprocessWeatherData(self, lat: float, lng: float, file_name: str) -> pd.DataFrame:
        # Import the data and preprocess it
        df = self.__importData(file_name)
        if df is None:
            return None
        df = self.__interpolateData(df)
        
        df = self.__addLocationToDf(df, lat, lng)
        df = self.__calculateSunPosition(df)

        # Export DataFrame to CSV
        df.to_csv(f'./data/processed/processed_{file_name}', index=False)

        # Check if the script is run standalone or imported
        if __name__ == "__main__":
            print(f"Data exported as {file_name}. No DataFrame returned.")
            return None
        else:
            return df
        
    def __importData(self, name: str) -> pd.DataFrame:
        try:
            # Importing the CSV file
            df = pd.read_csv(f'./data/raw/{name}')
            # Selecting only the relevant columns
            df_weather = df[['datetime', 'temp', 'humidity', 'cloudcover', 'solarenergy', 'uvindex']].copy()
            return df_weather
        except FileNotFoundError:
            print(f"File not found at data/raw/{name}. Please check the path and try again.")

    def __interpolateData(self, df: pd.DataFrame) -> pd.DataFrame:
        # Converting the 'datetime' column to a pandas datetime object
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.drop_duplicates(subset='datetime', keep='first', inplace=True)
        # Setting 'datetime' as the index
        df.set_index('datetime', inplace=True)
        # Resampling the data to 15-minute intervals and interpolating the values
        resampled_data = df.resample('15min').interpolate()
        # Resetting the index to make 'datetime' a column again
        resampled_data.reset_index(inplace=True)
        return resampled_data
    
    def __addLocationToDf(self, df: pd.DataFrame, lat: float, lng: float) -> pd.DataFrame:
        # Add 'latitude' and 'longitude' columns
        df.loc[:, 'latitude'] = lat
        df.loc[:, 'longitude'] = lng
        return df
    
    def __calculateSunPosition(self, df: pd.DataFrame) -> pd.DataFrame:
        # using the sun calculator to calculate the sun position (azimuth and elevation) for each row
        calculator = sc.SunCalculator()
        df['solar_azimuth'] = df.apply(lambda row: calculator.get_position(date=row['datetime'], lat=row['latitude'], lng=row['longitude'])['azimuth'], axis=1)
        df['solar_elevation'] = df.apply(lambda row: calculator.get_position(date=row['datetime'], lat=row['latitude'], lng=row['longitude'])['altitude'], axis=1)
        return df

# Example usage when run as a script
if __name__ == "__main__":
    processor = WeatherDataPreprocess()
    file_name = input("Enter name of CSV file (stored in the data/raw folder): ")
    latitude = input("Enter the latitude of the location: ")
    longitude = input("Enter the longitude of the location: ")
    processor.preprocessWeatherData(latitude, longitude, file_name)
