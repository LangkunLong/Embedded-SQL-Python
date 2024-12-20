"""CSC343 Assignment 2

=== CSC343 Winter 2023 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC343 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Danny Heap, Marina Tawfik, and Jacqueline Smith

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Danny Heap and Jacqueline Smith

=== Module Description ===

This file contains the WasteWrangler class and some simple testing functions.
"""

import datetime as dt
import psycopg2 as pg
import psycopg2.extensions as pg_ext
import psycopg2.extras as pg_extras
from typing import Optional, TextIO


class WasteWrangler:
    """A class that can work with data conforming to the schema in
    waste_wrangler_schema.ddl.

    === Instance Attributes ===
    connection: connection to a PostgreSQL database of a waste management
    service.

    Representation invariants:
    - The database to which connection is established conforms to the schema
      in waste_wrangler_schema.ddl.
    """
    connection: Optional[pg_ext.connection]

    def __init__(self) -> None:
        """Initialize this WasteWrangler instance, with no database connection
        yet.
        """
        self.connection = None

    def connect(self, dbname: str, username: str, password: str) -> bool:
        """Establish a connection to the database <dbname> using the
        username <username> and password <password>, and assign it to the
        instance attribute <connection>. In addition, set the search path
        to waste_wrangler.

        Return True if the connection was made successfully, False otherwise.
        I.e., do NOT throw an error if making the connection fails.

        >>> ww = WasteWrangler()
        >>> ww.connect("csc343h-marinat", "marinat", "")
        True
        >>> # In this example, the connection cannot be made.
        >>> ww.connect("invalid", "nonsense", "incorrect")
        False
        """
        try:
            self.connection = pg.connect(
                dbname=dbname, user=username, password=password,
                options="-c search_path=waste_wrangler"
            )
            return True
        except pg.Error:
            return False

    def disconnect(self) -> bool:
        """Close this WasteWrangler's connection to the database.

        Return True if closing the connection was successful, False otherwise.
        I.e., do NOT throw an error if closing the connection failed.

        >>> ww = WasteWrangler()
        >>> ww.connect("csc343h-marinat", "marinat", "")
        True
        >>> ww.disconnect()
        True
        """
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
            return True
        except pg.Error:
            return False

    def schedule_trip(self, rid: int, time: dt.datetime) -> bool:
        """Schedule a truck and two employees to the route identified
        with <rid> at the given time stamp <time> to pick up an
        unknown volume of waste, and deliver it to the appropriate facility.

        The employees and truck selected for this trip must be available:
            * They can NOT be scheduled for a different trip from 30 minutes
              of the expected start until 30 minutes after the end time of this
              trip.
            * The truck can NOT be scheduled for maintenance on the same day.

        The end time of a trip can be computed by assuming that all trucks
        travel at an average of 5 kph.

        From the available trucks, pick a truck that can carry the same
        waste type as <rid> and give priority based on larger capacity and
        use the ascending order of ids to break ties.

        From the available employees, give preference based on hireDate
        (employees who have the most experience get priority), and order by
        ascending order of ids in case of ties, such that at least one
        employee can drive the truck type of the selected truck.

        Pick a facility that has the same waste type a <rid> and select the one
        with the lowest fID.

        Return True iff a trip has been scheduled successfully for the given
            route.
        This method should NOT throw an error i.e. if scheduling fails, the
        method should simply return False.

        No changes should be made to the database if scheduling the trip fails.

        Scheduling fails i.e., the method returns False, if any of the following
        is true:
            * If rid is an invalid route ID.
            * If no appropriate truck, drivers or facility can be found.
            * If a trip has already been scheduled for <rid> on the same day
              as <time> (that encompasses the exact same time as <time>).
            * If the trip can't be scheduled within working hours i.e., between
              8:00-16:00.

        While a realistic use case will provide a <time> in the near future, our
        tests could use any valid value for <time>.
        """
        try:
            # TODO: implement this method
            pass
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            # raise ex
            return False

    def schedule_trips(self, tid: int, date: dt.date) -> int:
        """Schedule the truck identified with <tid> for trips on <date> using
        the following approach:

            1. Find routes not already scheduled for <date>, for which <tid>
               is able to carry the waste type. Schedule these by ascending
               order of rIDs.

            2. Starting from 8 a.m., find the earliest available pair
               of drivers who are available all day. Give preference
               based on hireDate (employees who have the most
               experience get priority), and break ties by choosing
               the lower eID, such that at least one employee can
               drive the truck type of <tid>.

               The facility for the trip is the one with the lowest fID that can
               handle the waste type of the route.

               The volume for the scheduled trip should be null.

            3. Continue scheduling, making sure to leave 30 minutes between
               the end of one trip and the start of the next, using the
               assumption that <tid> will travel an average of 5 kph.
               Make sure that the last trip will not end after 4 p.m.

        Return the number of trips that were scheduled successfully.

        Your method should NOT raise an error.

        While a realistic use case will provide a <date> in the near future, our
        tests could use any valid value for <date>.
        """
        # TODO: implement this method

        cursor = self.connection.cursor()

        cursor.execute("drop view if exists allDriverTrips cascade;")
        cursor.execute("drop view if exists allDrivers cascade;")
        cursor.execute("drop view if exists allAvailableDrivers cascade;")
        cursor.execute("drop view if exists driverExperience cascade;")

        cursor.execute("select * \
                       from Truck natural join TruckType \
                       where Truck.tid = %s;", [tid]) #get all wastetype the given truck can carry 
        truck_wastetype = cursor.fetchall()
        #print("Trucktype relation: ", truck_wastetype)
        truck_type = truck_wastetype[0][0]
        #print("Trucktype: ", truck_type)

        #iterate over each wastetype that the truck can carry, find routes where there's no trips in given day of that wastetype 
        #allRoute should have all the Route IDs that do not have any trips involving the wastypes of our truck
        allRoutes = list()
        for row in range(len(truck_wastetype)):
            waste = truck_wastetype[row][3]
            #print(waste)
            cursor.execute("select distinct t1.rid \
                            from Trip natural join Route t1 \
                            where t1.rid not in (select t2.rid \
                                             from Trip natural join Route t2 \
                                             where date(trip.ttime) = %s and t2.wastetype = %s) \
                            and t1.wastetype = %s \
                            order by t1.rid asc;", (date.date(), waste, waste))
            if cursor.rowcount != 0:
                subRoute = cursor.fetchall()
                allRoutes.extend(subRoute)
        
        all_distinct_routes = list(dict.fromkeys(allRoutes))
        #print(all_distinct_routes)
        #no available routes 
        """
        if len(all_distinct_routes) == 0:
            return 0 
        """

        #Step2: Starting from 8 a.m., find the earliest available pair of drivers of whom at least one can drive the
        #given truck and both are available for the day. Break ties by choosing lower eIDs.

        #this creates a view called <allDriverTrips> that contains all the driver who are booked to a trip on a given date 
        cursor.execute(" create view allDriverTrips as \
                        (select distinct eid \
                         from Driver join Trip on Driver.eid = Trip.eid1 \
                         where date(trip.ttime) = %s) \
                         UNION \
                        (select distinct eid \
                         from Driver join Trip on Driver.eid = Trip.eid2 \
                         where date(trip.ttime) = %s);", [date.date(), date.date()])
        
        #obtain all the drivers who do not have a booked trip on that day, creates a view called <allDrivers>
        cursor.execute("create view allDrivers as \
                        select distinct(eid) \
                        from Driver;")

        #Keep all the drivers that do not have a trip booked: all_remaining_drivers = allDrivers - allDriverTrips
        #creates a view called all_remaining_drivers
        cursor.execute("create view allAvailableDrivers as \
                        (select * from allDrivers) \
                        EXCEPT \
                        (select * from allDriverTrips);")
        
        #from the available drivers, create a view consisting of their hiredate, eID, and the trucktype they can drive
        #ordered from descending order so we have the drivers hired longest at the top of the table, and break ties by choosing lower eid
        #<eID, hiredate, trucktype>
        cursor.execute("create view driverExperience as \
                       select allAvailableDrivers.eid, Employee.hiredate, Driver.trucktype \
                       from allAvailableDrivers natural join Driver natural join Employee \
                       order by Employee.hiredate asc, allAvailableDrivers.eid asc;")
        
        #create a self join, and since it is already ordered based on longest experience, we can select the first tuple where it satisfies:
        # eid1 != eid2 and one of eid1 or eid2 can drive required trucktype 
        cursor.execute("select t1.eid, t2.eid \
                        from driverExperience t1, driverExperience t2 \
                        where not t1.eid = t2.eid \
                        and (t1.trucktype = %s or t2.trucktype = %s);",[truck_type, truck_type])
        #no available drivers
       
        if cursor.rowcount == 0:
            return 0
        
        driver1, driver2 = cursor.fetchone()[0], cursor.fetchone()[1]

        #loop over the routes, and scheduling trips based on ascending rIDs. First trip assumes start at 8am, adds (route.length / 5km/hr)
        trips_scheduled = 0
        start_time = dt.datetime.combine(date, dt.time(8,0)) # 2023-05-03 08:00:00
        current_time = start_time
        end_time = dt.datetime.combine(date, dt.time(16,0))

        for route in range(len(all_distinct_routes)):
            if current_time < end_time:
                #print(all_distinct_routes[route])
                rid = all_distinct_routes[route][0]
                #print("rid:", rid)
                cursor.execute("select wastetype, length \
                                from Route \
                                where rID = %s;", [rid])
                
                #covnert to hour + minutes, update time, then insert into trips , then update trips_scheduled
                #ALSO NEED FID VALUE (get from wastype from route it )

                #obtain the length and wastetype of the route
                route_tuple = cursor.fetchone()
                route_waste = route_tuple[0]
                route_length = route_tuple[1] 
                

                #get the lowest fid that can collect the waste of the route
                cursor.execute("select fid \
                                from Facility \
                                where wastetype = %s \
                                order by fid asc;", [route_waste])
                fid_tuple = cursor.fetchone()
                fid = fid_tuple[0]

                #insert into trips relation: 
                cursor.execute("insert into trip values \
                                (%s, %s, %s, NULL, %s, %s, %s);", [rid, tid, current_time, driver1, driver2, fid])
                #print("inserted into trips: (%s, %s, %s, NULL, %s, %s, %s)",rid, tid, current_time, driver1, driver2, fid)
                
                #update time; update number of trips scheduled 
                current_time = current_time + dt.timedelta(hours=float(route_length/5)) #time it takes to finish the route
                current_time = current_time + dt.timedelta(hours=0.5) #time between trips 
                trips_scheduled = trips_scheduled + 1

            else:
                break

        cursor.execute("drop view if exists allDriverTrips cascade;")
        cursor.execute("drop view if exists allDrivers cascade;")
        cursor.execute("drop view if exists allAvailableDrivers cascade;")
        cursor.execute("drop view if exists driverExperience cascade;")

        #commit newly inserted 
        if trips_scheduled > 0:
            self.connection.commit()

        return trips_scheduled
    

    def update_technicians(self, qualifications_file: TextIO) -> int:
        """Given the open file <qualifications_file> that follows the format
        described on the handout, update the database to reflect that the
        recorded technicians can now work on the corresponding given truck type.

        For the purposes of this method, you may assume that no two employees
        in our database have the same name i.e., an employee can be uniquely
        identified using their name.

        Your method should NOT throw an error.
        Instead, only correct entries should be reflected in the database.
        Return the number of successful changes, which is the same as the number
        of valid entries.
        Invalid entries include:
            * Incorrect employee name.
            * Incorrect truck type.
            * The technician is already recorded to work on the corresponding
              truck type.
            * The employee is a driver.

        Hint: We have provided a helper _read_qualifications_file that you
            might find helpful for completing this method.
        """
        # TODO: implement this method
        employee_list = self._read_qualifications_file(qualifications_file)
        cursor = self.connection.cursor()
        employee_added = 0

        for employee in employee_list:
            employee_name = employee[0] + " " + employee[1]

            #check if employee name is correct and exists in employee relation
            cursor.execute("select eid \
                            from employee \
                            where name = %s;", [employee_name])
            if cursor.rowcount == 0: #doesn't have this employee
                continue
            
            #check if employee is a driver
            name = cursor.fetchone() 
            eid = name[0]
            cursor.execute("select * \
                            from driver \
                            where eid = %s;", [eid])
            if cursor.rowcount != 0: #employee exists in driver relation
                continue
            
            #check if trucktype is correct 
            truck_type = employee[2]
            cursor.execute("select * \
                            from trucktype \
                            where trucktype = %s;", [truck_type])
            if cursor.rowcount == 0: #incorrect trucktype
                continue

            #check if employee is already working on the given truck
            cursor.execute("select * \
                            from technician \
                            where eid = %s \
                            and trucktype = %s;", [eid, truck_type])
            if cursor.rowcount != 0: #returns non-empty row, means employee already working on given type
                continue

            cursor.execute("insert into technician values \
                            (%s,%s);", [eid, truck_type])
            employee_added = employee_added + 1

        if employee_added > 0:
            self.connection.commit()

        return employee_added
    """
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            # raise ex
            return 0
    """

    def workmate_sphere(self, eid: int) -> list[int]:
        """Return the workmate sphere of the driver identified by <eid>, as a
        list of eIDs.

        The workmate sphere of <eid> is:
            * Any employee who has been on a trip with <eid>.
            * Recursively, any employee who has been on a trip with an employee
              in <eid>'s workmate sphere is also in <eid>'s workmate sphere.

        The returned list should NOT include <eid> and should NOT include
        duplicates.

        The order of the returned ids does NOT matter.

        Your method should NOT return an error. If an error occurs, your method
        should simply return an empty list.
        """
        try:
            # TODO: implement this method
            pass
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            # raise ex
            return []

    def schedule_maintenance(self, date: dt.date) -> int:
        """For each truck whose most recent maintenance before <date> happened
        over 90 days before <date>, and for which there is no scheduled
        maintenance up to 10 days following date, schedule maintenance with
        a technician qualified to work on that truck in ascending order of tIDs.

        For example, if <date> is 2023-05-02, then you should consider trucks
        that had maintenance before 2023-02-01, and for which there is no
        scheduled maintenance from 2023-05-02 to 2023-05-12 inclusive.

        Choose the first day after <date> when there is a qualified technician
        available (not scheduled to maintain another truck that day) and the
        truck is not scheduled for a trip or maintenance on that day.

        If there is more than one technician available on a given day, choose
        the one with the lowest eID.

        Return the number of trucks that were successfully scheduled for
        maintenance.

        Your method should NOT throw an error.

        While a realistic use case will provide a <date> in the near future, our
        tests could use any valid value for <date>.
        """
        #find all trucks that last had maintenance before date - 90
        cutoff_date = date + dt.timedelta(days=-90)
        cursor = self.connection.cursor()

        cursor.execute("drop view if exists within_90_days cascade;")
        cursor.execute("drop view if exists not_within_90_days cascade;")

        #first find all trucks that had maintenance within 90 days, then later subtract this from maintenance to find all trucks
        #that did not have maintenance within 90 days
        cursor.execute("create view within_90_days as \
                        select t1.tid \
                        from truck t1 \
                        where exists (select t2.tid \
                                      from maintenance t2 \
                                      where t1.tid = t2.tid \
                                      and t2.mdate >= %s);", [cutoff_date])
        
        cursor.execute("create view not_within_90_days as \
                        (select tid from truck) \
                        EXCEPT \
                        (select tid from within_90_days);")
        
        cursor.execute("select tid \
                        from not_within_90_days \
                        order by tid asc;")
        trucks_need_maintenance = list()
        if cursor.rowcount != 0:
            trucks_need_maintenance = cursor.fetchall()
        
        latest_date = date + dt.timedelta(days=10)
        trucks_maintenanced = 0
        
        for truck in trucks_need_maintenance:

            tid = truck[0]
            cursor.execute("select trucktype \
                            from truck \
                            where tid = %s;", [tid])
            truck_tuple = cursor.fetchone()
            truck_type = truck_tuple[0]

            #see if there is a scheduled maintenance in the next 10 days
            cursor.execute("select * \
                            from maintenance \
                            where tid = %s \
                            and mdate between %s and %s;", [tid, date, latest_date])
            if cursor.rowcount != 0:
                continue

            #if we get here, it means that there is no upcoming scheduled maintenance
            maintenance_date = date + dt.timedelta(days=1)
            technician_found = False

            while(technician_found == False):
                cursor.execute("drop view if exists scheduled_technicians cascade;")
                cursor.execute("drop view if exists available_technicians cascade;")

                #create a view to find all booked technicians, then we subtract this from all technicians
                cursor.execute("create view scheduled_technicians as \
                                select distinct eid from maintenance \
                                where mdate = %s;", [maintenance_date])
            
                cursor.execute("create view available_technicians as \
                                (select distinct eid from technician) \
                                 except \
                                (select * from scheduled_technicians);")
            
                cursor.execute("select distinct available_technicians.eid  \
                                from available_technicians join technician on available_technicians.eid = technician.eid \
                                where trucktype = %s \
                                order by available_technicians.eid asc;", [truck_type])
                
                #if no available technicians available, see if there is availability next day
                if cursor.rowcount == 0:
                    maintenance_date = maintenance_date + dt.timedelta(days=1)
                    continue
                else:
                    technician_found = True

            #get the first tuple since it is sorted in ascending order already 
            technician_tuple = cursor.fetchone()
            technician_eid = technician_tuple[0]

            cursor.execute("insert into maintenance values \
                            (%s,%s,%s);", [tid, technician_eid, maintenance_date])
            print("inserted: (%s,%s,%s)",tid, technician_eid, maintenance_date)

            trucks_maintenanced = trucks_maintenanced + 1
        
        if trucks_maintenanced > 0:
            self.connection.commit()
        
        return trucks_maintenanced

        """
        try:
            # TODO: implement this method
            pass
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            # raise ex
            return 0
        """

    def reroute_waste(self, fid: int, date: dt.date) -> int:
        """Reroute the trips to <fid> on day <date> to another facility that
        takes the same type of waste. If there are many such facilities, pick
        the one with the smallest fID (that is not <fid>).

        Return the number of re-routed trips.

        Don't worry about too many trips arriving at the same time to the same
        facility. Each facility has ample receiving facility.

        Your method should NOT return an error. If an error occurs, your method
        should simply return 0 i.e., no trips have been re-routed.

        While a realistic use case will provide a <date> in the near future, our
        tests could use any valid value for <date>.

        Assume this happens before any of the trips have reached <fid>.
        """
        try:
            # TODO: implement this method
            pass
        except pg.Error as ex:
            # You may find it helpful to uncomment this line while debugging,
            # as it will show you all the details of the error that occurred:
            # raise ex
            return 0

    # =========================== Helper methods ============================= #

    @staticmethod
    def _read_qualifications_file(file: TextIO) -> list[list[str, str, str]]:
        """Helper for update_technicians. Accept an open file <file> that
        follows the format described on the A2 handout and return a list
        representing the information in the file, where each item in the list
        includes the following 3 elements in this order:
            * The first name of the technician.
            * The last name of the technician.
            * The truck type that the technician is currently qualified to work
              on.

        Pre-condition:
            <file> follows the format given on the A2 handout.
        """
        result = []
        employee_info = []
        for idx, line in enumerate(file):
            if idx % 2 == 0:
                info = line.strip().split(' ')[-2:]
                fname, lname = info
                employee_info.extend([fname, lname])
            else:
                employee_info.append(line.strip())
                result.append(employee_info)
                employee_info = []

        return result


def setup(dbname: str, username: str, password: str, file_path: str) -> None:
    """Set up the testing environment for the database <dbname> using the
    username <username> and password <password> by importing the schema file
    and the file containing the data at <file_path>.
    """
    connection, cursor, schema_file, data_file = None, None, None, None
    try:
        # Change this to connect to your own database
        connection = pg.connect(
            dbname=dbname, user=username, password=password,
            options="-c search_path=waste_wrangler"
        )
        cursor = connection.cursor()

        schema_file = open("./waste_wrangler_schema.sql", "r")
        cursor.execute(schema_file.read())

        data_file = open(file_path, "r")
        cursor.execute(data_file.read())

        connection.commit()
    except Exception as ex:
        connection.rollback()
        raise Exception(f"Couldn't set up environment for tests: \n{ex}")
    finally:
        if cursor and not cursor.closed:
            cursor.close()
        if connection and not connection.closed:
            connection.close()
        if schema_file:
            schema_file.close()
        if data_file:
            data_file.close()


def test_preliminary() -> None:
    """Test preliminary aspects of the A2 methods."""
    ww = WasteWrangler()
    qf = None
    try:
        # TODO: Change the values of the following variables to connect to your
        #  own database:
        dbname = 'csc343h-longlang'
        user = 'longlang'
        password = ''

        connected = ww.connect(dbname, user, password)

        # The following is an assert statement. It checks that the value for
        # connected is True. The message after the comma will be printed if
        # that is not the case (connected is False).
        # Use the same notation to thoroughly test the methods we have provided
        assert connected, f"[Connected] Expected True | Got {connected}."

        # TODO: Test one or more methods here, or better yet, make more testing
        #   functions, with each testing a different aspect of the code.

        # The following function will set up the testing environment by loading
        # the sample data we have provided into your database. You can create
        # more sample data files and use the same function to load them into
        # your database.
        # Note: make sure that the schema and data files are in the same
        # directory (folder) as your a2.py file.
        setup(dbname, user, password, './waste_wrangler_data.sql')

        # --------------------- Testing schedule_trip  ------------------------#

        # You will need to check that data in the Trip relation has been
        # changed accordingly. The following row would now be added:
        # (1, 1, '2023-05-04 08:00', null, 2, 1, 1)
        #scheduled_trip = ww.schedule_trip(1, dt.datetime(2023, 5, 4, 8, 0))
        #assert scheduled_trip, \
        #    f"[Schedule Trip] Expected True, Got {scheduled_trip}"

        # Can't schedule the same route of the same day.
        #scheduled_trip = ww.schedule_trip(1, dt.datetime(2023, 5, 4, 13, 0))
        #assert not scheduled_trip, \
        #    f"[Schedule Trip] Expected False, Got {scheduled_trip}"

        # -------------------- Testing schedule_trips  ------------------------#

        # All routes for truck tid are scheduled on that day
        scheduled_trips = ww.schedule_trips(1, dt.datetime(2023, 5, 3))
        assert scheduled_trips == 0, \
            f"[Schedule Trips] Expected 0, Got {scheduled_trips}"
        #print("Passed assert for scheduled trips\n")

        scheduled_trips = ww.schedule_trips(2, dt.datetime(2023,5, 4))
        assert scheduled_trips == 1, \
            f"[Schedule Trips] Expected 1, Got {scheduled_trips}"

        # ----------------- Testing update_technicians  -----------------------#

        # This uses the provided file. We recommend you make up your custom
        # file to thoroughly test your implementation.
        # You will need to check that data in the Technician relation has been
        # changed accordingly
        qf = open('qualifications.txt', 'r')
        updated_technicians = ww.update_technicians(qf)
        assert updated_technicians == 2, \
            f"[Update Technicians] Expected 2, Got {updated_technicians}"

        # ----------------- Testing workmate_sphere ---------------------------#

        # This employee doesn't exist in our instance
        #workmate_sphere = ww.workmate_sphere(2023)
        #assert len(workmate_sphere) == 0, \
        #    f"[Workmate Sphere] Expected [], Got {workmate_sphere}"

        #workmate_sphere = ww.workmate_sphere(3)
        # Use set for comparing the results of workmate_sphere since
        # order doesn't matter.
        # Notice that 2 is added to 1's work sphere because of the trip we
        # added earlier.
        #assert set(workmate_sphere) == {1, 2}, \
        #    f"[Workmate Sphere] Expected {{1, 2}}, Got {workmate_sphere}"

        # ----------------- Testing schedule_maintenance ----------------------#

        # You will need to check the data in the Maintenance relation
        scheduled_maintenance = ww.schedule_maintenance(dt.date(2023, 5, 5))
        assert scheduled_maintenance == 7, \
            f"[Schedule Maintenance] Expected 7, Got {scheduled_maintenance}"

        # ------------------ Testing reroute_waste  ---------------------------#

        # There is no trips to facility 1 on that day
        reroute_waste = ww.reroute_waste(1, dt.date(2023, 5, 10))
        assert reroute_waste == 0, \
            f"[Reroute Waste] Expected 0. Got {reroute_waste}"

        # You will need to check that data in the Trip relation has been
        # changed accordingly
        reroute_waste = ww.reroute_waste(1, dt.date(2023, 5, 3))
        assert reroute_waste == 1, \
            f"[Reroute Waste] Expected 1. Got {reroute_waste}"
    finally:
        if qf and not qf.closed:
            qf.close()
        ww.disconnect()


if __name__ == '__main__':
    # Un comment-out the next two lines if you would like to run the doctest
    # examples (see ">>>" in the methods connect and disconnect)
    # import doctest
    # doctest.testmod()

    # TODO: Put your testing code here, or call testing functions such as
    #   this one:
    test_preliminary()