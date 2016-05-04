from alpg.households import HouseholdSingleWorker

class LoadProfile():

    def __init__(self):
        pass

    def get_generation_profile(self, start_date=None, end_date=None):
        h = HouseholdSingleWorker()
        h.simulate()
        h.scaleProfile()
        data = h.Consumption['Total']
        hourly = []
        for i in range(0, len(data), 60):
            hourly.append(sum(data[i:i+60]))

        if start_date is None and end_date is None:
            return hourly
        elif start_date is None:
            end_day_in_year = end_date.timetuple().tm_yday
            return hourly[:end_day_in_year * 24]
        elif end_date is None:
            start_day_in_year = start_date.timetuple().tm_yday
            return hourly[start_day_in_year * 24:]
        else:
            start_day_in_year = start_date.timetuple().tm_yday
            end_day_in_year = end_date.timetuple().tm_yday
            return hourly[start_day_in_year * 24:end_day_in_year * 24]