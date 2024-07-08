class PlantInfo:
    def __init__(self, name, start_year, state, city, utility,
                 capacity, dataset_year):
        self.name = name
        self.start_year = start_year
        self.dataset_year = dataset_year
        self.state = state
        self.city = city
        self.capacity = capacity
        self.lat = None
        self.lng = None

    def get_year(self):
        return self.start_year

    def get_state(self):
        return self.state

    def get_city(self):
        return self.city

    def update_lat_lng(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def get_lat(self):
        return self.lat

    def get_lng(self):
        return self.lng

    def get_capacity_mw(self):
        return self.capacity / 1000

    def get_capacity_kw(self):
        return self.capacity

    def __str__(self):
        s = ("Name: {}, Year: {}, State: {}, City: {}, Capacity: {}, "
             "DS Year: {}, Lat: {}, Lng: {}"
             .format(self.name, self.start_year,
                     self.state, self.city, self.capacity,
                     self.dataset_year, self.lat, self.lng))
        return s


def load_plant_array(df):
    output_arr = []
    cnt = 0
    added = 0
    print("df size = ", len(df))
    for index, row in df.iterrows():
        name = row['Project Name']
        utility = row['Utility']
        c = row['City']
        s = row['State']
        cap = row['System Size (kW-AC)']
        year = row['Year of Interconnection']
        dataset_year = row['Year']

        data_obj = PlantInfo(name, year, s, c, utility, cap, dataset_year)

        output_arr.append(data_obj)

    cnt += 1
    print("added ", added)
    added = 0
    return output_arr


def match_lat_lngs(plant_arr, ll_df):
    for v in plant_arr:
        state = v.get_state()
        city = v.get_city()
        # print("2 state <{}> and city <{}>".format(state, city))
        val = ll_df.loc[(ll_df['State'] == state) & (ll_df['City'] == city)]
        if not val.empty:
            v.update_lat_lng(val.iloc[0]['lat'], val.iloc[0]['lng'])
    return plant_arr