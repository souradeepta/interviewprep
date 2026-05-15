import java.util.*;

interface Observer { void update(Button b); }

class Button {
    List<Observer> observers = new ArrayList<>();
    boolean pressed;
    void attach(Observer o) { observers.add(o); }
    void detach(Observer o) { observers.remove(o); }
    void notify_obs() { for(Observer o : observers) o.update(this); }
    void press() { pressed=true; notify_obs(); }
    void release() { pressed=false; notify_obs(); }
}

class LogObserver implements Observer {
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public void update(Button b) { System.out.println("Button: " + (b.pressed ? "pressed" : "released")); }
}

/**
 * ObserverPattern - [Brief description]
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

public class ObserverPattern {
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        Button btn = new Button();
        btn.attach(new LogObserver());
        btn.press();
        btn.release();
    }
}
