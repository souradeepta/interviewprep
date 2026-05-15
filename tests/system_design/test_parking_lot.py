import pytest
from python.system_design.parking_lot import (
    ParkingLot, Vehicle, VehicleSize, Spot, Level
)


class TestSpot:
    def test_park_vehicle(self):
        spot = Spot(1, 0, VehicleSize.REGULAR)
        vehicle = Vehicle("ABC123", VehicleSize.REGULAR)
        assert spot.park_vehicle(vehicle)
        assert spot.occupied

    def test_cannot_park_oversized(self):
        spot = Spot(1, 0, VehicleSize.COMPACT)
        vehicle = Vehicle("ABC123", VehicleSize.REGULAR)
        assert not spot.park_vehicle(vehicle)

    def test_unpark_vehicle(self):
        spot = Spot(1, 0, VehicleSize.REGULAR)
        vehicle = Vehicle("ABC123", VehicleSize.REGULAR)
        spot.park_vehicle(vehicle)
        spot.unpark_vehicle()
        assert not spot.occupied


class TestLevel:
    def test_find_available_spot(self):
        level = Level(0, 2, 2, 2)
        spot = level.find_available_spot(VehicleSize.COMPACT)
        assert spot is not None

    def test_no_spot_for_oversized(self):
        level = Level(0, 1, 0, 0)
        spot = level.find_available_spot(VehicleSize.REGULAR)
        assert spot is None  # No regular or large spots

    def test_park_vehicle_in_level(self):
        level = Level(0, 5, 5, 5)
        vehicle = Vehicle("ABC123", VehicleSize.COMPACT)
        spot = level.park_vehicle(vehicle)
        assert spot is not None
        assert vehicle.size.value <= spot.size.value


class TestParkingLot:
    def test_park_and_unpark(self):
        lot = ParkingLot(2, 5, 5, 5)
        v1 = Vehicle("ABC123", VehicleSize.COMPACT)
        v2 = Vehicle("XYZ789", VehicleSize.REGULAR)

        assert lot.park_vehicle(v1)
        assert lot.park_vehicle(v2)
        assert "ABC123" in lot.parked_vehicles
        assert "XYZ789" in lot.parked_vehicles

    def test_unpark_vehicle(self):
        lot = ParkingLot(2, 5, 5, 5)
        v1 = Vehicle("ABC123", VehicleSize.COMPACT)
        lot.park_vehicle(v1)
        assert lot.unpark_vehicle("ABC123")
        assert "ABC123" not in lot.parked_vehicles

    def test_unpark_nonexistent_vehicle(self):
        lot = ParkingLot(2, 5, 5, 5)
        assert not lot.unpark_vehicle("NONEXISTENT")

    def test_parking_full(self):
        lot = ParkingLot(1, 1, 1, 1)
        v1 = Vehicle("ABC123", VehicleSize.COMPACT)
        v2 = Vehicle("DEF456", VehicleSize.COMPACT)
        v3 = Vehicle("GHI789", VehicleSize.REGULAR)

        assert lot.park_vehicle(v1)
        assert lot.park_vehicle(v2)
        assert lot.park_vehicle(v3)
        # Should be 3 total spots, all filled
        assert not lot.park_vehicle(Vehicle("JKL012", VehicleSize.COMPACT))
