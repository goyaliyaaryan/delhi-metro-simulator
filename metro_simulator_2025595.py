def load_data():
    f = open("metro_data.txt", "r")
    lines = f.readlines()
    f.close()

    data = []
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        if line != "":
            parts = line.split(",")
            entry = {
                "line": parts[0],
                "station": parts[1],
                "next": parts[2],
                "time": int(parts[3]),
                "interchange": parts[4]
            }
            data.append(entry)
        i = i + 1

    return data

# TIME HELPERS 
def minutes(time):
    hour, min = time.split(":")
    return int(hour) * 60 + int(min)

def change_time(min):
    hour = min // 60
    minute = min % 60
    hour_str = "0" + str(hour) if hour < 10 else str(hour)
    min_str = "0" + str(minute) if minute < 10 else str(minute)
    return hour_str + ":" + min_str

def validate_time(time_str):
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            return False
        hour = int(parts[0])
        min = int(parts[1])
        if hour < 0 or hour > 23 or min < 0 or min > 59:
            return False
        return True
    except:
        return False

def frequency(time_str):
    mins = minutes(time_str)
    hr = mins // 60
    return 4 if (hr >= 8 and hr < 10) or (hr >= 17 and hr < 19) else 8

def next_train(time_str):
    mins = minutes(time_str)
    if mins < minutes("06:00") or mins >= minutes("23:30"):
        return None
    freq = frequency(time_str)
    start = minutes("06:00")
    now = minutes(time_str)
    if now <= start:
        return "06:00"
    diff = now - start
    rem = diff % freq
    nxt = now if rem == 0 else now + (freq - rem)
    return change_time(nxt)

# BASIC SEARCH HELPERS 
def find_real_station_name(data, name):
    name_low = name.lower()
    i = 0
    while i < len(data):
        if data[i]["station"].lower() == name_low:
            return data[i]["station"]
        i = i + 1
    return None

def get_lines_station(data, station):
    lines = []
    i = 0
    while i < len(data):
        a = data[i]
        if a["station"] == station and a["line"] not in lines:
            lines.append(a["line"])
        i = i + 1
    return lines

def get_travel_time(data, s1, s2, line):
    i = 0
    while i < len(data):
        a = data[i]
        if a["line"] == line:
            if (a["station"] == s1 and a["next"] == s2) or (a["station"] == s2 and a["next"] == s1):
                return a["time"]
        i = i + 1
    return 0

def calculate_fare(total_stations):
    if total_stations <= 3:
        return 10
    elif total_stations <= 7:
        return 20
    elif total_stations <= 11:
        return 30
    elif total_stations <= 15:
        return 40
    elif total_stations <= 20:
        return 50
    else:
        return 60

def get_all_lines(data):
    lines = []
    i = 0
    while i < len(data):
        ln = data[i]["line"]
        if ln not in lines:
            lines.append(ln)
        i = i + 1
    return lines

def get_terminals_for_line(data, line):
    stations = []
    nexts = []
    i = 0
    while i < len(data):
        temp_data = data[i]
        if temp_data["line"].lower() == line.lower():
            stations.append(temp_data["station"])
            if temp_data["next"] != "End":
                nexts.append(temp_data["next"])
        i = i + 1
    
    start_terminal = None
    j = 0
    while j < len(stations):
        s = stations[j]
        found_in_nexts = False
        k = 0
        while k < len(nexts):
            if nexts[k] == s:
                found_in_nexts = True
                break
            k = k + 1
        if not found_in_nexts:
            start_terminal = s
            break
        j = j + 1
    
    end_terminal = None
    k = 0
    while k < len(data):
        e = data[k]
        if e["line"].lower() == line.lower() and e["next"] == "End":
            end_terminal = e["station"]
            break
        k = k + 1
    
    return start_terminal, end_terminal

def time_from_start_terminal(data, line, start_terminal, station):
    total = 0
    cur = start_terminal
    while cur != station:
        found = False
        i = 0
        while i < len(data):
            e = data[i]
            if e["line"].lower() == line.lower() and e["station"] == cur:
                next_station = e["next"]
                travel = e["time"]
                total = total + travel
                cur = next_station
                found = True
                break
            i = i + 1
        if not found or cur == "End":
            break
    return total

def time_from_end_terminal(data, line, end_terminal, station):
    total = 0
    cur = end_terminal
    while cur != station:
        found = False
        i = 0
        while i < len(data):
            e = data[i]
            if e["line"].lower() == line.lower() and e["next"] == cur:
                prev_station = e["station"]
                travel = e["time"]
                total = total + travel
                cur = prev_station
                found = True
                break
            i = i + 1
        if not found:
            break
    return total

def station_on_line(data, line, station):
    i = 0
    while i < len(data):
        a = data[i]
        if a["line"].lower() == line.lower() and a["station"].lower() == station.lower():
            return True
        i = i + 1
    return False


# ROUTE FINDING 
def simple_route_same_line(data, line, start, end):
    route = []
    cur = start
    
    # Forward direction
    while True:
        route.append(cur)
        nxt = None
        i = 0
        while i < len(data):
            if data[i]["line"] == line and data[i]["station"] == cur:
                nxt = data[i]["next"]
                break
            i = i + 1
        if nxt is None or nxt == "End":
            break
        cur = nxt

    i = 0
    while i < len(route):
        if route[i] == end:
            return route[0:i+1]
        i = i + 1

    # Backward direction
    route = []
    cur = start
    while True:
        route.append(cur)
        prev = None
        i = 0
        while i < len(data):
            if data[i]["line"] == line and data[i]["next"] == cur:
                prev = data[i]["station"]
                break
            i = i + 1
        if prev is None:
            break
        cur = prev

    i = 0
    while i < len(route):
        if route[i] == end:
            return route[0:i+1]
        i = i + 1

    return []

def find_interchange_station(data, line1, line2):
    i = 0
    while i < len(data):
        station_name = data[i]["station"]
        lines_of_st = get_lines_station(data, station_name)
        if line1 in lines_of_st and line2 in lines_of_st:
            return station_name
        i = i + 1
    return None

def route_travel_time(data, line, route):
    total = 0
    i = 0
    while i < len(route) - 1:
        total = total + get_travel_time(data, route[i], route[i + 1], line)
        i = i + 1
    return total

# TWO INTERCHANGE ROUTE 
def find_two_interchange_route(data, source, destination, source_line, destination_line):
    all_lines = get_all_lines(data)
    best_time = None
    best_result = None
    
    i = 0
    while i < len(all_lines):
        middle_line = all_lines[i]
        if middle_line == source_line or middle_line == destination_line:
            i = i + 1
            continue
        
        # Find common stations between source_line and middle_line
        common_line = []
        j = 0
        while j < len(data):
            station = data[j]["station"]
            lines_here = get_lines_station(data, station)
            if source_line in lines_here and middle_line in lines_here:
                if station not in common_line:
                    common_line.append(station)
            j = j + 1
        
        # Find common stations between middle_line and destination_line
        mid_dst_commons = []
        j = 0
        while j < len(data):
            station = data[j]["station"]
            lines_here = get_lines_station(data, station)
            if middle_line in lines_here and destination_line in lines_here:
                if station not in mid_dst_commons:
                    mid_dst_commons.append(station)
            j = j + 1
        
        # Try all combinations
        p = 0
        while p < len(common_line):
            inter1 = common_line[p]
            q = 0
            while q < len(mid_dst_commons):
                inter2 = mid_dst_commons[q]
                
                route1 = simple_route_same_line(data, source_line, source, inter1)
                route2 = simple_route_same_line(data, middle_line, inter1, inter2)
                route3 = simple_route_same_line(data, destination_line, inter2, destination)
                
                if route1 and route2 and route3:
                    total_time = route_travel_time(data, source_line, route1) + route_travel_time(data, middle_line, route2) + route_travel_time(data, destination_line, route3)
                    
                    if best_time is None or total_time < best_time:
                        best_time = total_time
                        best_result = (middle_line, inter1, inter2, route1, route2, route3)
                
                q = q + 1
            p = p + 1
        
        i = i + 1
    
    return best_result

def print_line():
    print("========================================")

def print_subline():
    print("----------------------------------------")

def next_metro_option(data):
    line = input("Enter line: ").strip()
    station_name = input("Enter station name: ").strip()
    current_time = input("Enter current time (HH:MM, 24-hr): ").strip()

    if not validate_time(current_time):
        print("Time entered is wrong. Please use HH:MM format (00:00 to 23:59).\n")
        return

    real_station = find_real_station_name(data, station_name)
    if real_station is None:
        print("Station not found in data.\n")
        return

    if not station_on_line(data, line, real_station):
        print("This station is not on that line.\n")
        return

    freq = frequency(current_time)
    if freq == -1:
        print("No service at this time (06:00-23:00 only).\n")
        return

    start_terminal, end_terminal = get_terminals_for_line(data, line)
    
    distance_start = time_from_start_terminal(data, line, start_terminal, real_station)
    distance_end = time_from_end_terminal(data, line, end_terminal, real_station)
    # Calculate first train times from both ends
    start_service_mins = minutes("06:00")
    base_start = start_service_mins + distance_start
    base_end = start_service_mins + distance_end
    now = minutes(current_time)
    # Find first train times after 'now'
    if now <= base_start:
        first_start = base_start
    else:
        diff1 = now - base_start
        rem1 = diff1 % freq
        first_start = now if rem1 == 0 else now + (freq - rem1)
    # For end direction
    if now <= base_end:
        first_end = base_end
    else:
        diff2 = now - base_end
        rem2 = diff2 % freq
        first_end = now if rem2 == 0 else now + (freq - rem2)
    # Generate next 6 trains in both directions
    start_times = []
    end_times = []
    end_of_service = minutes("23:00")

    tm = first_start
    for _ in range(6):
        if tm >= end_of_service:
            break
        start_times.append(change_time(tm))
        tm = tm + freq
    tm = first_end
    for _ in range(6):
        if tm >= end_of_service:
            break
        end_times.append(change_time(tm))
        tm = tm + freq

    print()
    print("Next trains at", real_station, "on", line, "(Current time:", current_time + "):")
    print("-- Direction: From Line Start -> End")
    if len(start_times) == 0:
        print("No more trains in this direction today.")
    else:
        i = 0
        line_str = ""
        while i < len(start_times):
            if i == 0:
                line_str = start_times[i]
            else:
                line_str = line_str + ", " + start_times[i]
            i = i + 1
        print(line_str)

    print("-- Direction: From Line End -> Start")
    if len(end_times) == 0:
        print("No more trains in this direction today.")
    else:
        i = 0
        line_str = ""
        while i < len(end_times):
            if i == 0:
                line_str = end_times[i]
            else:
                line_str = line_str + ", " + end_times[i]
            i = i + 1
        print(line_str)

    print()
    
# PRINTING JOURNEY DETAILS
def print_journey(data, line_num, line, route, departure, start_station=None):
    print("\nLINE " + str(line_num) + ":", line)
    print_subline()
    if start_station:
        print("Departure from", start_station, "at", departure)
    print("\nArrival times:")
    
    print(route[0], (25 - len(route[0])) * " ", "->", departure)

    current = minutes(departure)
    total_journey_travel = 0
    i = 0
    while i < len(route) - 1:
        seg_time = get_travel_time(data, route[i], route[i + 1], line)
        current = current + seg_time
        total_journey_travel = total_journey_travel + seg_time
        print(route[i + 1], (25 - len(route[i + 1])) * " ", "->", change_time(current))
        i = i + 1
    
    return current, total_journey_travel

# JOURNEY PLANNING 
def plan_journey_option(data):
    source_input = input("Enter source station: ").strip()
    destination_in = input("Enter destination station: ").strip()
    time_input = input("Enter start time (HH:MM, 24-hr): ").strip()
    

    if not validate_time(time_input):
        print("Time entered is wrong. Please use HH:MM format (00:00 to 23:59).\n")
        return
    
    source = find_real_station_name(data, source_input)
    destination = find_real_station_name(data, destination_in)

    if source is None or destination is None:
        print("Source or destination station not found.\n")
        return

    freq = frequency(time_input)
    if freq == -1:
        print("No service at this time (06:00-23:00 only).\n")
        return

    source_lines = get_lines_station(data, source)
    final_line = get_lines_station(data, destination)

    if len(source_lines) == 0 or len(final_line) == 0:
        print("No lines for these stations.\n")
        return

    if source == destination:
        print("\nYou are already at", source, "- no journey needed.\n")
        return
        
    best_route_info = None
    best_time = None

    # try all combinations
    # goes through through all lines passing through source and destination
    for start_line in source_lines:
        for end_line in final_line:
            
            # CASE 1: SAME LINE
            if start_line == end_line:
                route = simple_route_same_line(data, start_line, source, destination)
                if route:
                    t_time = route_travel_time(data, start_line, route)
                    # Update best route if this is the first one found OR it is faster
                    if best_time is None or t_time < best_time:
                        best_time = t_time
                        best_route_info = ("same_line", start_line, route, None, None)

            else:
                # CASE 2: ONE INTERCHANGE
                inter1 = find_interchange_station(data, start_line, end_line)
                if inter1:
                    r1 = simple_route_same_line(data, start_line, source, inter1)
                    r2 = simple_route_same_line(data, end_line, inter1, destination)
                    
                    if r1 and r2:
                        # Time = Travel on Line 1 + Travel on Line 2
                        t_time = route_travel_time(data, start_line, r1) + route_travel_time(data, end_line, r2)
                        
                        if best_time is None or t_time < best_time:
                            best_time = t_time
                            best_route_info = ("one_interchange", start_line, end_line, inter1, r1, r2)
                
                # CASE 3: TWO INTERCHANGES 
                # Only check this if we haven't found a direct or single-interchange route yet, 
                # OR if you want to be exhaustive to find the absolute fastest path
                result = find_two_interchange_route(data, source, destination, start_line, end_line)
                if result:
                    middle_line, int1, int2, r1, r2, r3 = result
                    
                    # Time = Line 1 + Line 2 + Line 3
                    t_time = (route_travel_time(data, start_line, r1) + 
                              route_travel_time(data, middle_line, r2) + 
                              route_travel_time(data, end_line, r3))
                    
                    if best_time is None or t_time < best_time:
                        best_time = t_time
                        best_route_info = ("two_interchanges", start_line, middle_line, end_line, int1, int2, r1, r2, r3)
    if best_route_info is None:
        print("No valid route found.\n")
        return

    route_type = best_route_info[0]
    
    print()
    print_line()
    print("JOURNEY PLAN:", source, "->", destination)
    print_line()
    print("Start time:", time_input)
    print_subline()

    depart = next_train(time_input)
    if depart is None:
        print("No service for given time.\n")
        return

    current = minutes(depart)
    total_travel = 0
    total_stations = 0

    if route_type == "same_line":
        _, line, route, _, _ = best_route_info
        current, journey_travel = print_journey(data, 1, line, route, depart, source)
        total_travel = journey_travel
        total_stations = len(route)

    elif route_type == "one_interchange":
        _, line1, line2, inter, route1, route2 = best_route_info
        
        print("\nJourney Plan (1 interchange at", inter + "):")
        print_subline()
        
        current, journey1 = print_journey(data, 1, line1, route1, depart, source)
        total_travel = journey1
        
        print("\n---------- INTERCHANGE ----------")
        print("Arrive at", inter, "at", change_time(current))
        current = current + 5
        print("Interchange time: + 5 minutes")
        
        new_depart = next_train(change_time(current))
        if new_depart is None:
            print("No train available.\n")
            return
        current = minutes(new_depart)
        print("Next train on", line2, "at", new_depart)
        print_subline()
        
        current, journey2 = print_journey(data, 2, line2, route2, new_depart)
        total_travel = total_travel + journey2
        total_stations = len(route1) + len(route2) - 1

    else:
        _, line1, line2, line3, inter1, inter2, route1, route2, route3 = best_route_info
        
        print("\nJourney Plan (2 interchanges at", inter1, "and", inter2 + "):")
        print_subline()
        
        current, journey1 = print_journey(data, 1, line1, route1, depart, source)
        total_travel = journey1
        
        print("\n---------- INTERCHANGE 1 ----------")
        print("Arrive at", inter1, "at", change_time(current))
        current = current + 5
        print("Interchange time: + 5 minutes")
        new_depart_1 = next_train(change_time(current))
        if new_depart_1 is None:
            print("No train available.\n")
            return
        current = minutes(new_depart_1)
        print("Next train on", line2, "at", new_depart_1)
        print_subline()
        
        current, journey2 = print_journey(data, 2, line2, route2, new_depart_1)
        total_travel = total_travel + journey2
        
        print("\n---------- INTERCHANGE 2 ----------")
        print("Arrive at", inter2, "at", change_time(current))
        current = current + 5
        print("Interchange time: + 5 minutes")
        new_depart_2 = next_train(change_time(current))
        if new_depart_2 is None:
            print("No train available.\n")
            return
        current = minutes(new_depart_2)
        print("Next train on", line3, "at", new_depart_2)
        print_subline()
        
        current, journey3 = print_journey(data, 3, line3, route3, new_depart_2)
        total_travel = total_travel + journey3
        total_stations = len(route1) + len(route2) + len(route3) - 2

    fare = calculate_fare(total_stations)
    print()
    print_line()
    print("FINAL SUMMARY")
    print_subline()
    print("Start time:         ", time_input)
    print("Final arrival:      ", change_time(current))
    print("Total journey time: ", total_travel, "minutes")
    print("Total stations:     ", total_stations)
    print("Approx fare:        ", "Rs", fare)
    print_line()
    print()
    
# MAIN PROGRAM 
def main():
    print("Loading metro data from metro_data.txt ...")
    data = load_data()
    print("Data loaded.\n")

    while True:
        print("----- Delhi Metro Simulator -----")
        print("All lines available. Use Branch2 format (ex: Blue2) for branches")
        print("1. Next metro at a station")
        print("2. Plan a journey")
        print("3. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            next_metro_option(data)
        elif choice == "2":
            plan_journey_option(data)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")

main()
