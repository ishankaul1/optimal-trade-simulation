#Implementations of various state quality function possibilities
#All state quality functions should take in a dict of {resource: value} pairs that represent how much of each resource
#one country has at the time. The state quality function should output a value representative of how 'good' the current
#state of that country is based on the resources

import math

#the most naive version possible, just for testing funzies
def state_quality_basic(resources: dict)-> float:
    return sum(resources.values())

def state_quality_realistic(resources: dict) -> float:
    if resources['Population'] <= 0:
        return 0 #can't have no people, worst country ever

    #the real essentials - people, water, food, shelter
    population_baseline_factor = -20 if resources['Population'] < 5 else 0

    #TODO: find a better way to normalize the minimum for these 3
    #idea: add factor 0.0000000001 to each ratio instead of the minimum
    water_per_person_factor = -50 if resources['Water'] == 0 else min((resources['Water'] / resources['Population']) * 10, 30)
    food_factor = -30 if resources['Food'] == 0 else min(math.log(resources['Food'] / resources['Population'], 3) * 8, 30)
    housing_factor = -20 if resources['Housing'] == 0 else min(math.log(resources['Housing'] / resources['Population'], 3) * 7,
                         30)  # terrible if low ratio, diminishing returns on too much

    #secondary - PotentialFossilEnergyUsable, PotentialRenewableEnergyUsable, Electronics
    potentialfossilenergyusable_factor = min(resources['PotentialFossilEnergyUsable'] * 2, 20)
    potentialrenewableenergyusable_factor = min(resources['PotentialRenewableEnergyUsable'] * 3, 25)
    electronics_factor = min(resources['Electronics'] * 5, 25)

    wastespread = resources['Population'] + resources['AvailableLand']
    #penalties for waste - PopulationWaste, FarmWaste, MetallicAlloysWaste, ElectronicsWaste, HousingWaste, FoodWaste, PotentialFossilEnergyWaste, PotentialRenewableEnergyWaste
    population_waste_factor = (resources['PopulationWaste'] / wastespread) * -4
    farm_waste_factor = (resources['FarmWaste'] / wastespread) * -3 #compostable :P
    metallic_waste_factor = (resources['MetallicAlloysWaste'] / wastespread) * -6
    electronics_waste_factor = (resources['MetallicAlloysWaste'] / wastespread) * -8
    housing_waste_factor = (resources['HousingWaste'] / wastespread) * -4
    food_waste_factor = (resources['FoodWaste'] / wastespread) * -1
    potentialfossilenergy_waste_factor = (resources['PotentialFossilEnergyUsableWaste'] / wastespread) * -8
    potentialrenewableenergy_waste_factor = (resources['PotentialRenewableEnergyUsableWaste'] / wastespread) * -6

    return sum([population_baseline_factor, water_per_person_factor, food_factor, housing_factor, potentialfossilenergyusable_factor, potentialrenewableenergyusable_factor, electronics_factor, population_waste_factor, farm_waste_factor, metallic_waste_factor, electronics_waste_factor, housing_waste_factor, food_waste_factor, potentialfossilenergy_waste_factor, potentialrenewableenergy_waste_factor])

