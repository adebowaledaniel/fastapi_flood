from src import  flood_model

# base period
before_start = "2019-03-01"
before_end = "2019-03-10"
base_period = (before_start, before_end)

# Now set the same parameters for AFTER the flood.
after_start = "2019-03-10"
after_end = "2019-03-23"
flood_period = (after_start, after_end)

geometry = [[[31.59324397753903, -16.467062381836637],
          [31.59324397753903, -20.83766152348578],
          [38.163068196289025, -20.83766152348578],
          [38.163068196289025, -16.467062381836637]]]

difference_threshold = 1.25

dict_db = flood_model.db_creator(base_period, flood_period, geometry)
flood_added = flood_model.flood_estimation(dict_db=dict_db)
pop_added = flood_model.population_exposed(flood_added)
cropland_added = flood_model.cropland_exposed(pop_added)
urban_added = flood_model.urban_exposed(cropland_added)
