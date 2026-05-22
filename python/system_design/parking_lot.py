"""Parking Lot System - OOP design with multiple levels and spot types"""

from enum import Enum


class VehicleSize(Enum):
    COMPACT = 1
    REGULAR = 2
    LARGE = 3


class Spot:
    """Parking spot"""

    def __init__(self, spot_id: int, level: int, size: VehicleSize):
        self.spot_id = spot_id
        self.level = level
        self.size = size
        self.occupied = False
        self.vehicle = None

    def park_vehicle(self, vehicle):
        """Park vehicle in spot"""
        if self.occupied or vehicle.size.value > self.size.value:
            return False
        self.occupied = True
        self.vehicle = vehicle
        return True

    def unpark_vehicle(self):
        """Remove vehicle from spot"""
        self.occupied = False
        self.vehicle = None
        return True

    def is_available(self, vehicle_size: VehicleSize) -> bool:
        """Check if spot can fit vehicle"""
        return not self.occupied and vehicle_size.value <= self.size.value


class Level:
    """Parking lot level"""

    def __init__(self, level_num: int, num_compact: int, num_regular: int, num_large: int):
        self.level_num = level_num
        self.spots = []
        self.available_compact = num_compact
        self.available_regular = num_regular
        self.available_large = num_large

        spot_id = 0
        for _ in range(num_compact):
            self.spots.append(Spot(spot_id, level_num, VehicleSize.COMPACT))
            spot_id += 1
        for _ in range(num_regular):
            self.spots.append(Spot(spot_id, level_num, VehicleSize.REGULAR))
            spot_id += 1
        for _ in range(num_large):
            self.spots.append(Spot(spot_id, level_num, VehicleSize.LARGE))
            spot_id += 1

    def find_available_spot(self, vehicle_size: VehicleSize):
        """Find first available spot for vehicle size"""
        for spot in self.spots:
            if spot.is_available(vehicle_size):
                return spot
        return None

    def park_vehicle(self, vehicle):
        """Park vehicle in level"""
        spot = self.find_available_spot(vehicle.size)
        if spot and spot.park_vehicle(vehicle):
            self._update_availability(-1, vehicle.size)
            return spot
        return None

    def unpark_vehicle(self, spot_id: int):
        """Unpark vehicle from spot"""
        spot = self.spots[spot_id]
        if spot.occupied:
            size = spot.vehicle.size
            spot.unpark_vehicle()
            self._update_availability(1, size)
            return True
        return False

        """_update_availability implementation.

        Time: O(n)
        Space: O(1)
        """
    def _update_availability(self, delta: int, size: VehicleSize):
        if size == VehicleSize.COMPACT:
            self.available_compact += delta
        elif size == VehicleSize.REGULAR:
            self.available_regular += delta
        elif size == VehicleSize.LARGE:
            self.available_large += delta

    def display_availability(self):
        """Display available spots"""
        print(f"Level {self.level_num}: Compact={self.available_compact}, Regular={self.available_regular}, Large={self.available_large}")


class Vehicle:
    """Vehicle to park"""

    def __init__(self, license_plate: str, size: VehicleSize):
        self.license_plate = license_plate
        self.size = size


class ParkingLot:
    """Parking lot with multiple levels"""

    def __init__(self, num_levels: int, num_compact: int, num_regular: int, num_large: int):
        self.levels = []
        for i in range(num_levels):
            self.levels.append(Level(i, num_compact, num_regular, num_large))
        self.parked_vehicles = {}  # license_plate -> (level, spot_id)

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        """Park vehicle in first available level"""
        for level in self.levels:
            spot = level.park_vehicle(vehicle)
            if spot:
                self.parked_vehicles[vehicle.license_plate] = (level.level_num, spot.spot_id)
                print(f"Parked {vehicle.license_plate} at Level {level.level_num}, Spot {spot.spot_id}")
                return True
        print(f"Cannot park {vehicle.license_plate} - no available spots")
        return False

    def unpark_vehicle(self, license_plate: str) -> bool:
        """Unpark vehicle"""
        if license_plate not in self.parked_vehicles:
            print(f"{license_plate} not found")
            return False

        level_num, spot_id = self.parked_vehicles[license_plate]
        level = self.levels[level_num]
        if level.unpark_vehicle(spot_id):
            del self.parked_vehicles[license_plate]
            print(f"Unparked {license_plate} from Level {level_num}, Spot {spot_id}")
            return True
        return False

    def display_availability(self):
        """Display availability for all levels"""
        for level in self.levels:
            level.display_availability()


if __name__ == "__main__":
    lot = ParkingLot(3, 10, 20, 5)

    v1 = Vehicle("ABC123", VehicleSize.COMPACT)
    v2 = Vehicle("XYZ789", VehicleSize.REGULAR)
    v3 = Vehicle("DEF456", VehicleSize.LARGE)

    lot.park_vehicle(v1)
    lot.park_vehicle(v2)
    lot.park_vehicle(v3)
    lot.display_availability()

    lot.unpark_vehicle("ABC123")
    lot.display_availability()