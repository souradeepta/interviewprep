import java.util.*;

/**
 * ParkingLot - [Brief description]
 *
 * <p>OVERVIEW:
 * [Detailed explanation of what this class does]
 *
 * <p>COMPLEXITY:
 * <ul>
 *   <li>Time: [See method documentation]</li>
 *   <li>Space: O(n) where n is [the element count]</li>
 * </ul>
 *
 * <p>USAGE:
 * [How to use this class, with example]
 *
 * @author Interview Preparation
 * @since 1.0
 */

public class ParkingLot {
    enum VehicleSize { COMPACT(1), REGULAR(2), LARGE(3);
        int val; VehicleSize(int v) { val = v; }
    }
    
    static class Vehicle { String plate; VehicleSize size; Vehicle(String p, VehicleSize s) { plate=p; size=s; } }
    static class Spot { int id; VehicleSize size; Vehicle vehicle; boolean occupied;
        Spot(int i, VehicleSize s) { id=i; size=s; occupied=false; }
        boolean park(Vehicle v) { if(occupied || v.size.val > size.val) return false; occupied=true; vehicle=v; return true; }
        void unpark() { occupied=false; vehicle=null; }
    }
    
    List<Spot>[] levels; int available[];
    ParkingLot(int n, int c, int r, int l) {
        levels = new List[n]; available = new int[3];
        for(int i=0; i<n; i++) levels[i] = new ArrayList<>();
        int id=0;
        for(int i=0; i<c; i++) { levels[0].add(new Spot(id++, VehicleSize.COMPACT)); available[0]++; }
        for(int i=0; i<r; i++) { levels[0].add(new Spot(id++, VehicleSize.REGULAR)); available[1]++; }
        for(int i=0; i<l; i++) { levels[0].add(new Spot(id++, VehicleSize.LARGE)); available[2]++; }
    }
    
    boolean park(Vehicle v) {
        for(List<Spot> level : levels) {
            for(Spot s : level) {
                if(!s.occupied && s.park(v)) {
                    available[v.size.ordinal()]--;
                    return true;
                }
            }
        }
        return false;
    }
    
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        ParkingLot lot = new ParkingLot(2, 10, 20, 5);
        Vehicle v1 = new Vehicle("ABC123", VehicleSize.COMPACT);
        System.out.println("Parked v1: " + lot.park(v1));
    }
}
