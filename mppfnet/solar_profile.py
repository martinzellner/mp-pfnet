from pypvwatts import PVWatts


class SolarProfile():

    pv_watts = None
    api_key = "01afy2HxYxnSamxe7Z24eto4qXAs30YZLf5hmJZj" # PVWatts API Key
    system_capacity = 1 # default system capacity (in kW)
    module_type = 0 # default module type (see PVWatts API v5)
    format = 'json'
    losses = 0   # default losses (see PVWatts API v5)
    array_type = 1   # default array type (see PVWatts API v5)
    tilt = 30   # default tilt angle (degrees) (see PVWatts API v5)
    azimuth = 190   # default azimuth angle (degrees) (see PVWatts API v5)
    address = "San Diego" # default address (see PVWatts API v5)
    timeframe = 'hourly'

    def __init__(self):
        PVWatts.api_key = self.api_key

    def get_generation_profile(self, start_date=None, end_date=None):
        """
        :param start_date: inclusive that date
        :type start_date: :class:`datetime.datetime`
        :param end_date: exclusive that date
        :type end_date: :class:`datetime.datetime`

        :return: a array with the solar profile in hourly resolution for a standardized meteorological year.
        """
        result = PVWatts.request(system_capacity=self.system_capacity, module_type=self.module_type,
                        format=self.format, losses=self.losses, array_type=self.array_type, tilt=self.tilt,
                        azimuth=self.azimuth, timeframe=self.timeframe, address=self.address)
        data = result.raw
        if start_date is None and end_date is None:
            return data['outputs']['ac']
        elif start_date is None:
            end_day_in_year = end_date.timetuple().tm_yday
            return data['outputs']['ac'][:end_day_in_year * 24]
        elif end_date is None:
            start_day_in_year = start_date.timetuple().tm_yday
            return data['outputs']['ac'][start_day_in_year * 24:]
        else:
            start_day_in_year = start_date.timetuple().tm_yday
            end_day_in_year = end_date.timetuple().tm_yday
            return data['outputs']['ac'][start_day_in_year * 24:end_day_in_year * 24]


