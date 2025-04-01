import pandas as pd
import numpy as np


class MockDataGenerator:
    def __init__(self, filename: str, num_entries: int = 100, stallions: list = None):
        """
        Initializes the MockDataGenerator.

        :param filename: Name of the CSV file to save the data.
        :param num_entries: Number of rows (data points) to generate.
        :param stallions: List of stallion names to randomly choose from. Defaults to ['A', 'B', 'C'].
        """
        self.filename = filename
        self.num_entries = num_entries
        self.stallions = stallions if stallions is not None else ['A', 'B', 'C']
    
    def generate_data(self) -> pd.DataFrame:
        """
        Generates a pandas DataFrame with mock data.

        :return: DataFrame with columns 'time_idx', 'target', and 'stallion'
        """
        # Create a sequential time index
        time_idx = np.arange(self.num_entries)
        
        # Generate random target values (for example, between 0 and 100)
        target = np.random.uniform(0, 100, self.num_entries)
        
        # Randomly assign a stallion from the list for each entry
        stallion = np.random.choice(self.stallions, self.num_entries)
        
        # Create and return the DataFrame
        df = pd.DataFrame({
            'time_idx': time_idx,
            'target': target,
            'stallion': stallion
        })
        return df

    def save_to_csv(self):
        """
        Generates the data and saves it to a CSV file.
        """
        df = self.generate_data()
        df.to_csv(self.filename, index=False)
        print(f"Data successfully saved to '{self.filename}'")


