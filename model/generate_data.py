import model.mockGenerator as mG

generator = mG.MockDataGenerator(filename='mock_data.csv', num_entries=1000, stallions=['A', 'B', 'C'])
generator.save_to_csv()

